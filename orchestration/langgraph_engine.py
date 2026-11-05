"""
LangGraph Orchestration Engine
Coordinates the multi-agent workflow for loan approval
"""

import logging
import json
from typing import Any, Dict, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class ApplicationState:
    """State of application throughout workflow"""
    application_id: str
    applicant_data: Dict[str, Any]
    status: str  # pending, profile_analysis, risk_analysis, decision, compliance, completed
    applicant_profile: Optional[Dict[str, Any]] = None
    financial_risk: Optional[Dict[str, Any]] = None
    decision: Optional[Dict[str, Any]] = None
    compliance: Optional[Dict[str, Any]] = None
    errors: list = None
    created_at: str = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()


class LoanApprovalOrchestrator:
    """Orchestrates the multi-agent loan approval workflow"""

    def __init__(self):
        """Initialize orchestrator with agents"""
        from agents.applicant_profile_agent import create_applicant_profile_agent
        from agents.financial_risk_agent import create_financial_risk_agent
        from agents.loan_decision_agent import create_loan_decision_agent
        from agents.compliance_agent import create_compliance_agent

        self.applicant_agent = create_applicant_profile_agent()
        self.risk_agent = create_financial_risk_agent()
        self.decision_agent = create_loan_decision_agent()
        self.compliance_agent = create_compliance_agent()

        logger.info("Orchestrator initialized with all 4 agents")

    def process_application(self, application_id: str, applicant_data: Dict[str, Any], applicant_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process loan application through all agents

        Workflow:
        1. Initialize state
        2. Run applicant profile analysis
        3. Run financial risk analysis
        4. Synthesize decision
        5. Process compliance
        6. Return final result
        """

        # Use provided applicant_id or extract from applicant_data
        lookup_id = applicant_id or applicant_data.get("applicant_id", application_id)

        # Step 1: Initialize
        state = ApplicationState(
            application_id=application_id,
            applicant_data=applicant_data,
            status="pending"
        )
        logger.info(f"Starting application processing: {application_id} (applicant: {lookup_id})")

        try:
            # Step 2: Applicant Profile Analysis
            state.status = "profile_analysis"
            logger.info("Running ApplicantProfileAgent...")
            profile_result = self.applicant_agent["run"](lookup_id, applicant_data)

            if profile_result.get("status") == "success":
                state.applicant_profile = profile_result
                logger.info("Profile analysis completed")
            else:
                state.errors.append(f"Profile analysis failed: {profile_result.get('message')}")
                logger.error(f"Profile analysis error: {profile_result}")

            # Step 3: Financial Risk Analysis
            state.status = "risk_analysis"
            logger.info("Running FinancialRiskAgent...")
            risk_result = self.risk_agent["run"](applicant_data)

            if risk_result.get("status") == "success":
                state.financial_risk = risk_result
                logger.info("Risk analysis completed")
            else:
                state.errors.append(f"Risk analysis failed: {risk_result.get('message')}")
                logger.error(f"Risk analysis error: {risk_result}")

            # Step 4: Decision Synthesis
            state.status = "decision"
            logger.info("Running LoanDecisionAgent...")

            decision_result = self.decision_agent["run"](
                applicant_data,
                state.applicant_profile or {},
                state.financial_risk or {}
            )

            if decision_result.get("status") == "success":
                state.decision = decision_result
                logger.info("Decision synthesis completed")
            else:
                state.errors.append(f"Decision synthesis failed: {decision_result.get('message')}")
                logger.error(f"Decision error: {decision_result}")

            # Step 5: Compliance Processing
            state.status = "compliance"
            logger.info("Running ComplianceAgent...")

            # Extract decision details from synthesis
            decision_summary = state.decision.get("decision_summary", "")
            decision_class = "REVIEW"  # Default
            risk_score = 0.5
            confidence = 0.5

            # Try to parse decision from agent response
            if "APPROVED" in decision_summary.upper():
                decision_class = "APPROVED"
                risk_score = 0.25
                confidence = 0.90
            elif "REJECTED" in decision_summary.upper():
                decision_class = "REJECTED"
                risk_score = 0.85
                confidence = 0.95

            compliance_result = self.compliance_agent["run"](
                application_id,
                decision_class,
                risk_score,
                confidence,
                ["Decision processed", "Compliance documented"]
            )

            if compliance_result.get("status") == "success":
                state.compliance = compliance_result
                logger.info("Compliance processing completed")
            else:
                state.errors.append(f"Compliance failed: {compliance_result.get('message')}")

            # Final status
            state.status = "completed"
            logger.info(f"Application {application_id} processing completed")

            return self._format_final_result(state)

        except Exception as e:
            logger.error(f"Error processing application: {e}")
            state.status = "failed"
            state.errors.append(str(e))
            return self._format_final_result(state)

    def _format_final_result(self, state: ApplicationState) -> Dict[str, Any]:
        """Format the final result from orchestration"""
        return {
            "application_id": state.application_id,
            "status": state.status,
            "profile_analysis": state.applicant_profile,
            "financial_risk": state.financial_risk,
            "decision": state.decision,
            "compliance": state.compliance,
            "errors": state.errors if state.errors else None,
            "created_at": state.created_at
        }


# Global orchestrator instance
_orchestrator = None


def get_orchestrator() -> LoanApprovalOrchestrator:
    """Get or create global orchestrator instance"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = LoanApprovalOrchestrator()
    return _orchestrator


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Test the orchestrator
    orchestrator = LoanApprovalOrchestrator()

    test_data = {
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

    result = orchestrator.process_application("APP-001", test_data)
    print(json.dumps(result, indent=2, default=str))
