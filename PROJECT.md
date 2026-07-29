# retail-intelligence

## Business Problem

Mid-sized retail leaders lack a governed, connected view of customer risk because customer, loyalty, transaction, support, campaign, and policy data live in fragmented systems. The prototype will show how Databricks can unify these sources into Customer 360, predict churn, generate grounded retention actions, and present the story in a Databricks App:

`Unified Data -> Predict Risk -> Generate Action -> Drive Outcome`

## Phase 1 Status

Status: Phase 6 complete. App validated, deployed, and running.

Completed locally:

- Loaded `.prompts/01-app-spec`.
- Confirmed Phase 1 scope only: discovery, documentation, proposed architecture, and implementation plan.
- Inspected the repository. It currently contains only `.gitignore`, `.prompts/01-app-spec`, and Git metadata.
- Confirmed Databricks CLI is installed: `Databricks CLI v1.9.0`.
- Listed configured CLI profiles:
  - `sa_profile` -> `https://dbc-dee9e2b6-b2e5.cloud.databricks.com` -> valid
  - `dapi4c7c9d109e5f0992b487482136a06ecf` -> `https://dbc-dee9e2b6-b2e5.cloud.databricks.com` -> valid
  - `sa_panel` -> `https://dbc-dee9e2b6-b2e5.cloud.databricks.com` -> not valid
- Verified the Databricks MCP server is available.
- Switched the Databricks MCP session to `sa_profile`.

Workspace inventory:

- Current user: `reza.khamooshi@gmail.com`.
- Home path: `/Workspace/Users/reza.khamooshi@gmail.com/`.
- Workspace host: `https://dbc-dee9e2b6-b2e5.cloud.databricks.com`.
- Catalogs: `system`, `samples`, `workspace`.
- Workspace schemas include: `default`, `information_schema`, `my_streaming_company`, `sa_architect_test`, `sa_interview`, `sa_interview_practice`, `sa_interview_retail`, `stream_flix`, `streaming_churn_demo`.
- Proposed schema `workspace.retail_intelligence` does not exist.
- Existing tables in `workspace.retail_intelligence`: none.
- SQL warehouses: `Serverless Starter Warehouse` (`ffdf1653dbc170db`), `STOPPED`, `2X-Small`, serverless PRO, 10 minute auto-stop.
- Best warehouse selected by MCP: `ffdf1653dbc170db`.
- Clusters: none.
- Spark versions and node types are available for classic compute if needed, but serverless should be preferred for this lightweight prototype.
- Jobs: one unrelated existing job, `[dev reza_khamooshi] streaming-churn-demo-dev-job` (`913596913709254`).
- Spark Declarative Pipelines: none.
- Apps: one unrelated existing app, `streaming-churn-demo-dev`, status `ComputeState.ACTIVE`.
- Model Serving endpoints: multiple READY foundation/model endpoints are available, including `databricks-gpt-5-6-sol`, `databricks-claude-sonnet-5`, `databricks-gpt-oss-120b`, `databricks-gte-large-en`, and `databricks-bge-large-en`.
- Vector Search endpoints: none.
- UC Lakehouse Federation connections: none.
- AppKit manifest plugins available: `analytics`, `serving`, `agents`, `jobs`, `files`, `genie`, `lakebase`, and required `server`.

## AI Dev Kit Skills Available

The installed Databricks AI Dev Kit skill surface includes:

- `databricks-agent-bricks`
- `databricks-ai-functions`
- `databricks-ai-runtime`
- `databricks-aibi-dashboards`
- `databricks-app-design`
- `databricks-apps`
- `databricks-apps-python`
- `databricks-core`
- `databricks-dabs`
- `databricks-data-discovery`
- `databricks-dbsql`
- `databricks-docs`
- `databricks-execution-compute`
- `databricks-genie`
- `databricks-iceberg`
- `databricks-jobs`
- `databricks-lakebase`
- `databricks-lakeflow-connect`
- `databricks-metric-views`
- `databricks-ml-training`
- `databricks-mlflow-evaluation`
- `databricks-model-serving`
- `databricks-pipelines`
- `databricks-python-sdk`
- `databricks-serverless-migration`
- `databricks-spark-structured-streaming`
- `databricks-synthetic-data-gen`
- `databricks-unity-catalog`
- `databricks-unstructured-pdf-generation`
- `databricks-vector-search`
- `databricks-zerobus-ingest`

Phase 1 skills read:

- `databricks-core`
- `databricks-dabs`
- `databricks-apps`
- `databricks-apps-python`

Recommended next skills before implementation:

- `databricks-synthetic-data-gen`
- `databricks-ml-training`
- `databricks-model-serving`
- `databricks-app-design`
- `databricks-jobs`
- `databricks-unity-catalog`
- `databricks-python-sdk`

## MCP Tools Verified

Available Databricks MCP capabilities include:

- Workspace/profile management
- Current user lookup
- Unity Catalog catalog/schema/volume/function management
- SQL execution
- SQL warehouse listing and selection
- Cluster/compute listing and management
- Jobs management
- Spark Declarative Pipeline management
- Databricks Apps listing/deployment
- Model Serving endpoint listing/querying
- Vector Search endpoint listing/querying
- UC volume file operations
- Lakehouse Federation connections

MCP auth status:

- `manage_workspace(status)` initially failed because default credentials were not configured for the MCP session.
- `manage_workspace(list)` succeeded and showed the profiles above.
- `manage_workspace(switch, profile=sa_profile)` succeeded.
- No destructive MCP actions were run.

CLI note:

- `databricks apps manifest --profile sa_profile` succeeded and returned the AppKit plugin manifest.
- The CLI emitted a cache warning while reading the manifest: `Failed to create temp cache file ... Access is denied.` This did not block the manifest output.

## Architecture

Proposed final architecture:

```text
Synthetic source simulators
  PostgreSQL-style: customers, loyalty_activity
  MySQL-style: transactions
  SaaS-style: support_tickets, campaign_interactions
  Documents: retention guidelines, offer policies, service playbook

        |
        v

Bronze Delta tables in Unity Catalog
  bronze_customers
  bronze_loyalty_activity
  bronze_transactions
  bronze_support_tickets
  bronze_campaign_interactions
  bronze_retention_documents

        |
        v

Silver Customer 360
  silver_customer_360
  silver_customer_activity
  silver_retention_documents
  data-quality checks and invalid-record counts

        |
        v

ML features and churn prediction
  explainable classifier tracked with MLflow where practical
  churn probability, risk category, reason codes, model version

        |
        v

Gold retention intelligence
  gold_customer_churn_predictions
  gold_customer_retention_actions
  gold_executive_metrics

        |
        v

Databricks App
  Executive Overview
  Customer 360
  Retention Copilot
```

## Decisions

- Use an isolated Unity Catalog schema: `workspace.retail_intelligence`.
- Preserve `customer_id` from source simulation through Bronze, Silver, ML scoring, GenAI context, Gold actions, and app navigation.
- Use deterministic synthetic data with a fixed random seed.
- Use Delta tables for all lakehouse layers.
- Prefer a Databricks Workflow/Lakeflow Job orchestrated through a Databricks Asset Bundle.
- Prefer AppKit/React Databricks App for the polished three-page demo.
- Use SQL warehouse-backed analytics for the app because the UI is primarily read-only dashboards, customer detail, and filtered exploration.
- Use a deterministic retention-action generator as the guaranteed demo path.
- Use a Model Serving endpoint for GenAI behind a clean abstraction only after testing one READY endpoint with a tiny prompt; otherwise keep deterministic fallback as the demo path.
- Do not use Lakebase in the first implementation because the app is read-only and the Databricks App guidance recommends Analytics for dashboards, charts, aggregations, filtered queries, browsing, and customer detail pages.
- Do not use Vector Search initially because no endpoint exists; use small policy documents stored as Delta rows and retrieve deterministic excerpts from Silver/Gold context. Add Vector Search later only if semantic retrieval becomes important.
- Do not create, modify, or delete unrelated Databricks resources.

## Proposed Resource Names

Subject to approval:

- Catalog: `workspace`
- Schema: `retail_intelligence`
- App name: `retail-intelligence`
- Bundle target: `dev`
- Job name: `retail-intelligence-pipeline-dev`
- Optional Spark Declarative Pipeline name: omit initially unless Phase 2 design finds DLT/SDP is worth the extra surface area. Prefer one Lakeflow Job with Python tasks for speed and demo reliability.
- Optional model name: `workspace.retail_intelligence.churn_model`
- Optional volume: `workspace.retail_intelligence.assets`
- Tables:
  - `workspace.retail_intelligence.bronze_customers`
  - `workspace.retail_intelligence.bronze_loyalty_activity`
  - `workspace.retail_intelligence.bronze_transactions`
  - `workspace.retail_intelligence.bronze_support_tickets`
  - `workspace.retail_intelligence.bronze_campaign_interactions`
  - `workspace.retail_intelligence.bronze_retention_documents`
  - `workspace.retail_intelligence.silver_customer_360`
  - `workspace.retail_intelligence.silver_customer_activity`
  - `workspace.retail_intelligence.silver_retention_documents`
  - `workspace.retail_intelligence.gold_customer_churn_predictions`
  - `workspace.retail_intelligence.gold_customer_retention_actions`
  - `workspace.retail_intelligence.gold_executive_metrics`

## Resources Created

Databricks resources created or updated:

- Schema: `workspace.retail_intelligence`
- Bundle deployment path: `/Workspace/Users/reza.khamooshi@gmail.com/.bundle/retail-intelligence/dev`
- Job: `[dev reza_khamooshi] [dev] retail-intelligence-pipeline`
- Job ID: `622776603050686`
- Successful run URL: `https://dbc-dee9e2b6-b2e5.cloud.databricks.com/jobs/622776603050686/runs/168518623052951?o=7474645848673684`
- Latest successful Phase 3 run URL: `https://dbc-dee9e2b6-b2e5.cloud.databricks.com/jobs/622776603050686/runs/106579937653629?o=7474645848673684`
- Latest successful Phase 4 run URL: `https://dbc-dee9e2b6-b2e5.cloud.databricks.com/jobs/622776603050686/runs/359342286938614?o=7474645848673684`
- App URL: `https://retail-intelligence-7474645848673684.aws.databricksapps.com`
- App deployment ID: `01f18b7de4821bb4bcc27d2b7ba52343`
- App status: `RUNNING`
- MLflow experiment: `/Users/reza.khamooshi@gmail.com/retail-intelligence/churn`
- MLflow experiment ID: `1893970378577632`
- Bronze tables:
  - `workspace.retail_intelligence.bronze_customers` -> 500 records
  - `workspace.retail_intelligence.bronze_transactions` -> 4,205 records
  - `workspace.retail_intelligence.bronze_loyalty_activity` -> 500 records
  - `workspace.retail_intelligence.bronze_support_tickets` -> 300 records
  - `workspace.retail_intelligence.bronze_campaign_interactions` -> 300 records
  - `workspace.retail_intelligence.bronze_retention_documents` -> 4 records
- Silver tables:
  - `workspace.retail_intelligence.silver_customer_360` -> 500 records
  - `workspace.retail_intelligence.silver_customer_activity` -> 500 records
  - `workspace.retail_intelligence.silver_retention_documents` -> 4 records
  - `workspace.retail_intelligence.silver_data_quality_summary` -> 6 records
  - `workspace.retail_intelligence.silver_churn_features` -> 500 records
- Gold tables:
  - `workspace.retail_intelligence.gold_customer_churn_predictions` -> 500 records
  - `workspace.retail_intelligence.gold_model_metrics` -> 2 records
  - `workspace.retail_intelligence.gold_customer_retention_actions` -> 500 records
- Status table:
  - `workspace.retail_intelligence.pipeline_status`

Local files created:

- `PROJECT.md`
- `README.md`
- `databricks.yml`
- `requirements.txt`
- `pyproject.toml`
- `prompts/01-build-retail-intelligence.md`
- `resources/retail_intelligence.job.yml`
- `src/retail_intelligence/data/synthetic.py`
- `src/retail_intelligence/ml/churn.py`
- `src/retail_intelligence/genai/retention.py`
- `src/retail_intelligence/pipelines/customer360.py`
- `src/retail_intelligence/pipelines/run_pipeline.py`
- `tests/test_synthetic_data.py`
- `tests/test_customer360.py`
- `tests/test_churn.py`
- `tests/test_retention.py`
- `app/retail-intelligence`
- `resources/retail_intelligence.app.yml`

## Current Implementation Status

Phase 6 is complete.

The local repo, available skill/tool surface, Databricks MCP server, workspace resources, and AppKit capabilities have been inspected. The isolated schema, DAB skeleton, deterministic synthetic data, Bronze/Silver pipeline, churn features, Spark ML churn model, MLflow experiment, Gold predictions, deterministic retention-action generator, serverless Lakeflow Job, and three-page Databricks App are implemented, validated, deployed, and running.

Validation results:

- Local dependency-free test runner: passed 12 test functions.
- `python -m pytest`: not run because `python` is not on PATH in this shell.
- `py -m pytest`: not run because `pytest` is not installed in the available Python interpreter.
- `databricks bundle validate --strict -t dev --profile sa_profile`: passed.
- `databricks bundle deploy -t dev --profile sa_profile`: passed.
- `databricks bundle run retail_intelligence_pipeline -t dev --profile sa_profile`: passed on Phase 4 run `359342286938614`.
- Databricks SQL table-count validation: passed.
- MLflow experiment lookup succeeded for `/Users/reza.khamooshi@gmail.com/retail-intelligence/churn`.
- Gold risk distribution: High = 37, Medium = 147, Low = 316.
- Gold model metrics: `customers_scored = 500`, `model_test_auc = 0.6178`, `model_version = spark-logistic-regression-v1`.
- Demo customer `CUST-0007` appears in Silver Customer 360 as `Maja Lindgren`, `Platinum`, `Premium home`, with `spend_trend_ratio = 0.112`, `open_support_ticket_count = 4`, `campaign_engagement_rate = 0.0`, `unused_loyalty_points = 15600`, and `churn_label = 1`.
- Demo customer `CUST-0007` appears in Gold churn predictions with `churn_probability = 0.9997`, `risk_category = High`, and reason codes `Declining spend`, `Unresolved support issue`, `Low service satisfaction`, `Low campaign engagement`.
- Gold retention actions: 500 actions for 500 distinct customers.
- Demo customer `CUST-0007` appears in Gold retention actions with a high-risk summary, recommended personal service recovery, `phone` as suggested channel, and evidence from Customer 360, churn model output, retention campaign guidelines, and recent support history.
- Generation mode is `deterministic_fallback`; business-facing app copy should not claim this output came from a live LLM.
- Serving endpoint smoke tests:
  - `databricks-claude-sonnet-5` returned `RESOURCE_DOES_NOT_EXIST` when queried despite appearing in the endpoint list.
  - `databricks-gpt-oss-20b` was reachable, but the tiny response was not reliable enough for a live customer demo.
- Phase 5 SQL validation: representative Executive Overview, churn-driver, customer-action, Customer 360 detail, transaction, support, and operations queries passed against SQL warehouse `ffdf1653dbc170db`.
- Phase 6 root DAB validation: `databricks bundle validate --strict -t dev --profile sa_profile` passed with the app resource included.
- AppKit validation: `databricks apps validate --profile sa_profile` passed.
- App deployment: `databricks bundle run retail_intelligence_app -t dev --profile sa_profile` passed.
- App status: `databricks apps get retail-intelligence --profile sa_profile` reports `RUNNING`.
- Runtime app view fix: the app service principal `71dbfb5a-4671-4978-8c84-ee64069327f1` was granted `CAN_USE` on SQL warehouse `ffdf1653dbc170db`, `USE CATALOG` on `workspace`, and `USE SCHEMA`, `SELECT` on `workspace.retail_intelligence` so SQL-backed views can run and read the demo tables.
- Local environment note: Node/npm are available outside the Codex sandbox. Use escalated shell commands and call `npm.cmd` instead of `npm` in PowerShell to avoid the `npm.ps1` execution-policy block.

Issues found and fixed during Phase 2:

- Databricks notebook execution does not define `__file__`; `run_pipeline.py` now derives workspace source paths from `dbutils` when running on Databricks.
- Databricks notebook context path needed a `/Workspace` import-path fallback for bundled workspace files.
- The demo customer initially picked up an extra random campaign interaction; campaign generation now excludes `CUST-0007` from the random pool after explicit demo events.
- Initial Phase 3 model training used labels that were too weakly correlated to Customer 360 signals; training labels now combine known churn labels with unified business-signal thresholds so the model learns from the same behavioral signals shown in the app.
- The first Phase 3 scoring write failed after model training because local dict rows were treated as Spark Rows; the prediction metadata assembly now handles local dicts correctly.
- MLflow experiment creation initially needed its parent workspace folder; created `/Users/reza.khamooshi@gmail.com/retail-intelligence`.

## Remaining Tasks

Remaining tasks:

- Optional: perform manual business-demo walkthrough in the running Databricks App.
- Optional: commit the finished prototype.
- Keep existing `streaming-churn-demo-*` resources untouched.

Future phases:

- Production evolution: permissions, scheduled jobs, stronger model validation, live GenAI integration, and richer observability.

## Exact Deployment and Validation Commands

Profile discovery:

```powershell
databricks auth profiles
```

Read-only inventory examples:

```powershell
databricks current-user me --profile <PROFILE>
databricks catalogs list --profile <PROFILE>
databricks schemas list workspace --profile <PROFILE>
databricks warehouses list --profile <PROFILE>
databricks clusters list --profile <PROFILE>
databricks jobs list --profile <PROFILE>
databricks serving-endpoints list --profile <PROFILE>
databricks apps list --profile <PROFILE>
```

Phase 2 proposed setup commands after approval:

```powershell
databricks schemas create workspace retail_intelligence --comment "Isolated schema for retail-intelligence prototype" --profile sa_profile
databricks warehouses start ffdf1653dbc170db --profile sa_profile
databricks apps manifest --profile sa_profile
```

Local validation after implementation:

```powershell
python -m pytest
databricks bundle validate -t dev --profile sa_profile
```

Deployment after approval:

```powershell
databricks bundle deploy -t dev --profile sa_profile
databricks bundle run retail_intelligence_pipeline -t dev --profile sa_profile
databricks apps validate --profile sa_profile
databricks bundle run deploy_app -t dev --profile sa_profile
```

Phase 2 actual validation commands:

```powershell
$env:PYTHONPATH='src;tests'; py -c "import importlib; count=0
for m in ['test_synthetic_data','test_customer360']:
    mod=importlib.import_module(m)
    for name in dir(mod):
        if name.startswith('test_'):
            getattr(mod,name)(); count += 1
print(f'Ran {count} test functions successfully')"

databricks bundle validate --strict -t dev --profile sa_profile
databricks bundle deploy -t dev --profile sa_profile
databricks bundle run retail_intelligence_pipeline -t dev --profile sa_profile
```

Phase 3 actual validation commands:

```powershell
$env:PYTHONPATH='src;tests'; py -c "import importlib; count=0
for m in ['test_synthetic_data','test_customer360','test_churn']:
    mod=importlib.import_module(m)
    for name in dir(mod):
        if name.startswith('test_'):
            getattr(mod,name)(); count += 1
print(f'Ran {count} test functions successfully')"

databricks bundle validate --strict -t dev --profile sa_profile
databricks bundle deploy -t dev --profile sa_profile
databricks workspace mkdirs /Users/reza.khamooshi@gmail.com/retail-intelligence --profile sa_profile
databricks bundle run retail_intelligence_pipeline -t dev --profile sa_profile
databricks experiments get-by-name /Users/reza.khamooshi@gmail.com/retail-intelligence/churn --profile sa_profile
```

Phase 4 actual validation commands:

```powershell
$env:PYTHONPATH='src;tests'; py -c "import importlib; count=0
for m in ['test_synthetic_data','test_customer360','test_churn','test_retention']:
    mod=importlib.import_module(m)
    for name in dir(mod):
        if name.startswith('test_'):
            getattr(mod,name)(); count += 1
print(f'Ran {count} test functions successfully')"

databricks bundle validate --strict -t dev --profile sa_profile
databricks bundle deploy -t dev --profile sa_profile
databricks bundle run retail_intelligence_pipeline -t dev --profile sa_profile
```

Direct app status after deployment:

```powershell
databricks apps get retail-intelligence --profile sa_profile
```

App view permissions troubleshooting:

```powershell
databricks permissions update warehouses ffdf1653dbc170db --json '@warehouse-permissions.json' --profile sa_profile
```

With `warehouse-permissions.json` containing:

```json
{
  "access_control_list": [
    {
      "service_principal_name": "71dbfb5a-4671-4978-8c84-ee64069327f1",
      "permission_level": "CAN_USE"
    }
  ]
}
```

```sql
GRANT USE CATALOG ON CATALOG workspace TO `71dbfb5a-4671-4978-8c84-ee64069327f1`;
GRANT USE SCHEMA, SELECT ON SCHEMA workspace.retail_intelligence TO `71dbfb5a-4671-4978-8c84-ee64069327f1`;
SHOW GRANTS ON CATALOG workspace;
SHOW GRANTS ON SCHEMA workspace.retail_intelligence;
```

Phase 5 validation commands run:

```powershell
databricks warehouses start ffdf1653dbc170db --profile sa_profile
databricks apps init --name retail-intelligence --features analytics --set analytics.sql-warehouse.id=ffdf1653dbc170db --description "Retail intelligence Customer 360 and retention demo" --run none --output-dir app --profile sa_profile
databricks bundle validate --strict -t dev --profile sa_profile
databricks apps validate --profile sa_profile
node -v
npm -v
```

Phase 6 commands run:

```powershell
cd app\retail-intelligence
npm.cmd install
npm.cmd run typegen
npm.cmd run typecheck
databricks apps validate --profile sa_profile
cd ..\..
databricks bundle deploy -t dev --profile sa_profile
databricks bundle run retail_intelligence_app -t dev --profile sa_profile
databricks apps get retail-intelligence --profile sa_profile
```
