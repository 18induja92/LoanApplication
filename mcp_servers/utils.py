"""
MCP Server Utilities
Shared utilities and helpers for MCP servers
"""

import json
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def validate_applicant_data(applicant_data: Dict[str, Any]) -> tuple[bool, List[str]]:
    """Validate applicant data structure"""
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

    errors = []

    # Check required fields
    for field in required_fields:
        if field not in applicant_data:
            errors.append(f"Missing required field: {field}")

    # Validate field types and ranges
    if "age" in applicant_data:
        age = applicant_data["age"]
        if not isinstance(age, (int, float)) or age < 18 or age > 100:
            errors.append("Age must be between 18 and 100")

    if "income" in applicant_data:
        income = applicant_data["income"]
        if not isinstance(income, (int, float)) or income < 0:
            errors.append("Income must be non-negative")

    if "credit_score" in applicant_data:
        score = applicant_data["credit_score"]
        if not isinstance(score, (int, float)) or score < 300 or score > 850:
            errors.append("Credit score must be between 300 and 850")

    if "loan_amount" in applicant_data:
        amount = applicant_data["loan_amount"]
        if not isinstance(amount, (int, float)) or amount < 0:
            errors.append("Loan amount must be non-negative")

    if "tenure_months" in applicant_data:
        tenure = applicant_data["tenure_months"]
        if not isinstance(tenure, (int, float)) or tenure < 1:
            errors.append("Tenure must be at least 1 month")

    return len(errors) == 0, errors


def format_currency(amount: float) -> str:
    """Format amount as currency string"""
    return f"${amount:,.2f}"


def format_percentage(value: float) -> str:
    """Format value as percentage"""
    return f"{value * 100:.1f}%"


def format_risk_level(risk: str) -> str:
    """Format risk level with emoji indicator"""
    indicators = {
        "LOW": "🟢 LOW",
        "MEDIUM": "🟡 MEDIUM",
        "HIGH": "🔴 HIGH",
        "VERY_HIGH": "🔴 VERY HIGH",
    }
    return indicators.get(risk, risk)


def format_decision(decision: str) -> str:
    """Format decision with emoji indicator"""
    indicators = {
        "APPROVED": "✅ APPROVED",
        "REJECTED": "❌ REJECTED",
        "REVIEW": "⏳ REQUIRES REVIEW",
    }
    return indicators.get(decision, decision)


def calculate_monthly_payment(
    principal: float, annual_rate: float, months: int
) -> float:
    """Calculate monthly payment using standard amortization formula"""
    if months <= 0 or principal <= 0:
        return 0

    monthly_rate = annual_rate / 100 / 12
    if monthly_rate == 0:
        return principal / months

    numerator = principal * monthly_rate * (1 + monthly_rate) ** months
    denominator = (1 + monthly_rate) ** months - 1

    return numerator / denominator


def create_analysis_summary(
    applicant_profile: Dict[str, Any],
    financial_risk: Dict[str, Any],
    decision: Dict[str, Any],
) -> Dict[str, Any]:
    """Create a comprehensive analysis summary"""
    return {
        "profile_analysis": {
            "income_stability": applicant_profile.get("income_stability_score"),
            "employment_risk": applicant_profile.get("employment_risk"),
            "credit_history": applicant_profile.get("credit_history_summary"),
        },
        "financial_analysis": {
            "debt_to_income": financial_risk.get("debt_to_income_ratio_with_new_loan"),
            "credit_risk": financial_risk.get("credit_score_risk"),
            "loan_risk": financial_risk.get("loan_amount_risk"),
            "anomalies": financial_risk.get("anomalies_detected", []),
        },
        "decision": {
            "classification": decision.get("classification"),
            "risk_score": decision.get("risk_score"),
            "confidence": decision.get("confidence_level"),
            "key_factors": decision.get("key_decision_factors"),
        },
    }


def log_mcp_call(server_name: str, tool_name: str, inputs: Dict[str, Any]) -> None:
    """Log MCP server call"""
    logger.debug(f"MCP Call: {server_name}.{tool_name}")
    logger.debug(f"  Inputs: {json.dumps(inputs, default=str)}")


def log_mcp_result(server_name: str, tool_name: str, result: Dict[str, Any]) -> None:
    """Log MCP server result"""
    logger.debug(f"MCP Result: {server_name}.{tool_name}")
    logger.debug(f"  Result: {json.dumps(result, default=str)}")


def handle_mcp_error(server_name: str, tool_name: str, error: Exception) -> Dict[str, Any]:
    """Handle MCP server error"""
    logger.error(f"MCP Error in {server_name}.{tool_name}: {str(error)}")
    return {
        "status": "error",
        "server": server_name,
        "tool": tool_name,
        "error": str(error),
        "message": f"Failed to execute {tool_name} in {server_name}",
    }


def merge_analyses(
    *analysis_results: Dict[str, Any],
) -> Dict[str, Any]:
    """Merge multiple analysis results"""
    merged = {}
    for analysis in analysis_results:
        merged.update(analysis)
    return merged


class MCPServerConfig:
    """Configuration for MCP servers"""

    def __init__(self):
        self.timeout = 10  # seconds
        self.max_retries = 3
        self.log_level = logging.INFO

        # Risk thresholds
        self.risk_high_threshold = 0.75
        self.risk_medium_threshold = 0.25

        # DTI thresholds
        self.dti_acceptable = 0.45
        self.dti_high = 0.50

        # Credit score thresholds
        self.credit_excellent = 750
        self.credit_good = 700
        self.credit_fair = 650
        self.credit_minimum = 600

        # Income thresholds
        self.income_minimum = 30000
        self.income_comfortable = 50000

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "risk_high_threshold": self.risk_high_threshold,
            "risk_medium_threshold": self.risk_medium_threshold,
            "dti_acceptable": self.dti_acceptable,
            "dti_high": self.dti_high,
            "credit_excellent": self.credit_excellent,
            "credit_good": self.credit_good,
            "credit_fair": self.credit_fair,
            "credit_minimum": self.credit_minimum,
            "income_minimum": self.income_minimum,
            "income_comfortable": self.income_comfortable,
        }
