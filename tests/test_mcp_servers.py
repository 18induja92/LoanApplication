"""
Unit tests for MCP Servers
"""

import pytest
from mcp_servers.applicant_db_server import (
    get_applicant_profile,
    calculate_income_stability,
    assess_employment_risk,
    get_credit_history,
    check_application_completeness,
)
from mcp_servers.risk_rules_server import (
    calculate_debt_to_income_ratio,
    assess_credit_score_risk,
    assess_loan_amount_risk,
    detect_anomalies,
    calculate_financial_metrics,
)
from mcp_servers.decision_synthesis_server import (
    synthesize_decision,
    determine_classification,
    extract_key_factors,
)
from mcp_servers.notification_server import (
    create_case_record,
    log_agent_action,
    generate_notification,
    create_compliance_record,
)


class TestApplicantDBServer:
    """Tests for ApplicantDB MCP Server"""

    def test_get_applicant_profile_success(self):
        """Test retrieving existing applicant"""
        result = get_applicant_profile("APP-001")
        assert result["status"] == "success"
        assert result["data"]["applicant_id"] == "APP-001"
        assert result["data"]["name"] == "John Doe"

    def test_get_applicant_profile_not_found(self):
        """Test retrieving non-existent applicant"""
        result = get_applicant_profile("APP-999")
        assert result["status"] == "error"

    def test_calculate_income_stability_high(self):
        """Test high income stability calculation"""
        result = calculate_income_stability("APP-001", 80000, 10)
        assert result["status"] == "success"
        assert result["income_stability_score"] > 0.6

    def test_calculate_income_stability_low(self):
        """Test low income stability calculation"""
        result = calculate_income_stability("APP-004", 40000, 1)
        assert result["status"] == "success"
        assert result["income_stability_score"] < 0.6

    def test_assess_employment_risk_full_time(self):
        """Test employment risk for full-time"""
        result = assess_employment_risk("FULL_TIME", 8)
        assert result["employment_risk"] == "LOW"

    def test_assess_employment_risk_self_employed_low(self):
        """Test employment risk for self-employed (low duration)"""
        result = assess_employment_risk("SELF_EMPLOYED", 2)
        assert result["employment_risk"] == "HIGH"

    def test_assess_employment_risk_part_time(self):
        """Test employment risk for part-time"""
        result = assess_employment_risk("PART_TIME", 5)
        assert result["employment_risk"] == "HIGH"

    def test_get_credit_history_success(self):
        """Test retrieving credit history"""
        result = get_credit_history("APP-001")
        assert result["status"] == "success"
        assert result["credit_score"] == 750
        assert "credit_history_summary" in result

    def test_check_application_completeness_valid(self):
        """Test validation of complete application"""
        applicant_data = {
            "applicant_id": "APP-001",
            "age": 35,
            "income": 75000,
            "employment_type": "FULL_TIME",
            "credit_score": 750,
            "loan_amount": 250000,
            "tenure_months": 360,
            "existing_liabilities": 50000,
            "location": "NEW_YORK",
        }
        result = check_application_completeness(applicant_data)
        assert result["is_complete"] is True
        assert len(result["completeness_flags"]) == 0

    def test_check_application_completeness_missing_fields(self):
        """Test validation with missing fields"""
        applicant_data = {
            "applicant_id": "APP-001",
            "age": 35,
        }
        result = check_application_completeness(applicant_data)
        assert result["is_complete"] is False
        assert len(result["missing_fields"]) > 0


class TestRiskRulesServer:
    """Tests for RiskRulesDB MCP Server"""

    def test_calculate_debt_to_income_normal(self):
        """Test DTI calculation"""
        dti = calculate_debt_to_income_ratio(5000, 1500)  # $5k income, $1.5k debt
        assert 0.29 <= dti <= 0.31

    def test_calculate_debt_to_income_zero_income(self):
        """Test DTI with zero income"""
        dti = calculate_debt_to_income_ratio(0, 1000)
        assert dti == 0.0

    def test_assess_credit_score_excellent(self):
        """Test credit assessment for excellent score"""
        result = assess_credit_score_risk(750)
        assert result["credit_score_risk"] == "LOW"
        assert result["risk_multiplier"] == 0.8

    def test_assess_credit_score_poor(self):
        """Test credit assessment for poor score"""
        result = assess_credit_score_risk(580)
        assert result["credit_score_risk"] == "VERY_HIGH"
        assert result["risk_multiplier"] == 2.0

    def test_assess_loan_amount_reasonable(self):
        """Test loan amount risk assessment"""
        result = assess_loan_amount_risk(150000, 75000, 50000)  # 2x income
        assert result["loan_amount_risk"] == "LOW"

    def test_assess_loan_amount_excessive(self):
        """Test excessive loan amount"""
        result = assess_loan_amount_risk(500000, 50000, 50000)  # 10x income
        assert result["loan_amount_risk"] == "VERY_HIGH"

    def test_detect_anomalies_none(self):
        """Test application with no anomalies"""
        applicant_data = {
            "age": 35,
            "income": 75000,
            "credit_score": 750,
            "existing_liabilities": 50000,
            "loan_amount": 250000,
            "tenure_months": 360,
            "employment_type": "FULL_TIME",
        }
        anomalies = detect_anomalies(applicant_data)
        assert len(anomalies) == 0

    def test_detect_anomalies_young_applicant(self):
        """Test anomaly detection for young applicant"""
        applicant_data = {
            "age": 22,
            "income": 40000,
            "credit_score": 650,
            "existing_liabilities": 20000,
            "loan_amount": 150000,
            "tenure_months": 360,
        }
        anomalies = detect_anomalies(applicant_data)
        assert any("under 25" in str(a).lower() for a in anomalies)

    def test_calculate_financial_metrics(self):
        """Test comprehensive financial metrics calculation"""
        applicant_data = {
            "income": 75000,
            "existing_liabilities": 50000,
            "loan_amount": 250000,
            "credit_score": 750,
        }
        result = calculate_financial_metrics(applicant_data)
        assert "debt_to_income_ratio_with_new_loan" in result
        assert "credit_score_risk" in result
        assert "loan_amount_risk" in result


class TestDecisionSynthesisServer:
    """Tests for DecisionSynthesis MCP Server"""

    def test_determine_classification_approved(self):
        """Test classification for approved"""
        classification, confidence = determine_classification(0.2, "LOW", "LOW", [])
        assert classification == "APPROVED"
        assert confidence > 0.85

    def test_determine_classification_rejected(self):
        """Test classification for rejected"""
        classification, confidence = determine_classification(0.9, "HIGH", "VERY_HIGH", [])
        assert classification == "REJECTED"
        assert confidence > 0.9

    def test_determine_classification_review(self):
        """Test classification for review"""
        classification, confidence = determine_classification(0.5, "MEDIUM", "MEDIUM", [])
        assert classification == "REVIEW"

    def test_extract_key_factors(self):
        """Test key factor extraction"""
        factors = extract_key_factors(0.8, "LOW", "LOW", "LOW", 0.25, [])
        assert len(factors) > 0
        assert any("stable" in str(f).lower() for f in factors)

    def test_synthesize_decision_approve(self):
        """Test decision synthesis leading to approval"""
        applicant_data = {
            "age": 35,
            "income": 75000,
            "credit_score": 750,
            "loan_amount": 250000,
            "tenure_months": 360,
            "existing_liabilities": 50000,
        }
        applicant_profile = {
            "income_stability_score": 0.85,
            "employment_risk": "LOW",
        }
        financial_risk = {
            "credit_score_risk": "LOW",
            "loan_amount_risk": "LOW",
            "debt_to_income_ratio_with_new_loan": 0.35,
            "anomalies_detected": [],
        }

        result = synthesize_decision(applicant_data, applicant_profile, financial_risk)
        assert result["classification"] == "APPROVED"
        assert result["confidence_level"] > 0.8


class TestNotificationServer:
    """Tests for NotificationSystem MCP Server"""

    def test_create_case_record(self):
        """Test case record creation"""
        result = create_case_record("APP-001", "APPROVED", 0.25, 0.92)
        assert "case_id" in result
        assert result["application_id"] == "APP-001"
        assert result["decision"] == "APPROVED"

    def test_log_agent_action(self):
        """Test agent action logging"""
        result = log_agent_action(
            "CASE-2026-ABC123",
            "APP-001",
            "ApplicantProfileAgent",
            "PROFILE_ANALYZED",
            {"score": 0.85},
        )
        assert "id" in result
        assert result["agent_name"] == "ApplicantProfileAgent"

    def test_generate_notification_approved(self):
        """Test notification generation for approved"""
        result = generate_notification(
            "CASE-2026-ABC123", "APP-001", "APPROVED", "Application approved"
        )
        assert result["status"] == "SENT"
        assert "APPROVED" in result["message"]

    def test_generate_notification_rejected(self):
        """Test notification generation for rejected"""
        result = generate_notification(
            "CASE-2026-ABC123", "APP-001", "REJECTED", "Application rejected"
        )
        assert result["status"] == "SENT"
        assert "REJECTED" in result["message"]

    def test_create_compliance_record(self):
        """Test compliance record creation"""
        result = create_compliance_record(
            "CASE-2026-ABC123",
            "APP-001",
            "APPROVED",
            0.25,
            ["Strong income", "Good credit"],
        )
        assert result["compliance_status"] == "COMPLIANT"
        assert result["audit_trail_created"] is True


class TestIntegration:
    """Integration tests across multiple servers"""

    def test_full_application_flow(self):
        """Test complete application flow through all servers"""
        # Step 1: Get applicant profile
        profile = get_applicant_profile("APP-001")
        assert profile["status"] == "success"

        # Step 2: Calculate income stability
        applicant = profile["data"]
        stability = calculate_income_stability(
            applicant["applicant_id"],
            applicant["income"],
            applicant["employment_duration_years"],
        )
        assert stability["status"] == "success"

        # Step 3: Calculate financial metrics
        metrics = calculate_financial_metrics(applicant)
        assert "debt_to_income_ratio_with_new_loan" in metrics

        # Step 4: Synthesize decision
        applicant_profile = {
            "income_stability_score": stability["income_stability_score"],
            "employment_risk": assess_employment_risk(
                applicant["employment_type"], applicant["employment_duration_years"]
            )["employment_risk"],
        }

        decision = synthesize_decision(applicant, applicant_profile, metrics)
        assert "classification" in decision

        # Step 5: Create case record
        case = create_case_record(
            applicant["applicant_id"],
            decision["classification"],
            decision["risk_score"],
            decision["confidence_level"],
        )
        assert "case_id" in case


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
