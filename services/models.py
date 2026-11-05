from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class EmploymentType(str, Enum):
    """Employment type enumeration"""
    FULL_TIME = "FULL_TIME"
    PART_TIME = "PART_TIME"
    SELF_EMPLOYED = "SELF_EMPLOYED"
    UNEMPLOYED = "UNEMPLOYED"


class ApplicationStatus(str, Enum):
    """Application status enumeration"""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Classification(str, Enum):
    """Loan decision classification"""
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    REVIEW = "REVIEW"


# Request/Input Models
class LoanApplicationRequest(BaseModel):
    """Loan application request model"""
    applicant_id: str = Field(..., description="Unique applicant identifier")
    age: int = Field(..., ge=18, le=100, description="Applicant age")
    income: float = Field(..., gt=0, description="Annual income in dollars")
    employment_type: EmploymentType = Field(..., description="Type of employment")
    credit_score: int = Field(..., ge=300, le=850, description="Credit score (300-850)")
    loan_amount: float = Field(..., gt=0, description="Requested loan amount")
    tenure_months: int = Field(..., gt=0, description="Loan tenure in months")
    existing_liabilities: float = Field(default=0, ge=0, description="Existing debts")
    location: str = Field(..., description="Geographic location")
    application_timestamp: Optional[datetime] = Field(
        default_factory=datetime.now,
        description="Application submission timestamp"
    )

    class Config:
        json_schema_extra = {
            "example": {
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
        }


class ApplicationStatusResponse(BaseModel):
    """Application status response"""
    application_id: str
    status: ApplicationStatus
    estimated_completion: Optional[datetime] = None


class DecisionResponse(BaseModel):
    """Loan decision response"""
    application_id: str
    classification: Classification
    risk_score: float = Field(..., ge=0, le=1, description="Risk score (0-1)")
    confidence_level: float = Field(..., ge=0, le=1, description="Confidence level (0-1)")
    key_decision_factors: List[str]
    reasoning: str
    timestamp: datetime = Field(default_factory=datetime.now)


# Agent Response Models
class ApplicantProfileAgentOutput(BaseModel):
    """Output from Applicant Profile Agent"""
    income_stability_score: float = Field(..., ge=0, le=1)
    employment_risk: str = Field(..., description="LOW, MEDIUM, HIGH")
    credit_history_summary: str
    completeness_flags: List[str] = []
    additional_notes: Optional[str] = None


class FinancialRiskAgentOutput(BaseModel):
    """Output from Financial Risk Analysis Agent"""
    debt_to_income_ratio: float
    credit_score_risk: str = Field(..., description="LOW, MEDIUM, HIGH")
    loan_amount_risk: str = Field(..., description="LOW, MEDIUM, HIGH")
    anomalies_detected: List[str] = []
    reasoning: str


class LoanDecisionAgentOutput(BaseModel):
    """Output from Loan Decision Agent"""
    classification: Classification
    risk_score: float = Field(..., ge=0, le=1)
    confidence_level: float = Field(..., ge=0, le=1)
    key_decision_factors: List[str]
    explanation: str


class ComplianceAgentOutput(BaseModel):
    """Output from Compliance & Action Agent"""
    action_taken: str
    notification_sent: bool
    case_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    summary: str


# Orchestrator State Models
class AgentAnalysis(BaseModel):
    """Analysis results from all agents"""
    applicant_profile: Optional[ApplicantProfileAgentOutput] = None
    financial_risk: Optional[FinancialRiskAgentOutput] = None
    loan_decision: Optional[LoanDecisionAgentOutput] = None
    compliance: Optional[ComplianceAgentOutput] = None


class OrchestratorState(BaseModel):
    """State of the orchestration engine"""
    application_id: str
    applicant_data: LoanApplicationRequest
    agent_analysis: AgentAnalysis = Field(default_factory=AgentAnalysis)
    final_decision: Optional[LoanDecisionAgentOutput] = None
    case_id: Optional[str] = None
    status: ApplicationStatus = ApplicationStatus.PENDING
    errors: List[str] = []
    created_at: datetime = Field(default_factory=datetime.now)


# Database Models (for internal use)
class ApplicationRecord(BaseModel):
    """Application database record"""
    id: str
    applicant_id: str
    age: int
    income: float
    employment_type: str
    credit_score: int
    loan_amount: float
    tenure_months: int
    existing_liabilities: float
    location: str
    application_timestamp: datetime
    status: str
    created_at: datetime


class DecisionRecord(BaseModel):
    """Decision database record"""
    id: str
    application_id: str
    classification: str
    risk_score: float
    confidence_level: float
    reasoning: str
    key_decision_factors: str  # JSON string
    created_at: datetime


class AuditLogRecord(BaseModel):
    """Audit log database record"""
    id: str
    case_id: Optional[str]
    application_id: Optional[str]
    agent_name: str
    action: str
    details: Optional[str]  # JSON string
    timestamp: datetime
