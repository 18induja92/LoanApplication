# Quick Start Guide

Get the loan approval system up and running in 5 minutes!

## Prerequisites
- Python 3.x installed
- Anthropic API key (from https://console.anthropic.com)

## Setup (One-time)

### 1. Create Virtual Environment
```bash
cd /home/ubuntu/Desktop/demo
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API Key
```bash
# Copy the template
cp .env.example .env

# Edit .env and add your API key
# ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
```

### 4. Initialize Database
```bash
python3 init_db.py
```

You should see:
```
✓ Database initialized successfully
Database Health: healthy
Tables: applications, decisions, audit_logs
✓ Database setup complete!
```

## Running the Application (Phases 2-3)

Once agents and API are implemented:

### Start API Server
```bash
uvicorn services.microservice_api:app --reload --host 0.0.0.0 --port 8000
```

### Start Streamlit UI
```bash
streamlit run frontend/streamlit_app.py
```

## Testing Database Setup

```python
from database import DatabaseManager
from config.settings import DATABASE_PATH

# Initialize
db = DatabaseManager(DATABASE_PATH)

# Create a test application
app_id = db.create_application({
    "applicant_id": "TEST-001",
    "age": 35,
    "income": 75000,
    "employment_type": "FULL_TIME",
    "credit_score": 750,
    "loan_amount": 250000,
    "tenure_months": 360,
    "existing_liabilities": 50000,
    "location": "NEW_YORK"
})

print(f"Created application: {app_id}")

# Get statistics
stats = db.get_statistics()
print(f"Statistics: {stats}")
```

## Project Status

**Phase 1**: ✅ Complete
- [x] Foundation setup
- [x] Database configured
- [x] Models created

**Phase 2**: ⏳ Upcoming
- [ ] MCP Servers implementation
- [ ] Agent framework setup

**Phase 3**: ⏳ Upcoming
- [ ] FastAPI microservice
- [ ] Streamlit UI

**Phase 4**: ⏳ Upcoming
- [ ] Testing & integration
- [ ] Documentation

## Important Files

- `CAPSTONE_PLAN.md` - Complete project plan
- `PHASE1_COMPLETE.md` - Phase 1 details
- `README.md` - Full documentation
- `.env.example` - Configuration template
- `requirements.txt` - Dependencies

## Environment Variables

Essential variables in `.env`:

```env
ANTHROPIC_API_KEY=your_key_here
DATABASE_PATH=data/loan_approval.db
LLM_MODEL=claude-sonnet-4-6
API_HOST=127.0.0.1
API_PORT=8000
```

## Troubleshooting

### ModuleNotFoundError
```bash
# Make sure virtual environment is activated
source venv/bin/activate
```

### Database Error
```bash
# Reinitialize database
python3 init_db.py
```

### API Key Error
```bash
# Check .env file has correct key
cat .env | grep ANTHROPIC_API_KEY

# If missing, add it
echo "ANTHROPIC_API_KEY=your_key_here" >> .env
```

## Next Steps

1. ✅ Complete Phase 1 setup (you are here)
2. ⏳ Start Phase 2: MCP Servers
3. ⏳ Start Phase 3: API & UI
4. ⏳ Testing & Deployment

---

**Ready?** Let's proceed with Phase 2! 🚀
