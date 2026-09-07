# AI-Powered Business Automation Hub

A professional Python foundation for processing business requests through structured, testable automation workflows. The project is intentionally conventional: it provides clear validation, persistence, logging, configuration, and workflow boundaries without introducing an advanced agentic system.

**Current status: Phase 8: Operational Analytics**

## Problem Statement

Business requests often arrive through inconsistent channels and require repeatable validation, processing, storage, and reporting. This project establishes a dependable local foundation for those steps so future integrations can be added without coupling them to the core workflow.

## Workflow Architecture

```text
Email / CSV / API Input
    -> Input Validation and Transformation
    -> BusinessTask
    -> FastAPI Route (optional HTTP boundary)
    -> AI Analysis and Classification
    -> Automation Rules
    -> Action Planning
    -> Action Execution
    -> Integration Router
       -> Notification Connector
       -> Webhook Connector
       -> Report Connector
    -> Database Storage
    -> AutomationResult
```

## CURRENTLY IMPLEMENTED

- `Settings` configuration with environment overrides and centralized `pathlib.Path` locations.
- Automatic creation of input, output, database, and log directories.
- Pydantic models for `BusinessTask`, `AutomationResult`, and `WorkflowStatus`.
- Pydantic input models for structured email, CSV rows, and API-style payloads.
- Unified ingestion adapters that transform external inputs into `BusinessTask` objects.
- Local email-style ingestion without a real mail provider.
- CSV ingestion with file, extension, required-column, and row validation.
- JSON/API-style dictionary ingestion without a web server.
- Structured `TaskAnalysis` models with category, priority, summary, confidence, and recommended actions.
- Custom application exceptions and reusable validation rules.
- Console and file logging with duplicate-handler protection.
- SQLite database initialization, parameterized task storage, retrieval, and counting.
- A focused `AIAnalyzer` abstraction with deterministic, credential-free demo analysis.
- Rule-based classification for support, sales, urgent, billing, operations, and general tasks.
- Rule-based priority detection for low, medium, high, and critical tasks.
- Related SQLite analysis records linked to stored business tasks.
- A workflow that validates, analyzes, stores, and returns structured task results.
- Deterministic `AutomationRulesEngine` action planning for urgent, support, sales, billing, operations, and general tasks.
- Safe local `ActionExecutor` execution with structured success and failure results.
- Related SQLite action persistence and retrieval by task ID.
- Execution lifecycle logging for task receipt, analysis, planning, and action outcomes.
- A unified-input demo covering email, CSV, and API-style sources.
- `IntegrationRouter` decoupling action execution from connector implementations.
- Notification integration simulation with recipient-group and priority payloads.
- Webhook integration simulation with payload validation and no network access.
- Local report/event generation under the configured output directory.
- FastAPI REST service over the existing workflow.
- Single-task and sequential batch task processing.
- Health monitoring and automatic OpenAPI documentation.
- Explicit task lifecycle tracking: `received`, `processing`, `completed`, and `failed`.
- Detailed SQLite processing persistence with timing, planned actions, execution results, and integration results.
- Deterministic duplicate task protection by task ID.
- Controlled workflow failure handling with safe API errors and logged diagnostics.
- Reliable sequential batch behavior with an explicit result for every submitted item.
- Operational overview analytics for task status, source, category, and priority.
- Processing performance analytics with duration metrics in seconds.
- Persisted integration activity analytics distinguishing simulated and completed events.
- Bounded recent activity monitoring with deterministic newest-first ordering.
- Pytest coverage for configuration, input models, ingestion, validation, analysis, rules, execution, database operations, and workflow behavior.

## FUTURE PLANNED INTEGRATIONS

- Gmail, Outlook, Slack, and Microsoft Teams.
- Real webhook delivery, CRM systems, and external business APIs.
- Real LLM provider integration behind the existing `AIAnalyzer` boundary.
- Reporting dashboards and production deployment.

The REST API, local integrations, and demo mode are implemented. Gmail, Outlook, Slack, Teams, real webhook delivery, CRM systems, external business APIs, and real LLM providers remain future integrations.

## PHASE 7: RELIABILITY & PERSISTENCE

Tasks are persisted with a lifecycle record and processing timestamps. A successful workflow reaches `completed`; failures after task acceptance reach `failed` and retain a generic failure marker while detailed diagnostics remain in logs. Processing duration is stored in milliseconds.

Task IDs are deterministic idempotency keys. Submitting an existing task ID through `POST /tasks` returns HTTP `409` and does not overwrite the original record. In `POST /tasks/batch`, duplicate or failed items receive an individual `failed` result while other items continue sequentially.

The database keeps processing information in a separate `task_processing` table, so existing SQLite databases are upgraded non-destructively when initialized.

## PHASE 8: OPERATIONAL ANALYTICS

The backend analytics layer reads persisted task, analysis, lifecycle, timing, and integration data. It safely handles empty databases and never invents duration or integration information for records where those values were not stored. The analytics endpoints can later support a dashboard or external reporting system; no frontend dashboard is included.

Available endpoints:

- `GET /analytics/overview` returns total, completed, failed, received, and processing counts, safe completion/failure rates, and grouped source/category/priority counts.
- `GET /analytics/performance` returns average, minimum, and maximum processing duration in seconds for records with duration metadata.
- `GET /analytics/integrations` returns persisted integration event counts by connector and status.
- `GET /analytics/recent?limit=20` returns bounded newest-first task activity. Limits are safely clamped to 1-100.

Real email providers, API servers, webhook delivery, CRM systems, external APIs, and LLM integrations are not implemented yet. All Phase 5 connectors default to local simulation and no external credentials are required.

## Unified Input Layer

The input layer keeps external formats separate from the automation workflow:

1. `EmailIngestion` validates `EmailInput` and creates an email-sourced `BusinessTask`.
2. `CSVIngestion` validates a `task_id,title,content,source` CSV format and creates one task per row.
3. `APIIngestion` validates a Python dictionary representing a future API request.

All three adapters raise clear ingestion exceptions for malformed input and return the same `BusinessTask` type. The existing workflow then performs analysis, rule evaluation, action execution, and SQLite storage.

## AI Analysis Architecture

`Workflow` receives an `AIAnalyzer` through dependency injection. The analyzer currently uses deterministic keyword rules, which makes local runs and tests repeatable. `Settings` exposes `DEMO_MODE` and `AI_PROVIDER` so a future provider can be added without moving analysis logic into the workflow.

Each analysis contains:

- `category`: `support`, `sales`, `urgent`, `billing`, `operations`, or `general`.
- `priority`: `low`, `medium`, `high`, or `critical`.
- `summary`: a concise task-title summary.
- `confidence`: a validated score from `0.0` to `1.0`.
- `recommended_actions`: deterministic next-step suggestions.

The Phase 3 rules engine converts analysis into structured actions. The local executor simulates those actions, records completion or failure, and never sends email or calls external systems.

## External Action Integrations

`ActionExecutor` continues to own action lifecycle and delegates integration-backed actions to `IntegrationRouter`. The router selects one independent connector:

- `NotificationConnector` creates recipient, subject, message, task, and priority payloads.
- `WebhookConnector` validates event payloads and simulates delivery locally.
- `ReportConnector` writes structured event records to `data/output/`.

`INTEGRATION_SIMULATION_MODE=true` is the default. `ENABLE_WEBHOOK_DELIVERY` is disabled by default, and the current implementation does not make network calls.

## Project Structure

```text
AI-Powered-Business-Automation-Hub/
├── data/                 # Local input and output files
│   └── input/sample_tasks.csv # Demo CSV input
├── database/             # SQLite database files
├── logs/                 # Application logs
├── src/                  # Application package
│   ├── ai_analyzer.py    # Demo analysis and future provider boundary
│   ├── action_executor.py # Safe local action execution
│   ├── analytics.py       # Repository-backed operational analytics
│   ├── api_ingestion.py   # API-style dictionary adapter
│   ├── automation_rules.py # Deterministic action planning
│   ├── csv_ingestion.py   # CSV file adapter
│   ├── integration_models.py # Connector request/result models
│   ├── integration_router.py  # Action-to-connector routing
│   ├── database_manager.py
│   ├── models.py         # Business and analysis models
│   ├── email_ingestion.py # Structured email adapter
│   ├── input_models.py    # External input models
│   ├── notification_connector.py # Notification simulation
│   ├── report_connector.py # Local event reports
│   ├── api/                 # FastAPI service layer
│   │   ├── app.py
│   │   ├── dependencies.py
│   │   ├── routes.py
│   │   └── schemas.py
│   ├── task_ingestion.py  # Shared ingestion boundary
│   ├── webhook_connector.py # Webhook simulation
│   └── workflow.py       # Validation, analysis, and persistence flow
├── tests/                # Automated tests
├── .env.example          # Optional environment configuration
├── requirements.txt      # Runtime and test dependencies
└── pytest.ini            # Pytest configuration
```

## Installation

From this directory, create and activate a virtual environment, then install dependencies:

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Copy `.env.example` to `.env` only when local configuration overrides are needed. Demo and integration simulation modes work without API keys, credentials, or internet access.

## Configuration

- `DEMO_MODE=true` enables deterministic analysis.
- `INTEGRATION_SIMULATION_MODE=true` prevents external side effects.
- `ENABLE_WEBHOOK_DELIVERY=false` keeps webhook delivery disabled.
- `OUTPUT_DIRECTORY=data/output` controls local report event records.

## API Usage

Start the local service with:

```bash
uvicorn src.api.app:app --reload
```

Available endpoints:

- `GET /health` checks service health.
- `POST /tasks` processes one task through the existing workflow.
- `POST /tasks/batch` processes a JSON list sequentially.
- `GET /tasks/{task_id}` returns persisted task, analysis, and action data.

Example request:

```json
{
    "task_id": "api-001",
    "title": "Customer requests pricing information",
    "content": "Please send enterprise pricing details.",
    "source": "api",
    "metadata": {"customer_id": "customer-123"}
}
```

Interactive documentation is available at `http://127.0.0.1:8000/docs`; the OpenAPI document is available at `/openapi.json`.

## Run Tests

```bash
pytest
```

## Run The Demo

```bash
python -m src.main
```

The demo initializes the local SQLite database, loads one email input, the sample CSV file, and one API-style dictionary, then sends every resulting `BusinessTask` through the full automation workflow. It prints the integration connector and result status for actions that trigger integrations, followed by a concise operational summary. The CLI and FastAPI service share the same workflow and analytics architecture.

## Technology Stack

- Python 3.10+
- Pydantic for domain model validation
- SQLite via Python's standard library
- `pathlib`, `logging`, and `sqlite3` from the standard library
- pytest for automated testing
- python-dotenv for optional local environment configuration
- FastAPI and Uvicorn for the REST service
- HTTPX for isolated API tests
