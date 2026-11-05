"""
ComplianceAgent
Manages audit trails, compliance tracking, and notifications
"""

import logging
from typing import Any, Dict
from anthropic import Anthropic

logger = logging.getLogger(__name__)


def create_compliance_agent() -> Dict[str, Any]:
    """Create ComplianceAgent with Claude"""

    client = Anthropic()

    system_prompt = """You are a compliance officer responsible for audit trails, regulatory compliance, and notifications.
Your role is to ensure all loan decisions are properly documented and tracked.

When given a decision, you MUST:
1. Create a case record for the application
2. Log all decision factors
3. Generate notification to applicant
4. Create compliance record for regulatory requirements
5. Ensure audit trail is complete

Use the provided tools to create all necessary records.

Output a compliance summary including:
- Case ID created
- Notification status
- Compliance record created
- Audit trail established
- Regulatory status

Ensure all requirements are met for audit and compliance."""

    tools = [
        {
            "name": "create_case_record",
            "description": "Create a case record for the application",
            "input_schema": {
                "type": "object",
                "properties": {
                    "application_id": {"type": "string"},
                    "decision": {"type": "string"},
                    "risk_score": {"type": "number"},
                    "confidence": {"type": "number"}
                },
                "required": ["application_id", "decision", "risk_score", "confidence"]
            }
        },
        {
            "name": "log_agent_action",
            "description": "Log an agent action in audit trail",
            "input_schema": {
                "type": "object",
                "properties": {
                    "case_id": {"type": "string"},
                    "application_id": {"type": "string"},
                    "agent_name": {"type": "string"},
                    "action": {"type": "string"},
                    "details": {"type": "object"}
                },
                "required": ["case_id", "application_id", "agent_name", "action", "details"]
            }
        },
        {
            "name": "generate_notification",
            "description": "Generate notification for applicant",
            "input_schema": {
                "type": "object",
                "properties": {
                    "case_id": {"type": "string"},
                    "application_id": {"type": "string"},
                    "decision": {"type": "string"},
                    "summary": {"type": "string"}
                },
                "required": ["case_id", "application_id", "decision", "summary"]
            }
        },
        {
            "name": "create_compliance_record",
            "description": "Create compliance record",
            "input_schema": {
                "type": "object",
                "properties": {
                    "case_id": {"type": "string"},
                    "application_id": {"type": "string"},
                    "decision": {"type": "string"},
                    "risk_score": {"type": "number"},
                    "decision_factors": {"type": "array"}
                },
                "required": ["case_id", "application_id", "decision", "risk_score", "decision_factors"]
            }
        }
    ]

    def process_tool_call(tool_name: str, tool_input: Dict[str, Any]) -> str:
        """Process tool calls from the agent"""
        from mcp_servers.notification_server import (
            create_case_record,
            log_agent_action,
            generate_notification,
            create_compliance_record
        )
        import json

        try:
            if tool_name == "create_case_record":
                result = create_case_record(
                    tool_input["application_id"],
                    tool_input["decision"],
                    tool_input["risk_score"],
                    tool_input["confidence"]
                )
            elif tool_name == "log_agent_action":
                result = log_agent_action(
                    tool_input["case_id"],
                    tool_input["application_id"],
                    tool_input["agent_name"],
                    tool_input["action"],
                    tool_input["details"]
                )
            elif tool_name == "generate_notification":
                result = generate_notification(
                    tool_input["case_id"],
                    tool_input["application_id"],
                    tool_input["decision"],
                    tool_input["summary"]
                )
            elif tool_name == "create_compliance_record":
                result = create_compliance_record(
                    tool_input["case_id"],
                    tool_input["application_id"],
                    tool_input["decision"],
                    tool_input["risk_score"],
                    tool_input["decision_factors"]
                )
            else:
                result = {"error": f"Unknown tool: {tool_name}"}

            return json.dumps(result)
        except Exception as e:
            logger.error(f"Error processing tool {tool_name}: {e}")
            return json.dumps({"error": str(e)})

    def run_compliance(
        application_id: str,
        decision: str,
        risk_score: float,
        confidence: float,
        decision_factors: list
    ) -> Dict[str, Any]:
        """Execute compliance workflow"""

        messages = [
            {
                "role": "user",
                "content": f"""Process compliance for this loan decision:

Application ID: {application_id}
Decision: {decision}
Risk Score: {risk_score:.2%}
Confidence: {confidence:.2%}
Key Factors: {', '.join(decision_factors[:3])}

Please create all necessary case records, audit logs, notifications, and compliance documentation."""
            }
        ]

        logger.info(f"Starting compliance processing for {application_id}")

        max_iterations = 15
        iteration = 0

        while iteration < max_iterations:
            iteration += 1

            response = client.messages.create(
                model="global.anthropic.claude-haiku-4-5-20251001-v1:0",
                max_tokens=2000,
                system=system_prompt,
                tools=tools,
                messages=messages
            )

            messages.append({"role": "assistant", "content": response.content})

            if response.stop_reason == "end_turn":
                for block in response.content:
                    if hasattr(block, "text"):
                        return {
                            "status": "success",
                            "compliance_summary": block.text,
                            "application_id": application_id
                        }
                break

            if response.stop_reason == "tool_use":
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        logger.info(f"Agent called tool: {block.name}")
                        result = process_tool_call(block.name, block.input)
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result
                        })

                messages.append({"role": "user", "content": tool_results})

        return {
            "status": "error",
            "message": "Max iterations reached",
            "application_id": application_id
        }

    return {
        "agent_name": "ComplianceAgent",
        "run": run_compliance,
        "system_prompt": system_prompt,
        "tools": tools
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    agent = create_compliance_agent()

    result = agent["run"](
        "APP-001",
        "APPROVED",
        0.25,
        0.92,
        ["Strong income", "Good credit", "Low DTI"]
    )
    print(f"Result: {result}")
