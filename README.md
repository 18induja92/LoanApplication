# Multi-Agent Loan Approval System

A capstone project demonstrating a multi-agent agentic AI system for automated loan application analysis and approval decision making.

## Project Overview

This system uses multiple specialized AI agents (powered by Claude Sonnet 4.6) coordinated through LangGraph to analyze loan applications and provide explainable, auditable decisions. The architecture follows microservices patterns with FastAPI, SQLite database, and a Streamlit UI.

## Architecture

```
Streamlit UI (Frontend)
    ↓
FastAPI Microservice
    ↓
LangGraph Orchestration Engine
    ↓
Multiple Specialized Agents:
  - Applicant Profile Agent
  - Financial Risk Agent
  - Loan Decision Agent
  - Compliance & Action Agent
    ↓
MCP Servers for Tool Integration
    ↓
SQLite Database
```

## Project Structure

```
loan-approval-system/
├── frontend/                  # Streamlit UI
├── services/                  # FastAPI microservice and models
├── orchestration/            # LangGraph orchestration engine
├── agents/                   # AI Agent implementations
├── mcp_servers/             # MCP server implementations
├── database/                # Database schema and utilities
├── config/                  # Configuration management
├── data/                    # Database and mock data
├── tests/                   # Test suite
├── requirements.txt         # Python dependencies
├── .env.example            # Environment template
├── init_db.py              # Database initialization script
└── README.md               # This file
```

## Setup Instructions

### 1. Clone and Navigate to Project
```bash
cd /home/ubuntu/Desktop/demo
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### 5. Initialize Database
```bash
python3 init_db.py
```

The database will be created at `data/loan_approval.db` with the following tables:
- `applications` - Loan application records
- `decisions` - Loan decision outcomes
- `audit_logs` - Compliance and action audit trails

## Technology Stack

- **Language**: Python 3.x
- **LLM**: Claude Sonnet 4.6
- **Agent Framework**: Anthropic Agent SDK
- **Orchestration**: LangGraph, LangChain
- **MCP Framework**: FastMCP
- **API**: FastAPI, Uvicorn
- **UI**: Streamlit
- **Database**: SQLite3
- **Testing**: pytest

## Configuration

All configuration is managed through environment variables in `.env`:

```env
# Anthropic API
ANTHROPIC_API_KEY=your_key_here

# Application
APP_ENV=development
DEBUG=True
LOG_LEVEL=INFO

# Database
DATABASE_PATH=data/loan_approval.db

# API Server
API_HOST=127.0.0.1
API_PORT=8000

# LLM
LLM_MODEL=claude-sonnet-4-6
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2000

# Loan Rules
MIN_CREDIT_SCORE=600
MAX_DTI_RATIO=0.45
MIN_INCOME=30000
```

## Data Models

### Loan Application Request
```python
{
    "applicant_id": "APP-001",
    "age": 35,
    "income": 75000,
    "employment_type": "FULL_TIME",
    "credit_score": 750,
    "loan_amount": 250000,
    "tenure_months": 360,
    "existing_liabilities": 50000,
    "location": "NEW_YORK"
}
```

### Decision Response
```python
{
    "application_id": "CASE-2026-001234",
    "classification": "APPROVED",
    "risk_score": 0.25,
    "confidence_level": 0.92,
    "key_decision_factors": [
        "Strong income stability",
        "Low debt-to-income ratio",
        "Good credit history"
    ],
    "reasoning": "Application meets all lending criteria with low risk profile"
}
```

## Database Schema

### applications table
- `id` - Primary key (APP-XXXXX)
- `applicant_id` - Applicant identifier
- `age`, `income`, `employment_type` - Applicant demographics
- `credit_score` - Credit score (300-850)
- `loan_amount`, `tenure_months` - Loan details
- `existing_liabilities` - Current debts
- `location` - Geographic location
- `status` - PENDING, PROCESSING, COMPLETED, FAILED
- `created_at` - Record creation timestamp

### decisions table
- `id` - Primary key (DEC-XXXXX)
- `application_id` - Reference to application
- `classification` - APPROVED, REJECTED, REVIEW
- `risk_score` - Risk score (0-1)
- `confidence_level` - Confidence (0-1)
- `reasoning` - Explanation
- `key_decision_factors` - JSON array of factors

### audit_logs table
- `id` - Primary key (LOG-XXXXX)
- `case_id` - Case reference
- `application_id` - Application reference
- `agent_name` - Agent that performed action
- `action` - Action taken
- `details` - JSON details
- `timestamp` - Action timestamp

## Usage

### Database Operations
```python
from database import DatabaseManager
from config.settings import DATABASE_PATH

db = DatabaseManager(DATABASE_PATH)

# Create application
app_id = db.create_application({
    "applicant_id": "APP-001",
    "age": 35,
    "income": 75000,
    ...
})

# Get application
app = db.get_application(app_id)

# Update status
db.update_application_status(app_id, "PROCESSING")

# List applications
apps = db.list_applications(status="COMPLETED", limit=10)

# Create decision
decision_id = db.create_decision({
    "application_id": app_id,
    "classification": "APPROVED",
    "risk_score": 0.25,
    ...
})

# Get audit logs
logs = db.get_audit_logs(app_id)

# Get statistics
stats = db.get_statistics()
```

## Phase 1 Deliverables ✓

- [x] Project structure initialized
- [x] Git repository created
- [x] Python virtual environment setup
- [x] Dependencies defined in requirements.txt
- [x] Environment configuration (.env.example, settings.py)
- [x] SQLite database schema with 3 tables
- [x] Database initialization script
- [x] Pydantic data models for all entities
- [x] Database utility functions (CRUD operations)
- [x] Logging configuration
- [x] README documentation

## Next Steps (Phase 2)

The next phase will implement the 4 MCP servers:
1. ApplicantDB MCP Server
2. RiskRulesDB MCP Server
3. DecisionSynthesis MCP Server
4. NotificationSystem MCP Server

## Testing

Run tests with:
```bash
pytest tests/ -v
```

## Logging

Logs are written to both console and file:
- Console: Real-time application logs
- File: `logs/app.log`

Log level can be configured via `LOG_LEVEL` in `.env`

## Troubleshooting

### Database Connection Error
```bash
# Reset database
python3 -c "from database import reset_database; from config.settings import DATABASE_PATH; reset_database(DATABASE_PATH)"

# Re-initialize
python3 init_db.py
```

### Missing Dependencies
```bash
pip install -r requirements.txt
```

### API Key Not Set
```bash
# Make sure .env has your API key
echo "ANTHROPIC_API_KEY=your_key_here" >> .env
```

## Contributing

This is a capstone project. For modifications or enhancements, please follow the project plan in `CAPSTONE_PLAN.md`.

## License

This project is for educational and capstone purposes.

## Support

For issues or questions, refer to:
- `CAPSTONE_PLAN.md` - Detailed project implementation plan
- `logs/app.log` - Application logs
- `/help` - Claude Code help

---

**Status**: Phase 1 Complete ✓
**Next Phase**: Phase 2 - MCP Servers Implementation
