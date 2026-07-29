You are building a Databricks-native prototype called **retail-intelligence** for a Solutions Architect customer presentation.

Use the installed **Databricks AI Dev Kit skills** and the configured **Databricks MCP server** wherever appropriate. Before coding:

1. Inspect and list the available AI Dev Kit skills.
2. Verify access to the Databricks MCP server.
3. Inspect the current Databricks workspace, available catalogs, schemas, SQL warehouses, clusters/serverless compute, model-serving endpoints, and app capabilities.
4. Do not make destructive changes to existing workspace resources.
5. Prefer creating isolated resources under a dedicated schema such as:
   `workspace.retail_intelligence`

First create or update `PROJECT.md` with:

* Business problem
* Architecture
* Decisions
* Resources created
* Current implementation status
* Remaining tasks
* Exact deployment and validation commands

## Business scenario

A mid-sized retailer has fragmented data across:

* PostgreSQL customer and loyalty data
* MySQL transaction data
* SaaS support-ticket and campaign exports
* Internal retention-policy documents

Executives do not have a single source of truth. Retention teams react too late, churn decisions are based on spreadsheets, and marketing campaigns are generic.

Build one cohesive solution that:

1. Unifies customer data into a governed Customer 360.
2. Predicts customer churn.
3. Uses customer data, model output, and internal business documents to generate a grounded next-best retention action.
4. Presents everything through a Databricks App for business and technical leaders.

The app must clearly communicate:

**Unified Data → Predict Risk → Generate Action → Drive Outcome**

## Technical architecture

Implement a realistic but lightweight Databricks prototype:

```text
PostgreSQL simulation:
customers
loyalty_activity

MySQL simulation:
transactions

SaaS simulation:
support_tickets
campaign_interactions

Internal documents:
retention guidelines
offer policies
customer-service playbook

        ↓

Bronze Delta tables

        ↓

Silver Customer 360
Data-quality checks
Identity resolution

        ↓

ML features and churn prediction

        ↓

Gold customer retention actions

        ↓

Databricks App
Executive Overview
Customer 360
Retention Copilot
```

Use:

* Databricks Asset Bundles
* Unity Catalog
* Delta tables
* A Lakeflow Job or Databricks Workflow
* Python and PySpark for data generation and transformation
* MLflow for model tracking when practical
* Databricks SQL for app queries
* A Databricks App for the user interface
* A Databricks model endpoint for GenAI only if one is already available and reliable

Do not depend on infrastructure that cannot be created or validated quickly.

## Synthetic data

Generate deterministic synthetic data using a fixed random seed.

Create approximately:

* 500 customers
* 3,000–5,000 transactions
* 500 loyalty events
* 300 support interactions
* 300 campaign interactions
* 3–5 short internal policy documents

Include realistic churn signals:

* Declining purchase frequency
* Reduced spending
* Long inactivity
* Unresolved support tickets
* Low campaign engagement
* Unused loyalty benefits
* Changes in return frequency

Include a known churn label so the model can be trained and evaluated.

Ensure several demonstration customers have clear stories, especially one high-risk customer whose data appears consistently through all application pages.

## Data layers

Create source-specific Bronze tables rather than pretending everything originated from one source.

Example tables:

```text
bronze_customers
bronze_loyalty_activity
bronze_transactions
bronze_support_tickets
bronze_campaign_interactions
bronze_retention_documents
```

Create Silver tables such as:

```text
silver_customer_360
silver_customer_activity
silver_retention_documents
```

Create Gold tables such as:

```text
gold_customer_churn_predictions
gold_customer_retention_actions
gold_executive_metrics
```

The same `customer_id` must be preserved through Customer 360, model scoring, GenAI context, and the final recommended action.

Add practical data-quality checks:

* Non-null customer IDs
* Valid transaction amounts
* Valid dates
* Deduplication
* Referential integrity
* Recognized customer records
* Quarantine or count invalid records

## Predictive ML

Train a simple, explainable churn model using the synthetic data.

Prefer a model that is reliable and fast to train, such as logistic regression, random forest, or gradient-boosted trees.

Produce:

* Churn probability
* Risk category: Low, Medium, High
* Top contributing business factors or understandable reason codes
* Model version
* Scoring timestamp

Track the model with MLflow when practical.

The demo must show that the prediction was produced from the unified data rather than hard-coded directly in the UI.

## GenAI activation

Create a Retention Copilot experience.

Inputs must include:

* Unified customer profile
* Purchase and engagement history
* Support history
* Churn probability
* Churn reason codes
* Relevant internal retention guidelines

Output:

* Concise customer-risk summary
* Recommended next-best action
* Personalized retention message
* Evidence or sources used
* Suggested channel
* Estimated business rationale

The GenAI capability must not appear isolated. Explicitly show that it uses both the Customer 360 data and ML prediction.

If a reliable Databricks model-serving endpoint is available, use it through a clean service abstraction.

Also implement a deterministic fallback generator so the live demo continues working if the endpoint is unavailable. Clearly label fallback output in the code, but keep the business-facing demo clean.

Do not claim that the fallback is a real LLM call.

## Databricks App

Build a polished but lightweight Databricks App with exactly three primary pages.

### Page 1 — Executive Overview

Show:

* Customers at high churn risk
* Estimated revenue at risk
* Retention opportunities
* Churn-risk distribution
* High-risk customers by loyalty tier or segment
* Top churn drivers
* Last pipeline status

Include a table of customers requiring action.

Selecting a customer should navigate to Customer 360.

Business message:

“Leadership now has one governed view of customer risk and revenue exposure.”

### Page 2 — Customer 360

Show the selected customer’s:

* Profile
* Loyalty tier
* Purchase history
* Spending trend
* Support tickets
* Campaign engagement
* Churn probability
* Risk category
* Model reason codes

Clearly show source badges:

* PostgreSQL — profile and loyalty
* MySQL — transactions
* SaaS — support and campaign activity
* ML model — churn score

Display:

**Sources → Customer 360 → Churn Prediction**

Provide a button to continue to Retention Copilot while preserving the same `customer_id`.

### Page 3 — Retention Copilot

Show:

* Customer context
* Churn probability
* Model reason codes
* Relevant internal policy excerpts
* Generated risk summary
* Recommended intervention
* Personalized message
* Suggested delivery channel
* Evidence used

Display an evidence panel such as:

```text
Based on:
✓ Customer 360
✓ Churn model output
✓ Retention campaign guidelines
✓ Recent support history
```

Display:

**Customer 360 + ML Prediction + Business Knowledge → Next-Best Action**

## Persistent solution journey

Across all pages, display a compact journey indicator:

```text
1. Unified Data → 2. Predict Risk → 3. Generate Action → 4. Drive Outcome
```

Highlight the relevant stage for the current page.

This is essential because the presentation must clearly demonstrate that all four architectural layers are connected.

## Operations panel

Add a small expandable operations panel rather than a fourth primary page.

Show:

* Last pipeline execution
* Pipeline status
* Bronze, Silver, and Gold record counts
* Data-quality status
* Model version
* Last training timestamp
* Last scoring timestamp

Add a “Run pipeline” button only if triggering the Databricks job from the app can be implemented safely and reliably. Otherwise show status only and provide the CLI command for running the job.

## UX requirements

* Optimize for a live customer demo.
* Use clear business language.
* Avoid exposing unnecessary technical implementation details.
* Provide useful loading, empty, and error states.
* Avoid excessive animations.
* Make the high-risk demonstration customer easy to find.
* Ensure navigation works without manually copying customer IDs.
* Use SEK for monetary values.
* Do not invent unsupported business metrics without documenting the assumptions.

## Project structure

Create a clear structure similar to:

```text
retail-intelligence/
  app/
  resources/
  src/
    data/
    pipelines/
    ml/
    genai/
  tests/
  prompts/
  databricks.yml
  app.yaml
  requirements.txt
  README.md
  PROJECT.md
```

Adapt this structure if the selected AI Dev Kit skill recommends something better.

## Deployment requirements

Use the Databricks MCP server to inspect and validate resources where possible.

Create a Databricks Asset Bundle that can:

* Validate configuration
* Deploy jobs and application resources
* Run the data pipeline
* Deploy the Databricks App

Before deploying:

1. Show the proposed resource names.
2. Run local validation and tests.
3. Run `databricks bundle validate`.
4. Fix validation failures.
5. Deploy only to an isolated development target.

Do not modify or delete unrelated Databricks resources.

## Testing

Add lightweight tests for:

* Synthetic-data determinism
* Customer 360 construction
* Churn feature generation
* Risk categorization
* Retention-action generation
* Fallback behavior
* Preservation of `customer_id` across layers

## Documentation

Create a useful `README.md` containing:

* Business problem
* Architecture
* Four-layer mapping
* Local setup
* Databricks prerequisites
* Authentication profile
* Validation commands
* Deployment commands
* Pipeline run commands
* App deployment commands
* Demo script
* Known limitations
* Production evolution

Create a Mermaid architecture diagram in the README.

Create `prompts/01-build-retail-intelligence.md` containing this original prompt.

## Execution approach

Work incrementally:

### Phase 1

Inspect skills, MCP access, workspace capabilities, and existing resources.

### Phase 2

Create the architecture, bundle structure, synthetic data, and pipeline.

### Phase 3

Build and validate the churn model.

### Phase 4

Build the GenAI service and deterministic fallback.

### Phase 5

Build the three-page Databricks App.

### Phase 6

Test, validate, deploy, and provide exact commands.

After every phase:

* Update `PROJECT.md`.
* Summarize files changed.
* Report validation results.
* State the next phase.
* Do not continue past a blocking error without explaining it.

Start now with **Phase 1 only**. Do not implement the full solution yet. Inspect the available AI Dev Kit skills and Databricks MCP tools, inspect the repository and workspace, then propose the final resource architecture and implementation plan for approval.
