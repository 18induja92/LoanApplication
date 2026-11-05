"""
RiskRulesDB MCP Server
Applies business rules and detects financial anomalies
"""

import json
import logging
from typing import Any, Dict, List
from fastmcp.server import FastMCP

logger = logging.getLogger(__name__)

# Initialize MCP server - stores compliance and risk rules
mcp = FastMCP("risk-rules-db", instructions="Applies business rules, detects anomalies, and calculates financial risk metrics")


@mcp.tool()
def calculate_debt_to_income_ratio(monthly_income: float, monthly_debt: float) -> float:
    """Calculate debt-to-income ratio"""
    if monthly_income <= 0:
        return 0.0
    return round(monthly_debt / monthly_income, 3)


@mcp.tool()
def assess_credit_score_risk(credit_score: int) -> Dict[str, Any]:
    """Assess risk level based on credit score"""
    if credit_score >= 750:
        risk = "LOW"
        risk_multiplier = 0.8
    elif credit_score >= 700:
        risk = "MEDIUM"
        risk_multiplier = 1.0
    elif credit_score >= 650:
        risk = "MEDIUM"
        risk_multiplier = 1.2
    elif credit_score >= 600:
        risk = "HIGH"
        risk_multiplier = 1.5
    else:
        risk = "VERY_HIGH"
        risk_multiplier = 2.0

    return {
        "credit_score_risk": risk,
        "risk_multiplier": risk_multiplier,
        "score": credit_score,
    }


@mcp.tool()
def assess_loan_amount_risk(
    loan_amount: float, income: float, existing_liabilities: float
) -> Dict[str, Any]:
    """Assess risk based on loan amount and financial capacity"""
    annual_income = income
    monthly_income = annual_income / 12

    # Calculate loan-to-income ratio
    loan_to_income = loan_amount / annual_income if annual_income > 0 else 0

    risk = "MEDIUM"
    reasoning = ""

    if loan_to_income <= 2.0:
        risk = "LOW"
        reasoning = "Loan is reasonable relative to income (< 2x annual)"
    elif loan_to_income <= 3.5:
        risk = "MEDIUM"
        reasoning = "Loan is moderate relative to income (2-3.5x annual)"
    elif loan_to_income <= 5.0:
        risk = "HIGH"
        reasoning = "Loan is high relative to income (3.5-5x annual)"
    else:
        risk = "VERY_HIGH"
        reasoning = "Loan exceeds safe limits relative to income (> 5x annual)"

    return {
        "loan_amount_risk": risk,
        "loan_to_income_ratio": round(loan_to_income, 2),
        "reasoning": reasoning,
    }


@mcp.tool()
def detect_anomalies(applicant_data: Dict[str, Any]) -> List[str]:
    """Detect anomalies in application data"""
    anomalies = []

    # Age check
    age = applicant_data.get("age", 0)
    if age < 25:
        anomalies.append("Applicant is under 25 (younger borrowers higher risk)")
    if age > 65:
        anomalies.append("Applicant is over 65 (near retirement)")

    # Income check
    income = applicant_data.get("income", 0)
    if income < 30000:
        anomalies.append("Income is below typical lending minimum")

    # Credit score check
    credit_score = applicant_data.get("credit_score", 0)
    if credit_score < 600:
        anomalies.append("Credit score is below acceptable threshold (600)")

    # Debt-to-income check
    existing_liabilities = applicant_data.get("existing_liabilities", 0)
    monthly_income = income / 12 if income > 0 else 0
    monthly_debt = existing_liabilities / 12 if existing_liabilities > 0 else 0
    dti = calculate_debt_to_income_ratio(monthly_income, monthly_debt)

    if dti > 0.45:
        anomalies.append(f"Current debt-to-income ratio is high ({dti:.2%})")

    # Loan amount check
    loan_amount = applicant_data.get("loan_amount", 0)
    tenure_months = applicant_data.get("tenure_months", 0)

    if tenure_months > 0:
        monthly_payment = loan_amount / tenure_months
        if monthly_payment > monthly_income * 0.5:
            anomalies.append("Estimated monthly payment exceeds 50% of income")

    # Employment check
    employment_type = applicant_data.get("employment_type", "")
    if employment_type == "SELF_EMPLOYED":
        income_variance = applicant_data.get("income_variance", 0.2)
        if income_variance > 0.3:
            anomalies.append("Self-employed with high income variance")

    return anomalies


@mcp.tool()
def calculate_financial_metrics(applicant_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate comprehensive financial metrics"""
    income = applicant_data.get("income", 0)
    existing_liabilities = applicant_data.get("existing_liabilities", 0)
    loan_amount = applicant_data.get("loan_amount", 0)
    credit_score = applicant_data.get("credit_score", 600)

    monthly_income = income / 12 if income > 0 else 0
    monthly_debt = existing_liabilities / 12 if existing_liabilities > 0 else 0
    monthly_payment = loan_amount / 12 if loan_amount > 0 else 0

    # Calculate DTI after new loan
    total_monthly_debt = monthly_debt + monthly_payment
    new_dti = calculate_debt_to_income_ratio(monthly_income, total_monthly_debt)

    credit_risk = assess_credit_score_risk(credit_score)
    loan_risk = assess_loan_amount_risk(loan_amount, income, existing_liabilities)
    anomalies = detect_anomalies(applicant_data)

    return {
        "debt_to_income_ratio": new_dti,
        "debt_to_income_ratio_current": calculate_debt_to_income_ratio(
            monthly_income, monthly_debt
        ),
        "debt_to_income_ratio_with_new_loan": new_dti,
        "credit_score_risk": credit_risk["credit_score_risk"],
        "loan_amount_risk": loan_risk["loan_amount_risk"],
        "monthly_income": round(monthly_income, 2),
        "monthly_debt": round(monthly_debt, 2),
        "monthly_payment": round(monthly_payment, 2),
        "total_monthly_debt": round(total_monthly_debt, 2),
        "anomalies_detected": anomalies,
        "reasoning": f"DTI would be {new_dti:.1%} after loan. Credit risk: {credit_risk['credit_score_risk']}. "
        f"Loan risk: {loan_risk['loan_amount_risk']}.",
    }


