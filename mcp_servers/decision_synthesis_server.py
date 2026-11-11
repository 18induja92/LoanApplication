"""
DecisionSynthesis MCP Server
Synthesizes analysis and generates loan decisions
"""

import json
import logging
from typing import Any, Dict, List
from fastmcp.server import FastMCP

logger = logging.getLogger(__name__)

# Initialize MCP server - synthesizes decisions from all agents
mcp = FastMCP("decision-synthesis", instructions="Synthesizes all agent analyses into final loan decisions with risk scores")


@mcp.tool()
def synthesize_decision(
    applicant_data: Dict[str, Any],
    applicant_profile_analysis: Dict[str, Any],
    financial_risk_analysis: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Synthesize all analysis into a final decision
    """
    from mcp_servers.risk_rules_server import (
        assess_credit_score_risk,
        assess_loan_amount_risk,
        calculate_debt_to_income_ratio,
        detect_anomalies
    )

    # Extract key metrics - try from structured analysis first, fallback to applicant_data
    income_stability = applicant_profile_analysis.get("income_stability_score", 0.6)
    employment_risk = applicant_profile_analysis.get("employment_risk", "MEDIUM")

    # Calculate from applicant_data if not in analysis
    if not employment_risk or employment_risk == "MEDIUM":
        employment_type = applicant_data.get("employment_type", "FULL_TIME")
        employment_risk = "LOW" if employment_type == "FULL_TIME" else "HIGH" if employment_type == "SELF_EMPLOYED" else "MEDIUM"

    # Get credit risk from score
    credit_score = applicant_data.get("credit_score", 700)
    credit_risk_result = assess_credit_score_risk(credit_score)
    credit_risk = credit_risk_result.get("credit_score_risk", "MEDIUM")

    # Get loan risk
    loan_amount = applicant_data.get("loan_amount", 0)
    income = applicant_data.get("income", 0)
    existing_liabilities = applicant_data.get("existing_liabilities", 0)
    loan_risk_result = assess_loan_amount_risk(loan_amount, income, existing_liabilities)
    loan_risk = loan_risk_result.get("loan_amount_risk", "MEDIUM")

    # Calculate DTI
    monthly_income = income / 12 if income > 0 else 0
    monthly_debt = existing_liabilities / 12 if existing_liabilities > 0 else 0
    monthly_payment = loan_amount / 12 if loan_amount > 0 else 0
    dti_ratio = calculate_debt_to_income_ratio(monthly_income, monthly_debt + monthly_payment)

    # Detect anomalies
    anomalies = detect_anomalies(applicant_data)

    # Calculate risk score (0-1, higher = more risky)
    risk_score = 0.5

    # Employment factor
    if employment_risk == "LOW":
        risk_score -= 0.15
    elif employment_risk == "HIGH":
        risk_score += 0.15
    elif employment_risk == "VERY_HIGH":
        risk_score += 0.25

    # Credit risk factor
    if credit_risk == "LOW":
        risk_score -= 0.15
    elif credit_risk == "HIGH":
        risk_score += 0.15
    elif credit_risk == "VERY_HIGH":
        risk_score += 0.25

    # Loan risk factor
    if loan_risk == "LOW":
        risk_score -= 0.10
    elif loan_risk == "HIGH":
        risk_score += 0.10
    elif loan_risk == "VERY_HIGH":
        risk_score += 0.20

    # Income stability factor
    risk_score -= income_stability * 0.10

    # DTI factor
    if dti_ratio <= 0.30:
        risk_score -= 0.10
    elif dti_ratio <= 0.45:
        risk_score -= 0.05
    elif dti_ratio <= 0.50:
        pass  # No adjustment
    else:
        risk_score += 0.15

    # Anomalies factor
    risk_score += len(anomalies) * 0.05

    # Clamp risk score
    risk_score = max(0.0, min(1.0, risk_score))

    # Determine classification and confidence
    classification, confidence = determine_classification(risk_score, employment_risk, credit_risk, anomalies)

    # Key decision factors
    key_factors = extract_key_factors(
        income_stability, employment_risk, credit_risk, loan_risk, dti_ratio, anomalies
    )

    # Explanation
    explanation = generate_explanation(classification, risk_score, key_factors)

    return {
        "classification": classification,
        "risk_score": round(risk_score, 3),
        "confidence_level": round(confidence, 3),
        "key_decision_factors": key_factors,
        "explanation": explanation,
        "analysis_summary": {
            "income_stability_score": income_stability,
            "employment_risk": employment_risk,
            "credit_score_risk": credit_risk,
            "loan_amount_risk": loan_risk,
            "debt_to_income_ratio": dti_ratio,
            "anomalies_count": len(anomalies),
        },
    }


@mcp.tool()
def determine_classification(
    risk_score: float, employment_risk: str, credit_risk: str, anomalies: List[str]
) -> tuple:
    """Determine classification and confidence level"""

    # Automatic rejection criteria (high risk)
    if risk_score > 0.80 or credit_risk == "VERY_HIGH" or employment_risk == "VERY_HIGH":
        return "REJECTED", 0.95

    # Automatic approval criteria (low risk)
    if risk_score < 0.20 and credit_risk in ["LOW", "MEDIUM"] and employment_risk in ["LOW", "MEDIUM"]:
        return "APPROVED", 0.90

    # Medium-high risk that needs review
    if risk_score > 0.65:
        return "REVIEW", 0.80

    # Medium risk - needs review but lower confidence
    if 0.25 <= risk_score <= 0.65:
        confidence = 0.7 - (abs(risk_score - 0.45) * 0.2)  # Varies between 0.6-0.8
        return "REVIEW", max(0.6, confidence)

    # Low risk near approval threshold
    if risk_score < 0.25:
        return "REVIEW", 0.70

    return "REVIEW", 0.65


@mcp.tool()
def extract_key_factors(
    income_stability: float,
    employment_risk: str,
    credit_risk: str,
    loan_risk: str,
    dti_ratio: float,
    anomalies: List[str],
) -> List[str]:
    """Extract key decision factors"""
    factors = []

    # Positive factors
    if income_stability > 0.7:
        factors.append("Strong income stability")
    if employment_risk == "LOW":
        factors.append("Stable employment")
    if credit_risk == "LOW":
        factors.append("Excellent credit history")
    if dti_ratio < 0.30:
        factors.append("Low debt-to-income ratio")
    if loan_risk == "LOW":
        factors.append("Reasonable loan amount")

    # Negative factors
    if income_stability < 0.5:
        factors.append("Income stability concerns")
    if employment_risk in ["HIGH", "VERY_HIGH"]:
        factors.append("Employment risk concerns")
    if credit_risk in ["HIGH", "VERY_HIGH"]:
        factors.append("Credit score concerns")
    if dti_ratio > 0.45:
        factors.append("High debt-to-income ratio")
    if loan_risk in ["HIGH", "VERY_HIGH"]:
        factors.append("Loan amount concerns")

    # Anomalies
    if len(anomalies) > 0:
        factors.append(f"Detected {len(anomalies)} anomalies")

    # Ensure we have factors
    if not factors:
        factors.append("Standard risk assessment")

    return factors


@mcp.tool()
def generate_explanation(classification: str, risk_score: float, key_factors: List[str]) -> str:
    """Generate human-readable explanation"""

    factor_text = " ".join(key_factors[:3])  # Take top 3 factors

    if classification == "APPROVED":
        return f"Application meets lending criteria with low risk profile ({risk_score:.1%}). Key strengths: {factor_text}"

    elif classification == "REJECTED":
        return f"Application does not meet lending criteria due to high risk ({risk_score:.1%}). Concerns: {factor_text}"

    else:  # REVIEW
        return f"Application requires manual review due to mixed risk indicators ({risk_score:.1%}). Factors: {factor_text}"


