# 🤖 AI-Powered Business Automation Hub

> A structured, testable Python automation platform that turns business tasks into validated, analyzed, rule-driven, safely executed, persisted, and traceable workflow results.

---

## 1. 📌 Project Title

**AI-Powered Business Automation Hub**

A portfolio-scale Python automation system for structured business task processing, workflow orchestration, local integrations, persistence, REST APIs, and operational analytics.

---

## 2. 📝 One-Line Description

A local business automation platform that receives structured business tasks, validates and analyzes them, plans rule-based actions, executes those actions safely, persists the lifecycle in SQLite, routes integration events, and exposes operational analytics through FastAPI.

---

## 3. 🔴 Problem

Business requests can arrive from different sources and require repeated operational work:

- validation
- normalization
- classification
- prioritization
- action planning
- execution
- persistence
- integration handling
- reporting and monitoring

When these responsibilities are handled as disconnected scripts or tightly coupled logic, workflows become harder to test, trace, extend, and operate reliably.

The project addresses this by providing a single structured workflow with explicit boundaries between ingestion, analysis, automation rules, execution, integrations, persistence, API access, and analytics.

---

## 4. 🟢 Solution

The Hub converts incoming business requests into a common `BusinessTask` model and processes them through a deterministic workflow:

```text
Input
  ↓
Validation
  ↓
Normalization / BusinessTask
  ↓
AI-style Analysis
  ↓
Automation Rules
  ↓
Action Planning
  ↓
Safe Local Execution
  ↓
Integration Routing
  ↓
SQLite Persistence
  ↓
Operational Analytics / REST API
```

The current implementation is deliberately local and deterministic. It demonstrates the architecture and workflow boundaries without pretending that external Gmail, Slack, CRM, webhook, or LLM integrations are already implemented.

---

## 5. ✨ Key Features

### 📥 Unified Input Processing

Supports separate ingestion boundaries for:

- Email-style input
- CSV input
- API-style dictionary payloads

Each adapter validates and transforms input into the shared `BusinessTask` domain model.

### 🧠 Deterministic AI-Style Analysis

The current `AIAnalyzer` uses deterministic keyword-based rules in demo mode.

It produces:

- category
- priority
- summary
- confidence
- recommended actions

Supported categories:

`support` · `sales` · `urgent` · `billing` · `operations` · `general`

Supported priorities:

`low` · `medium` · `high` · `critical`

### ⚙️ Rule-Based Automation

The `AutomationRulesEngine` converts analysis results into structured `AutomationAction` objects.

Examples include:

- flag critical task
- create incident record
- prepare operations notification
- assign support queue
- prepare customer response
- assign sales team
- create sales follow-up
- assign billing review
- assign operations team
- mark for general review

### 🛡️ Safe Action Execution

`ActionExecutor` executes supported actions locally and records:

- successful actions
- failed actions
- action status
- execution metadata
- integration results

External side effects are controlled by the integration configuration.

### 🔌 Integration Routing

The `IntegrationRouter` separates workflow logic from connector implementations.

Current connector boundaries include:

- NotificationConnector
- ReportConnector
- WebhookConnector

The current implementation uses local/simulated behavior rather than claiming real external delivery.

### 💾 SQLite Persistence

The system persists:

- task data
- analysis results
- lifecycle state
- processing timestamps
- processing duration
- planned actions
- execution results
- integration activity

Task IDs provide deterministic duplicate protection.

### 🔁 Idempotent Task Handling

For `POST /tasks`, an existing task ID produces an HTTP 409 duplicate-task response rather than overwriting the original record.

Batch processing handles duplicate or failed items individually while continuing through the remaining items.

### 📊 Operational Analytics

The system provides repository-backed analytics for:

- task totals
- completed and failed tasks
- received and processing states
- completion/failure rates
- source/category/priority distributions
- processing duration
- integration activity
- recent task activity

### 🌐 FastAPI REST API

The API exposes the core workflow and analytics through a local HTTP boundary with OpenAPI documentation.

### 🧪 Automated Testing

The project includes pytest coverage across configuration, models, ingestion, validation, analysis, automation rules, action execution, persistence, workflow behavior, and API-related behavior.

---

## 6. 🔄 How It Works

A single task follows this lifecycle:

1. An input adapter receives the source data.
2. The input is validated.
3. The data is converted into a `BusinessTask`.
4. The workflow checks for duplicate task IDs.
5. The task is persisted.
6. `AIAnalyzer` classifies and prioritizes the task.
7. The analysis is persisted.
8. `AutomationRulesEngine` plans deterministic actions.
9. `ActionExecutor` executes supported actions safely.
10. Integration-backed actions are routed to the appropriate connector.
11. Execution results are persisted.
12. Processing metadata records completion/failure and duration.
13. Analytics can query the persisted operational data.
14. FastAPI exposes the workflow and analytics through HTTP.

---

## 7. 🏗️ Architecture / Workflow

```text
┌─────────────────────────────────────────────────────────────┐
│                        INPUT SOURCES                        │
│             Email • CSV • API-style payloads                │
└──────────────────────────────┬──────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────┐
│                  INGESTION & VALIDATION                     │
│       Input adapters • Pydantic models • validation         │
└──────────────────────────────┬──────────────────────────────┘
                               ↓
                       ┌──────────────┐
                       │ BusinessTask │
                       └──────┬───────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    AI-STYLE ANALYSIS                        │
│       category • priority • summary • confidence            │
└──────────────────────────────┬──────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────┐
│                    AUTOMATION RULES                         │
│                 deterministic action planning               │
└──────────────────────────────┬──────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────┐
│                    ACTION EXECUTOR                          │
│                  controlled local execution                  │
└──────────────────────────────┬──────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────┐
│                    INTEGRATION ROUTER                       │
│       Notification • Report • Webhook connectors             │
└───────────────┬──────────────────┬──────────────────────────┘
                │                  │
                └──────────┬───────┘
                           ↓
                 ┌───────────────────┐
                 │ SQLite Persistence│
                 └─────────┬─────────┘
                           ↓
                 ┌───────────────────┐
                 │ Operational       │
                 │ Analytics         │
                 └─────────┬─────────┘
                           ↓
                 ┌───────────────────┐
                 │ FastAPI REST API  │
                 └───────────────────┘
```

### Core architectural boundaries

| Layer | Responsibility |
|---|---|
| Ingestion | Convert source-specific input into the common domain model |
| Validation | Enforce structured input boundaries |
| AIAnalyzer | Deterministic task analysis with a future provider boundary |
| AutomationRulesEngine | Convert analysis into planned actions |
| ActionExecutor | Execute supported actions and capture outcomes |
| IntegrationRouter | Route integration-backed actions to connectors |
| Connectors | Encapsulate notification, report, and webhook behavior |
| DatabaseManager | Persist tasks, processing, actions, and integration activity |
| AnalyticsService | Calculate operational metrics from persisted data |
| FastAPI | Expose workflow and analytics through HTTP |

---

## 8. 🧰 Technologies

- **Python 3.10+**
- **FastAPI** — REST API layer
- **Uvicorn** — ASGI server
- **Pydantic** — domain and input validation
- **SQLite** — local persistence
- **pytest** — automated testing
- **HTTPX** — API testing support
- **python-dotenv** — environment configuration
- **pathlib** — filesystem path management
- **logging** — application and lifecycle logging

Dependencies are declared in `requirements.txt`.

---

## 9. 📁 Project Structure

```text
AI-Powered-Business-Automation-Hub/
│
├── data/
│   └── input/
│       └── sample_tasks.csv
│
├── database/
│
├── logs/
│
├── src/
│   ├── action_executor.py
│   ├── ai_analyzer.py
│   ├── analytics.py
│   ├── api_ingestion.py
│   ├── automation_rules.py
│   ├── csv_ingestion.py
│   ├── database_manager.py
│   ├── email_ingestion.py
│   ├── input_models.py
│   ├── integration_models.py
│   ├── integration_router.py
│   ├── models.py
│   ├── notification_connector.py
│   ├── report_connector.py
│   ├── task_ingestion.py
│   ├── validators.py
│   ├── webhook_connector.py
│   ├── workflow.py
│   └── api/
│       ├── app.py
│       ├── dependencies.py
│       ├── routes.py
│       └── schemas.py
│
├── tests/
├── .env.example
├── .gitignore
├── pytest.ini
├── requirements.txt
└── README.md
```

---

## 10. ⚙️ Installation

### 1. Create a virtual environment

```bash
python -m venv .venv
```

### 2. Activate it

**Windows PowerShell**

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Optional environment configuration

Copy `.env.example` to `.env` only when you need to override local defaults.

The default demo and integration-simulation configuration does not require external API credentials.

---

## 11. 🔧 Configuration

Configuration is centralized in `src/config.py`.

| Variable | Purpose | Default |
|---|---|---|
| `AUTOMATION_HUB_ROOT` | Project root override | Project directory |
| `AUTOMATION_HUB_DB_NAME` | SQLite database filename | `automation_hub.db` |
| `AUTOMATION_HUB_LOG_LEVEL` | Logging level | `INFO` |
| `DEMO_MODE` | Enables deterministic analysis | `true` |
| `AI_PROVIDER` | AI provider identifier | `demo` |
| `INTEGRATION_SIMULATION_MODE` | Controls integration simulation | `true` |
| `ENABLE_WEBHOOK_DELIVERY` | Enables webhook delivery boundary | `false` |
| `OUTPUT_DIRECTORY` | Local output directory | `data/output` |

Default paths include:

- `data/input/`
- `data/output/`
- `database/`
- `logs/`

---

## 12. ▶️ Usage

### Run the CLI demo

```bash
python -m src.main
```

The demo exercises multiple input styles and sends them through the same workflow.

### Run the API

```bash
uvicorn src.api.app:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

### API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Service health check |
| POST | `/tasks` | Process one business task |
| POST | `/tasks/batch` | Process multiple tasks sequentially |
| GET | `/tasks/{task_id}` | Retrieve persisted task data |
| GET | `/analytics/overview` | Operational overview |
| GET | `/analytics/performance` | Processing performance |
| GET | `/analytics/integrations` | Integration activity |
| GET | `/analytics/recent?limit=20` | Recent task activity |

Interactive OpenAPI documentation is available at `/docs`, with the schema at `/openapi.json`.

---

## 13. 🧪 Example

### Example task

```json
{
  "task_id": "api-001",
  "title": "Customer requests pricing information",
  "content": "Please send enterprise pricing details.",
  "source": "api",
  "metadata": {
    "customer_id": "customer-123"
  }
}
```

### Processing

```text
Customer request
      ↓
BusinessTask validation
      ↓
Sales classification
      ↓
Priority assignment
      ↓
Sales automation rules
      ↓
Assign sales team
      ↓
Create sales follow-up
      ↓
Persist workflow result
      ↓
Expose result / analytics through API
```

### Result model

The workflow returns a structured `AutomationResult` containing:

- task ID
- workflow status
- message
- analysis
- planned actions
- execution result
- processing metadata

The execution result records successful/failed actions and integration results.

---

## 14. 📸 Screenshots

> 🟡 **Reserved area — screenshots will be added later during the Master Visual Portfolio / Visual Presentation stage.**

Planned evidence:

1. FastAPI Swagger/OpenAPI interface
2. Example `POST /tasks` request
3. Structured task-processing response
4. AI-style analysis result
5. Planned automation actions
6. Safe local execution result
7. SQLite persistence evidence
8. Duplicate-task HTTP 409 response
9. Operational analytics endpoints
10. Pytest verification output

---

## 15. 🎥 Demo Video / GIF

> 🟡 **Reserved area — demo video/GIF will be added later during the Master Visual Portfolio / Demo Videos stage.**

Planned demonstration flow:

```text
Start application
    ↓
Submit business task
    ↓
Validate input
    ↓
Analyze category + priority
    ↓
Plan automation actions
    ↓
Execute safely
    ↓
Route connector actions
    ↓
Persist lifecycle
    ↓
Query analytics
    ↓
Show final API result
```

The final demo should show the actual implemented behavior rather than simulated claims.

---

## 16. 📊 Results / Benefits

The implemented system demonstrates:

- A complete local business-task workflow
- Multiple input adapters with a shared domain model
- Deterministic AI-style analysis
- Rule-based automation planning
- Controlled action execution
- Integration connector boundaries
- SQLite lifecycle persistence
- Duplicate-task protection
- Batch processing with per-item results
- FastAPI REST access
- Repository-backed operational analytics
- Structured logging and controlled error responses
- Automated pytest verification
- Clear extension points for future external providers

The primary engineering benefit is separation of responsibilities: ingestion, analysis, decision logic, execution, integrations, persistence, API access, and analytics can evolve without collapsing into one tightly coupled module.

---

## 17. ⚠️ Limitations

The current implementation is intentionally local and deterministic.

Not currently implemented:

- Real Gmail integration
- Real Outlook integration
- Real Slack integration
- Real Microsoft Teams integration
- Production CRM integrations
- External business API integrations
- Production webhook delivery
- A real external LLM provider
- Frontend dashboard
- Production cloud deployment

The `AIAnalyzer` currently uses deterministic demo rules. When demo mode is disabled, the current code reports that the configured AI provider is not implemented rather than silently making an unsupported external call.

---

## 18. 🚀 Future Improvements

Potential future development areas include:

- Real LLM provider implementation behind the existing analyzer boundary
- Gmail and Outlook connectors
- Slack and Microsoft Teams connectors
- Production webhook delivery
- CRM and external business API connectors
- Authentication and authorization for the API
- Background job processing
- Queue-based execution
- Advanced workflow orchestration
- Dashboard visualization
- Production deployment
- Expanded observability
- More advanced analytics
- Additional business-domain rules

These are future improvements, not current implemented capabilities.

---

## 19. 📄 License

No `LICENSE` file is currently included in the project directory.

License terms should be added explicitly before distributing the project under a specific open-source license.

---

## 20. 👤 Author / Contact

**Hammad-Borz**

- GitHub: [Hammad-Borz](https://github.com/Hammad-Borz)
- Repository: [AI-Automation-Mega-Projects](https://github.com/Hammad-Borz/AI-Automation-Mega-Projects)

---

> ⭐ **Portfolio positioning:** A practical Python and AI Automation engineering project demonstrating structured business workflows, deterministic analysis, rule-based automation, safe execution, persistence, integrations, REST APIs, analytics, and automated testing.
