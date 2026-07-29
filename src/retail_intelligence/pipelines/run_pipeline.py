# Databricks notebook source
from __future__ import annotations

import os
import sys
from pathlib import Path, PurePosixPath


try:
    dbutils.widgets.text("catalog", "workspace")
    dbutils.widgets.text("schema", "retail_intelligence")
    catalog = dbutils.widgets.get("catalog")
    schema = dbutils.widgets.get("schema")
except NameError:
    catalog = os.getenv("DATABRICKS_CATALOG", "workspace")
    schema = os.getenv("DATABRICKS_SCHEMA", "retail_intelligence")


try:
    notebook_path = dbutils.notebook.entry_point.getDbutils().notebook().getContext().notebookPath().get()
    workspace_file = PurePosixPath(notebook_path)
    src_root = str(workspace_file.parents[2])
except NameError:
    current_file = Path(__file__).resolve()
    src_root = str(current_file.parents[2])

if src_root not in sys.path:
    sys.path.insert(0, src_root)
workspace_src_root = f"/Workspace{src_root}" if src_root.startswith("/Users/") else src_root
if workspace_src_root not in sys.path:
    sys.path.insert(0, workspace_src_root)

from retail_intelligence.data.synthetic import generate_all_sources
from retail_intelligence.genai.retention import generate_retention_actions
from retail_intelligence.ml.churn import FEATURE_COLUMNS, model_feature_rows, reason_codes, risk_category
from retail_intelligence.pipelines.customer360 import (
    build_customer_360,
    build_customer_activity,
    data_quality_summary,
)


def write_delta(table_name: str, rows: list[dict]) -> None:
    df = spark.createDataFrame(rows)
    df.write.mode("overwrite").option("overwriteSchema", "true").saveAsTable(f"{catalog}.{schema}.{table_name}")


def train_and_score_churn(customer_360: list[dict]) -> tuple[list[dict], list[dict]]:
    from pyspark.ml.classification import LogisticRegression
    from pyspark.ml.evaluation import BinaryClassificationEvaluator
    from pyspark.ml.feature import StandardScaler, VectorAssembler
    from pyspark.ml.functions import vector_to_array
    from pyspark.ml import Pipeline
    from pyspark.sql import functions as F

    features = model_feature_rows(customer_360)
    features_df = spark.createDataFrame(features)
    write_delta("silver_churn_features", features)

    assembler = VectorAssembler(inputCols=FEATURE_COLUMNS, outputCol="raw_features")
    scaler = StandardScaler(inputCol="raw_features", outputCol="features", withStd=True, withMean=True)
    lr = LogisticRegression(featuresCol="features", labelCol="label", maxIter=40, regParam=0.05)
    pipeline = Pipeline(stages=[assembler, scaler, lr])

    train_df, test_df = features_df.randomSplit([0.8, 0.2], seed=20260729)
    model = pipeline.fit(train_df)
    scored_df = model.transform(features_df)
    test_scored_df = model.transform(test_df)
    auc = BinaryClassificationEvaluator(labelCol="label", rawPredictionCol="rawPrediction").evaluate(test_scored_df)
    model_version = "spark-logistic-regression-v1"

    try:
        import mlflow
        import mlflow.spark

        mlflow.set_registry_uri("databricks-uc")
        mlflow.set_experiment(f"/Users/reza.khamooshi@gmail.com/retail-intelligence/churn")
        with mlflow.start_run(run_name="retail-intelligence-churn"):
            mlflow.log_param("model_type", "Spark ML LogisticRegression")
            mlflow.log_param("feature_count", len(FEATURE_COLUMNS))
            mlflow.log_metric("test_auc", float(auc))
            mlflow.spark.log_model(model, name="model")
    except Exception as exc:
        print(f"MLflow tracking skipped: {exc}")

    probability_df = scored_df.withColumn("churn_probability", vector_to_array(F.col("probability"))[1])
    scored_rows = probability_df.select("customer_id", "churn_probability").collect()
    by_customer_id = {row["customer_id"]: row for row in customer_360}
    prediction_rows = []
    for scored in scored_rows:
        customer_id = scored["customer_id"]
        probability = round(float(scored["churn_probability"]), 4)
        customer = by_customer_id[customer_id]
        prediction_rows.append(
            {
                "customer_id": customer_id,
                "churn_probability": probability,
                "risk_category": risk_category(probability),
                "reason_codes": reason_codes(customer),
                "model_version": model_version,
                "model_test_auc": round(float(auc), 4),
            }
        )

    prediction_df = spark.createDataFrame(prediction_rows)
    prediction_df = prediction_df.withColumn("scoring_timestamp", F.current_timestamp())
    prediction_df.write.mode("overwrite").option("overwriteSchema", "true").saveAsTable(
        f"{catalog}.{schema}.gold_customer_churn_predictions"
    )
    metrics = [
        {
            "metric_name": "model_test_auc",
            "metric_value": round(float(auc), 4),
            "model_version": model_version,
        },
        {
            "metric_name": "customers_scored",
            "metric_value": float(len(prediction_rows)),
            "model_version": model_version,
        },
    ]
    return prediction_rows, metrics


spark.sql(f"CREATE SCHEMA IF NOT EXISTS {catalog}.{schema}")
spark.sql(f"USE CATALOG {catalog}")
spark.sql(f"USE SCHEMA {schema}")

sources = generate_all_sources()
for table_name, rows in sources.items():
    write_delta(table_name, rows)

customer_360 = build_customer_360(sources)
write_delta("silver_customer_360", customer_360)
write_delta("silver_customer_activity", build_customer_activity(customer_360))
write_delta("silver_retention_documents", sources["bronze_retention_documents"])
write_delta("silver_data_quality_summary", data_quality_summary(sources))
predictions, model_metrics = train_and_score_churn(customer_360)
write_delta("gold_model_metrics", model_metrics)
retention_actions = generate_retention_actions(customer_360, predictions, sources["bronze_retention_documents"])
write_delta("gold_customer_retention_actions", retention_actions)

pipeline_status = [
    {
        "pipeline_name": "retail-intelligence-pipeline",
        "catalog": catalog,
        "schema": schema,
        "status": "success",
        "bronze_table_count": 6,
        "silver_table_count": 5,
        "gold_table_count": 3,
        "customers_scored": len(predictions),
        "retention_actions_generated": len(retention_actions),
    }
]
write_delta("pipeline_status", pipeline_status)

print(f"Wrote retail-intelligence Bronze and Silver tables to {catalog}.{schema}")
