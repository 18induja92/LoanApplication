"""
ApplicantDB MCP Server
Provides tools for querying applicant profiles and assessing creditworthiness
"""

import json
import logging
from typing import Any, Dict
from pydantic import BaseModel, Field
from fastmcp.server import FastMCP

logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = FastMCP("applicant-db", instructions="Provides tools for querying applicant profiles and creditworthiness")

# Mock applicant database - 10 diverse applicants for testing all scenarios
APPLICANT_DATABASE = {
    # APPROVED: Excellent profile
    "APP-001": {
        "applicant_id": "APP-001",
        "name": "John Doe",
        "age": 35,
        "income": 120000,
        "employment_type": "FULL_TIME",
        "employment_duration_years": 10,
        "credit_score": 800,
        "credit_history": "Excellent payment history with 20 years of credit. No late payments. Perfect record.",
        "existing_liabilities": 30000,
        "location": "NEW_YORK",
        "application_timestamp": "2026-11-03T10:00:00Z",
    },
    # APPROVED: Good profile, stable income
    "APP-002": {
        "applicant_id": "APP-002",
        "name": "Jane Smith",
        "age": 28,
        "income": 85000,
        "employment_type": "FULL_TIME",
        "employment_duration_years": 6,
        "credit_score": 750,
        "credit_history": "Good payment history. No late payments in past 5 years.",
        "existing_liabilities": 25000,
        "location": "CALIFORNIA",
        "application_timestamp": "2026-11-03T10:15:00Z",
    },
    # APPROVED: Solid middle-income profile
    "APP-003": {
        "applicant_id": "APP-003",
        "name": "Robert Johnson",
        "age": 42,
        "income": 95000,
        "employment_type": "FULL_TIME",
        "employment_duration_years": 12,
        "credit_score": 720,
        "credit_history": "Consistent payment history. Responsible credit user.",
        "existing_liabilities": 45000,
        "location": "TEXAS",
        "application_timestamp": "2026-11-03T10:30:00Z",
    },
    # MANUAL REVIEW: Self-employed, variable income
    "APP-004": {
        "applicant_id": "APP-004",
        "name": "Maria Garcia",
        "age": 31,
        "income": 70000,
        "employment_type": "SELF_EMPLOYED",
        "employment_duration_years": 4,
        "credit_score": 680,
        "credit_history": "Good history. Self-employed 4 years, income can vary seasonally.",
        "existing_liabilities": 50000,
        "location": "FLORIDA",
        "application_timestamp": "2026-11-03T10:45:00Z",
    },
    # MANUAL REVIEW: Fair credit, moderate DTI
    "APP-005": {
        "applicant_id": "APP-005",
        "name": "Michael Chen",
        "age": 40,
        "income": 65000,
        "employment_type": "FULL_TIME",
        "employment_duration_years": 3,
        "credit_score": 640,
        "credit_history": "Fair payment history. Two late payments 3 years ago, now on track.",
        "existing_liabilities": 55000,
        "location": "SEATTLE",
        "application_timestamp": "2026-11-03T11:00:00Z",
    },
    # REJECTED: Poor credit, high debt
    "APP-006": {
        "applicant_id": "APP-006",
        "name": "Sarah Williams",
        "age": 26,
        "income": 35000,
        "employment_type": "PART_TIME",
        "employment_duration_years": 1,
        "credit_score": 560,
        "credit_history": "Poor payment history. Multiple late payments. High credit utilization.",
        "existing_liabilities": 80000,
        "location": "BOSTON",
        "application_timestamp": "2026-11-03T11:15:00Z",
    },
    # REJECTED: Very poor credit, unstable employment
    "APP-007": {
        "applicant_id": "APP-007",
        "name": "David Brown",
        "age": 52,
        "income": 45000,
        "employment_type": "PART_TIME",
        "employment_duration_years": 0.5,
        "credit_score": 520,
        "credit_history": "Very poor. Bankruptcy 5 years ago. Recent defaults. High risk.",
        "existing_liabilities": 95000,
        "location": "CHICAGO",
        "application_timestamp": "2026-11-03T11:30:00Z",
    },
    # MANUAL REVIEW: Recent graduate, limited history but good metrics
    "APP-008": {
        "applicant_id": "APP-008",
        "name": "Emily Davis",
        "age": 24,
        "income": 55000,
        "employment_type": "FULL_TIME",
        "employment_duration_years": 1.5,
        "credit_score": 670,
        "credit_history": "New to credit. Limited history but all on-time payments so far.",
        "existing_liabilities": 15000,
        "location": "DENVER",
        "application_timestamp": "2026-11-03T11:45:00Z",
    },
    # APPROVED: Excellent all metrics
    "APP-009": {
        "applicant_id": "APP-009",
        "name": "Jennifer Lee",
        "age": 38,
        "income": 150000,
        "employment_type": "FULL_TIME",
        "employment_duration_years": 14,
        "credit_score": 820,
        "credit_history": "Exceptional. 25 years credit history. Perfect payment record. Low utilization.",
        "existing_liabilities": 20000,
        "location": "SAN_FRANCISCO",
        "application_timestamp": "2026-11-03T12:00:00Z",
    },
    # MANUAL REVIEW: Mixed indicators - good credit but high debt burden
    "APP-010": {
        "applicant_id": "APP-010",
        "name": "Thomas Martinez",
        "age": 45,
        "income": 88000,
        "employment_type": "FULL_TIME",
        "employment_duration_years": 8,
        "credit_score": 710,
        "credit_history": "Good credit. Excellent payment history but carrying significant debt load.",
        "existing_liabilities": 120000,
        "location": "ATLANTA",
        "application_timestamp": "2026-11-03T12:15:00Z",
    },
}


class GetApplicantProfileInput(BaseModel):
    """Input for get_applicant_profile tool"""

    applicant_id: str = Field(..., description="Unique applicant identifier")


class CalculateIncomeStabilityInput(BaseModel):
    """Input for calculate_income_stability tool"""

    applicant_id: str = Field(..., description="Unique applicant identifier")
    income: float = Field(..., description="Annual income")
    employment_duration_years: int = Field(..., description="Years in current employment")


class AssessEmploymentRiskInput(BaseModel):
    """Input for assess_employment_risk tool"""

    employment_type: str = Field(..., description="Type of employment (FULL_TIME, PART_TIME, SELF_EMPLOYED)")
    employment_duration_years: int = Field(..., description="Years in current employment")


class GetCreditHistoryInput(BaseModel):
    """Input for get_credit_history tool"""

    applicant_id: str = Field(..., description="Unique applicant identifier")


class CheckApplicationCompletenessInput(BaseModel):
    """Input for check_application_completeness tool"""

    applicant_data: Dict[str, Any] = Field(..., description="Application data to validate")


@mcp.tool()
def get_applicant_profile(applicant_id: str, applicant_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """Retrieve applicant profile from database or use submitted application data"""
    if applicant_id in APPLICANT_DATABASE:
        return {
            "status": "success",
            "data": APPLICANT_DATABASE[applicant_id],
            "source": "database"
        }

    # Fallback: if applicant not in database but application data provided, use that
    if applicant_data:
        return {
            "status": "success",
            "data": applicant_data,
            "source": "application_submission"
        }

    return {
        "status": "error",
        "message": f"Applicant {applicant_id} not found in database and no application data provided",
    }


@mcp.tool()
def calculate_income_stability(
    applicant_id: str, income: float, employment_duration_years: int
) -> Dict[str, Any]:
    """Calculate income stability score (0-1)"""
    score = 0.5

    # Base on employment duration
    if employment_duration_years >= 10:
        score += 0.25
    elif employment_duration_years >= 5:
        score += 0.15
    elif employment_duration_years >= 2:
        score += 0.05

    # Base on income level
    if income >= 80000:
        score += 0.15
    elif income >= 50000:
        score += 0.10
    elif income >= 30000:
        score += 0.05

    # Get applicant type for additional adjustment
    applicant = APPLICANT_DATABASE.get(applicant_id)
    if applicant:
        if applicant["employment_type"] == "SELF_EMPLOYED":
            score -= 0.1
        elif applicant["employment_type"] == "PART_TIME":
            score -= 0.05

    # Clamp to 0-1
    score = max(0.0, min(1.0, score))

    return {
        "status": "success",
        "income_stability_score": round(score, 2),
        "reasoning": f"Score based on {employment_duration_years} years employment and ${income} income",
    }


@mcp.tool()
def assess_employment_risk(employment_type: str, employment_duration_years: int) -> Dict[str, Any]:
    """Assess employment risk level"""
    risk = "MEDIUM"

    if employment_type == "FULL_TIME" and employment_duration_years >= 5:
        risk = "LOW"
    elif employment_type == "FULL_TIME" and employment_duration_years >= 2:
        risk = "MEDIUM"
    elif employment_type == "FULL_TIME":
        risk = "HIGH"
    elif employment_type == "SELF_EMPLOYED":
        risk = "MEDIUM" if employment_duration_years >= 5 else "HIGH"
    elif employment_type == "PART_TIME":
        risk = "HIGH"

    return {
        "status": "success",
        "employment_risk": risk,
        "employment_type": employment_type,
        "employment_duration_years": employment_duration_years,
    }


@mcp.tool()
def get_credit_history(applicant_id: str) -> Dict[str, Any]:
    """Retrieve credit history summary"""
    applicant = APPLICANT_DATABASE.get(applicant_id)
    if not applicant:
        return {
            "status": "error",
            "message": f"Applicant {applicant_id} not found",
        }

    return {
        "status": "success",
        "credit_score": applicant["credit_score"],
        "credit_history_summary": applicant["credit_history"],
        "recommendation": "Good" if applicant["credit_score"] >= 700 else "Fair" if applicant["credit_score"] >= 650 else "Poor",
    }


@mcp.tool()
def check_application_completeness(applicant_data: Dict[str, Any]) -> Dict[str, Any]:
    """Check if application has all required fields"""
    required_fields = [
        "applicant_id",
        "age",
        "income",
        "employment_type",
        "credit_score",
        "loan_amount",
        "tenure_months",
        "existing_liabilities",
        "location",
    ]

    missing_fields = [field for field in required_fields if field not in applicant_data or applicant_data[field] is None]

    flags = []
    if missing_fields:
        flags.append(f"Missing fields: {', '.join(missing_fields)}")

    # Check for unusual values
    age = applicant_data.get("age")
    if age and (age < 18 or age > 100):
        flags.append("Age outside acceptable range")

    income = applicant_data.get("income")
    if income and income < 0:
        flags.append("Negative income value")

    credit_score = applicant_data.get("credit_score")
    if credit_score and (credit_score < 300 or credit_score > 850):
        flags.append("Credit score outside valid range (300-850)")

    return {
        "status": "success",
        "is_complete": len(missing_fields) == 0 and len(flags) == 0,
        "completeness_flags": flags,
        "missing_fields": missing_fields,
    }
