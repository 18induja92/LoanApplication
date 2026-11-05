# GEN-AI Case Study – Executive Summary Report

---

## Details of Submission

| Field | Details |
|---|---|
| **Participant** | Induja Sivaraj |
| **Case Study** | Agentic AI Intelligent Loan Approval System |
| **Date** | November 5, 2026 |
| **Overall Score** | 7 / 10 |
| **Grade** | Good |
| **Status** | Pass (with recommended improvements) |

---

## Step 1: Submission Completeness Check

| Required Component | Status | Evidence |
|---|---|---|
| Business understanding of loan approval problem | ✅ Present | Clear problem decomposition into 4 agent domains; business rules encoded in MCP servers |
| Multi-agent / Agentic AI architecture | ✅ Present | 4 specialized agents with tool-use loop; Claude SDK agentic loops |
| Streamlit-based chatbot UI | ✅ Present | `frontend/streamlit_app.py` – 4-page application |
| FastAPI-based microservice layer | ✅ Present | `services/microservice_api.py` – 6 REST endpoints |
| LangGraph-based orchestration | ⚠️ Partial | File named `orchestration/langgraph_engine.py` but true LangGraph StateGraph not implemented |
| MCP-based agent communication | ⚠️ Partial | FastMCP library used with `@mcp.tool()` decorators, but servers run embedded (not as independent processes with MCP transport) |
| Applicant Profile Agent | ✅ Present | `agents/applicant_profile_agent.py` – all 4 expected outputs present |
| Financial Risk Analysis Agent | ✅ Present | `agents/financial_risk_agent.py` – all 5 expected outputs present |
| Loan Decision Agent | ✅ Present | `agents/loan_decision_agent.py` – classification, risk score, confidence, factors, explanation |
| Compliance & Action Orchestrator Agent | ✅ Present | `agents/compliance_agent.py` – case ID, notification, audit trail |
| End-to-end workflow | ✅ Present | Functional pipeline from UI → API → Orchestrator → 4 Agents → DB |
| Technology stack | ✅ Present | Streamlit, FastAPI, FastMCP, Anthropic SDK, SQLite, Pydantic |
| Explainability / Auditable decision output | ✅ Present | Risk score, confidence, key factors, reasoning, case records |
| Live walkthrough readiness | ✅ Present | Fully working running system with real API calls |

**Completeness Verdict:** Submission is sufficiently complete to proceed with detailed evaluation. Two components (LangGraph and MCP transport) are present but not fully implemented to their intended specification.

---

## Evaluation Summary Table

| Submission Complete | Business Understanding | Architecture Quality | Agent Design Quality | Workflow Clarity | Explainability & Auditability | Implementation Readiness | Score (out of 10) | Key Remarks |
|---|---|---|---|---|---|---|---|---|
| Yes (with partial gaps) | Strong | Good | Strong | Good | Good | Strong | **7 / 10** | Fully functional working system. LangGraph used in name only; MCP servers embedded rather than independent. All 4 agents correctly designed and operational. |

---

## Step 2: Detailed Dimension-by-Dimension Evaluation

---

### 1. Business Understanding & Alignment

**Score Assessment: Strong**

The participant demonstrates clear understanding of the loan approval business domain:

- **Problem Decomposition**: The application correctly separates loan evaluation into four distinct business concerns — applicant profiling, financial risk, decision synthesis, and compliance — closely mirroring how real-world loan processing departments operate.
- **Risk Business Rules**: The `mcp_servers/risk_rules_server.py` encodes concrete risk thresholds in `config/settings.py`: `MIN_CREDIT_SCORE = 600`, `MAX_DTI_RATIO = 0.45`, `MIN_INCOME = 30000`. These reflect realistic banking norms.
- **Decision Classifications**: The system correctly implements three loan outcomes — APPROVED, REJECTED, and MANUAL REVIEW — which aligns with actual lending practice, including a risk band for borderline cases.
- **Compliance Awareness**: The `notification_server.py` includes 7-year record retention (`retention_days=2555`), referencing regulatory best practice.
- **Applicant Diversity**: The 10 pre-populated test applicants (APP-001 to APP-010) are thoughtfully designed to trigger all three decision paths, demonstrating awareness of testing boundary conditions.

**Gap Identified:** The business rules are hardcoded in the MCP server and settings file. A production-grade system would benefit from externalising these thresholds into a configurable rules engine or database table.

---

### 2. Agentic AI Architecture & Design

**Score Assessment: Good**

The architecture demonstrates solid understanding of multi-agent design principles:

**Strengths:**
- Clear separation of agent responsibilities with no overlap between agents.
- Each agent is a self-contained module with its own system prompt, tool definitions, and agentic loop.
- MCP servers serve as tool providers for each agent domain — a correct architectural decision.
- The orchestrator (`LoanApprovalOrchestrator`) correctly maintains application state via the `ApplicationState` dataclass and passes context forward through the pipeline.
- Pydantic models (`services/models.py`) enforce strong typing at API boundaries.

**Gaps Identified:**
1. **LangGraph is not truly utilised.** The file `orchestration/langgraph_engine.py` uses a manually coded sequential Python orchestration pattern. True LangGraph requires a `StateGraph` with nodes and edges, conditional routing, and compiled graph execution. The current orchestrator is equivalent to a standard sequential function pipeline, not a LangGraph-native solution.
2. **Agent parallelism is not explored.** The ApplicantProfile and FinancialRisk agents are independent of each other and could run concurrently, but the current design runs them sequentially — a missed architectural optimisation.
3. **No explicit feedback loop.** The architecture does not define any agent re-invocation or iterative refinement when a REVIEW decision is made.

---

### 3. Orchestration & Workflow Quality

**Score Assessment: Good**

The orchestration flow is logically structured and correct:

```
UI Form Submission
    → FastAPI POST /apply
    → DatabaseManager.create_application()
    → LoanApprovalOrchestrator.process_application()
        → ApplicantProfileAgent (tools: 5 ApplicantDB MCP tools)
        → FinancialRiskAgent (tools: 5 RiskRules MCP tools)
        → LoanDecisionAgent (tools: DecisionSynthesis MCP tools)
        → ComplianceAgent (tools: 5 NotificationSystem MCP tools)
    → DatabaseManager.create_decision()
    → API returns application_id
    → UI polls /status and /decision endpoints
```

**Strengths:**
- State is passed correctly between agents via the `ApplicationState` object.
- Errors at any stage are captured in `state.errors` and logged without crashing the pipeline.
- The orchestrator correctly uses the user-provided `applicant_id` for profile lookup (after a fix applied during implementation), not the system-generated `application_id`.

**Gaps Identified:**
1. **No conditional routing in orchestration.** The pipeline always runs all 4 agents. A more advanced design would skip agents or route differently based on intermediate decisions (e.g., if the credit score is below 500, skip detailed synthesis and reject immediately).
2. **Manual review workflow incomplete.** The system classifies applications as REVIEW but does not define what happens next — there is no human review queue, no escalation path, and no re-submission mechanism for borderline cases.
3. **LangGraph state graph not compiled.** The import of `langgraph` in requirements is present, but no `StateGraph.compile()` is used, which means the LangGraph dependency is non-functional.

---

### 4. Agent Responsibilities & MCP Usage

**Score Assessment: Strong**

All four agents are correctly designed and implement the expected domain outputs:

#### Applicant Profile Agent (`agents/applicant_profile_agent.py`)
| Expected Output | Implemented | Notes |
|---|---|---|
| Income stability score (0–1) | ✅ | `calculate_income_stability()` in MCP server |
| Employment risk (LOW/MEDIUM/HIGH) | ✅ | `assess_employment_risk()` with tenure and type logic |
| Credit history summary | ✅ | `get_credit_history()` returns structured summary |
| Application completeness flags | ✅ | `check_application_completeness()` validates all required fields |

#### Financial Risk Analysis Agent (`agents/financial_risk_agent.py`)
| Expected Output | Implemented | Notes |
|---|---|---|
| Debt-to-income ratio | ✅ | `calculate_debt_to_income_ratio()` – current + with new loan |
| Credit score risk level | ✅ | `assess_credit_score_risk()` with tiered scoring |
| Loan amount risk | ✅ | `assess_loan_amount_risk()` based on income multiples |
| Anomaly detection | ✅ | `detect_anomalies()` – 7 anomaly types |
| Reasoning | ✅ | Narrative generated by Claude from tool results |

#### Loan Decision Agent (`agents/loan_decision_agent.py`)
| Expected Output | Implemented | Notes |
|---|---|---|
| Classification (Approve/Reject/Review) | ✅ | `synthesize_decision()` in MCP server |
| Risk score | ✅ | Weighted risk scoring algorithm |
| Confidence level | ✅ | Confidence bands based on risk distance from thresholds |
| Key decision factors | ✅ | `extract_key_factors()` – positive and negative factors |
| Explanation | ✅ | `generate_explanation()` returns business-readable text |

#### Compliance & Action Orchestrator Agent (`agents/compliance_agent.py`)
| Expected Output | Implemented | Notes |
|---|---|---|
| Action taken | ✅ | `log_agent_action()` records each agent step |
| Notification sent | ✅ | `generate_notification()` produces applicant-facing message |
| Case ID | ✅ | `CASE-2026-XXXXXXXX` format via UUID |
| Timestamp | ✅ | ISO format timestamps on all records |
| Summary | ✅ | Compliance record created with full decision summary |

**MCP Usage Assessment:**
- FastMCP 4.1.6 is installed and `@mcp.tool()` decorators are correctly applied to all tool functions across 4 MCP server files.
- **Gap**: The MCP servers are not running as independent network processes. They are imported as Python modules directly within the agent code. True MCP usage requires the servers to run as separate processes (stdio or HTTP transport) with an MCP client connecting to them. The current design is functionally equivalent but does not demonstrate the network-separated, protocol-compliant MCP architecture as defined in the MCP specification.

---

### 5. Technology Stack & Implementation Relevance

**Score Assessment: Good**

| Technology | Used | Correctness of Usage |
|---|---|---|
| **Streamlit** | ✅ | 4-page app with session state, form handling, custom CSS |
| **FastAPI** | ✅ | 6 endpoints, Pydantic models, CORS, exception handlers |
| **LangGraph** | ⚠️ | Imported but not used as StateGraph — sequential Python used instead |
| **LangChain** | ⚠️ | Listed in requirements.txt but no LangChain usage found in code |
| **FastMCP** | ✅ | Installed, `@mcp.tool()` decorators applied, `FastMCP()` instances created |
| **Anthropic Agent SDK** | ✅ | `anthropic.Anthropic()` client used; tool_use/tool_result cycle correct |
| **Prompt Engineering** | ✅ | Specialised system prompts per agent with clear role and output instructions |
| **Python** | ✅ | Clean Python 3.12 code with type hints and logging |
| **Claude / LLM** | ✅ | Haiku model (due to API key constraints); correct messages API usage |
| **SQLite3** | ✅ | 3-table schema, parameterised queries, indexed foreign keys |
| **Pydantic** | ✅ | Full request/response model validation including enums |

**Note on Model Selection:** The implementation uses `global.anthropic.claude-haiku-4-5-20251001-v1:0` due to API key access limitations in the test environment. The system was architected for Claude Sonnet 4.6 and the code is correct — the model substitution is an operational constraint, not a design flaw.

---

### 6. Decision Quality, Explainability & Auditability

**Score Assessment: Good**

**Strengths:**
- Every loan decision returns: `classification`, `risk_score` (0–1 scale), `confidence_level`, `key_decision_factors` (list), and `reasoning` (natural language).
- The `generate_explanation()` function in the DecisionSynthesis MCP server produces business-readable, non-technical explanations tailored to each classification outcome.
- Compliance records include case IDs, timestamps, decision factors, and are logged to both the in-memory audit trail and the SQLite `audit_logs` table.
- The Streamlit Decision page renders all decision fields and provides a JSON download for record-keeping.
- Risk score thresholds are documented: APPROVED < 0.25, REVIEW 0.25–0.85, REJECTED > 0.85.

**Gaps Identified:**
1. **Manual Review cases lack a downstream workflow.** When `classification = REVIEW`, the system terminates without defining what manual review entails — who receives the case, on what interface, and how a human overrides the system decision.
2. **No rejection justification in regulatory format.** In regulated lending, rejections require an Adverse Action Notice. The current notification is informative but not structured to regulatory standards (e.g., ECOA, FCRA).
3. **Audit log stored in memory in notification_server.py.** The `AUDIT_LOG` list in the notification server is in-memory and does not persist to the SQLite database on its own. The orchestrator does write to the SQLite `audit_logs` table separately, but the two stores are not synchronised.

---

### 7. Code / Implementation Readiness

**Score Assessment: Strong**

This is a fully operational, running implementation — not a theoretical design:

- ✅ FastAPI server runs and processes requests
- ✅ Streamlit UI renders forms and displays decisions
- ✅ All 4 agents execute agentic loops with real Claude API calls
- ✅ SQLite database stores applications, decisions, and audit logs
- ✅ MCP tool functions execute correctly and return structured results
- ✅ Tool-use / tool-result cycle correctly handled per Anthropic SDK spec
- ✅ Error handling at API, orchestrator, and agent levels
- ✅ Environment variable management via `.env` and `python-dotenv`
- ✅ Logging to console and file (`logs/app.log`)

The code demonstrates clean structure, proper use of Python type hints, and consistent naming conventions. The implementation is walkthrough-ready.

---

## Evaluation Summary Table (Final)

| Dimension | Rating | Score Weight | Evidence |
|---|---|---|---|
| Business Understanding | Strong | High | Correct domain decomposition, business rules, compliance awareness |
| Architecture Quality | Good | High | Modular agents, MCP design correct but not transport-separated |
| Orchestration & Workflow | Good | Medium | Functional pipeline; LangGraph not truly used |
| Agent Design Quality | Strong | High | All 4 agents with all expected outputs correctly implemented |
| Technology Stack | Good | Medium | Most technologies correctly used; LangGraph gap significant |
| Explainability & Auditability | Good | High | Risk scores, reasoning, case IDs present; manual review path incomplete |
| Implementation Readiness | Strong | High | Fully working system with real LLM calls |

---

## Final Recommendations for Participant

### Strengths to Highlight

1. **Complete End-to-End Implementation** — The submission is not theoretical; it is a working system with a running API, functional UI, real Claude API calls, and persistent database storage. This is a significant achievement.

2. **Correct Agent Architecture** — All four agents are correctly designed with appropriate specialisation, dedicated MCP tool servers, and proper tool-use agentic loops using the Anthropic SDK.

3. **Strong Business Alignment** — The system encodes realistic banking risk rules (DTI ratios, credit score thresholds, anomaly detection), demonstrates knowledge of compliance requirements (7-year retention), and covers all three loan decision paths.

4. **Pydantic Model Design** — The use of Pydantic v2 models for request/response validation, including enums for `EmploymentType`, `ApplicationStatus`, and `Classification`, reflects production-grade API design discipline.

5. **Prompt Engineering Quality** — Each agent has a differentiated, detailed system prompt that correctly frames the agent's role, responsibilities, and expected output format.

6. **Fallback Data Handling** — The implementation of a fallback mechanism (using submitted application data when an applicant is not found in the database) shows good defensive design thinking.

---

### Areas for Improvement

1. **Implement True LangGraph StateGraph**
   - Replace the manual sequential orchestration with a compiled LangGraph `StateGraph`
   - Define nodes for each agent, edges for flow control, and conditional routing
   - Example: If credit score < 500 in the profile stage, add an edge that routes directly to rejection without running all agents
   - This is the most significant gap relative to the stated technology requirements

2. **Use MCP with Proper Transport Protocol**
   - Start MCP servers as independent processes (stdio or HTTP)
   - Use `fastmcp.Client` or the MCP SDK client to connect agents to servers over the protocol
   - This demonstrates true service-oriented MCP usage rather than embedded imports

3. **Define Manual Review Workflow**
   - Add a review queue endpoint (`GET /review-queue`) to list REVIEW-classified applications
   - Add a human override endpoint (`POST /override/{application_id}`) to approve or reject manually
   - Implement a Streamlit "Review Queue" page for human-in-the-loop processing

4. **Synchronise In-Memory and Persistent Audit Logs**
   - Ensure the `AUDIT_LOG` list in `notification_server.py` writes to the SQLite `audit_logs` table
   - Currently two separate audit mechanisms exist; they should be unified

5. **Externalise Business Rules**
   - Move risk thresholds out of `config/settings.py` into a database-driven rules table
   - This enables dynamic rule updates without code redeployment

6. **Add Parallel Agent Execution**
   - Run `ApplicantProfileAgent` and `FinancialRiskAgent` concurrently using `asyncio.gather()` or LangGraph parallel nodes
   - This would reduce total processing time by ~50%

---

### Learning Outcomes Demonstrated

The participant has demonstrated mastery of the following:
- ✅ Agentic AI design patterns — tool use loops, multi-step reasoning, agent specialisation
- ✅ Anthropic Claude SDK — correct messages API usage, tool definitions, tool_use/tool_result handling
- ✅ REST API design with FastAPI — endpoint design, Pydantic validation, error handling, CORS
- ✅ Streamlit multi-page application development
- ✅ SQLite database management — schema design, parameterised queries, CRUD operations
- ✅ FastMCP tool server design — `@mcp.tool()` decorators, structured outputs
- ✅ Prompt engineering — specialised system prompts for distinct agent roles
- ✅ Software engineering practices — modular design, environment configuration, logging, type hints

---

### Final Verdict on Solution Quality

**Induja Sivaraj** has submitted a technically solid, end-to-end working implementation of the Agentic AI Intelligent Loan Approval System. The submission clearly demonstrates a strong grasp of multi-agent architecture, the Anthropic Claude SDK, and the full technology stack required.

The primary gap is the non-use of LangGraph as a state graph framework — the file is named correctly but the internal implementation uses manual Python orchestration. The MCP usage, while functionally correct, does not demonstrate the protocol-separated server architecture intended by the MCP specification.

These are architectural gaps rather than implementation failures, and the system works correctly in its current form. With the recommended improvements — particularly the LangGraph StateGraph implementation and true MCP transport separation — this submission would score in the 9–10 range.

**Current Score: 7/10 — GOOD — PASS**

---

*Evaluation conducted by: Senior GenAI Solution Reviewer*
*Evaluation framework: GEN-AI Case Study Evaluator Prompt v1.0*
*Date: November 5, 2026*
