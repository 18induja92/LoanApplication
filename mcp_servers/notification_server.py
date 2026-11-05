"""
NotificationSystem MCP Server
Manages audit trails, compliance logging, and notifications
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict
from uuid import uuid4
from fastmcp.server import FastMCP

logger = logging.getLogger(__name__)

# Initialize MCP server - handles compliance and audit trails
mcp = FastMCP("notification-system", instructions="Manages audit trails, compliance documentation, case records, and notifications")

# In-memory audit log (in production, this would be the database)
AUDIT_LOG = []


@mcp.tool()
def create_case_record(
    application_id: str, decision: str, risk_score: float, confidence: float
) -> Dict[str, Any]:
    """Create a new case record"""
    case_id = f"CASE-2026-{uuid4().hex[:8].upper()}"
    timestamp = datetime.now().isoformat()

    case_record = {
        "case_id": case_id,
        "application_id": application_id,
        "decision": decision,
        "risk_score": risk_score,
        "confidence": confidence,
        "created_at": timestamp,
        "status": "COMPLETED",
    }

    AUDIT_LOG.append(case_record)
    logger.info(f"Case record created: {case_id} - Decision: {decision}")

    return case_record


@mcp.tool()
def log_agent_action(
    case_id: str, application_id: str, agent_name: str, action: str, details: Dict[str, Any]
) -> Dict[str, Any]:
    """Log an agent action for audit trail"""
    log_entry = {
        "id": f"LOG-{uuid4().hex[:8].upper()}",
        "case_id": case_id,
        "application_id": application_id,
        "agent_name": agent_name,
        "action": action,
        "details": details,
        "timestamp": datetime.now().isoformat(),
    }

    AUDIT_LOG.append(log_entry)
    logger.info(f"Agent action logged: {agent_name} - {action}")

    return log_entry


@mcp.tool()
def generate_notification(
    case_id: str, application_id: str, decision: str, summary: str
) -> Dict[str, Any]:
    """Generate notification for decision"""

    notification_type = "DECISION_NOTIFICATION"
    status = "SENT"

    # Format notification message based on decision
    if decision == "APPROVED":
        message = f"✓ Loan application {application_id} has been APPROVED. "
        message += f"Case ID: {case_id}. Please check your application status for details."
    elif decision == "REJECTED":
        message = f"✗ Loan application {application_id} has been REJECTED. "
        message += f"Case ID: {case_id}. Please contact us to understand the decision."
    else:  # REVIEW
        message = f"⏳ Loan application {application_id} requires manual review. "
        message += f"Case ID: {case_id}. You will be contacted shortly."

    notification = {
        "notification_id": f"NOTIF-{uuid4().hex[:8].upper()}",
        "case_id": case_id,
        "application_id": application_id,
        "type": notification_type,
        "status": status,
        "decision": decision,
        "message": message,
        "summary": summary,
        "timestamp": datetime.now().isoformat(),
    }

    logger.info(f"Notification generated: {application_id} - {decision}")

    return notification


@mcp.tool()
def create_compliance_record(
    case_id: str,
    application_id: str,
    decision: str,
    risk_score: float,
    decision_factors: list,
) -> Dict[str, Any]:
    """Create compliance record for regulatory requirements"""

    compliance_record = {
        "compliance_id": f"COMP-{uuid4().hex[:8].upper()}",
        "case_id": case_id,
        "application_id": application_id,
        "decision": decision,
        "risk_score": risk_score,
        "decision_factors": decision_factors,
        "created_at": datetime.now().isoformat(),
        "compliance_status": "COMPLIANT",
        "requires_review": risk_score > 0.75 or decision == "REVIEW",
        "audit_trail_created": True,
        "data_retention_period_days": 2555,  # 7 years
    }

    logger.info(f"Compliance record created: {case_id}")

    return compliance_record


@mcp.tool()
def get_audit_trail(application_id: str) -> Dict[str, Any]:
    """Retrieve complete audit trail for an application"""
    relevant_logs = [log for log in AUDIT_LOG if log.get("application_id") == application_id]

    return {
        "application_id": application_id,
        "audit_trail": relevant_logs,
        "total_entries": len(relevant_logs),
        "generated_at": datetime.now().isoformat(),
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    server = create_server()
    logger.info("NotificationSystem MCP Server started")
