"""
FinancialRiskAgent
Performs comprehensive financial risk analysis and anomaly detection
"""

import logging
from typing import Any, Dict
from anthropic import Anthropic

logger = logging.getLogger(__name__)


def create_financial_risk_agent() -> Dict[str, Any]:
    """Create FinancialRiskAgent with Claude"""

    client = Anthropic()

    system_prompt = """You are an expert financial analyst specializing in lending risk assessment.
Your role is to perform comprehensive financial analysis on loan applications.

When analyzing an applicant, you MUST:
1. Calculate comprehensive financial metrics (DTI, etc.)
2. Assess credit score risk
3. Evaluate loan amount appropriateness
4. Detect any financial anomalies
5. Synthesize into risk assessment

Use the provided tools to gather financial information and provide detailed analysis.

Output a structured financial report including:
- Debt-to-Income Ratio (current and with new loan)
- Credit Score Risk Level
- Loan Amount Risk Assessment
- Detected Anomalies (if any)
- Overall Financial Risk Score
- Recommendations

Be precise with financial calculations and highlight any red flags."""

    tools = [
        {
            "name": "calculate_metrics",
            "description": "Calculate comprehensive financial metrics",
            "input_schema": {
                "type": "object",
                "properties": {
                    "applicant_data": {
                        "type": "object",
                        "description": "Applicant financial data"
                    }
                },
                "required": ["applicant_data"]
            }
        },
        {
            "name": "assess_credit_risk",
            "description": "Assess credit score risk level",
            "input_schema": {
                "type": "object",
                "properties": {
                    "credit_score": {"type": "integer"}
                },
                "required": ["credit_score"]
            }
        },
        {
            "name": "assess_loan_risk",
            "description": "Assess loan amount risk",
            "input_schema": {
                "type": "object",
                "properties": {
                    "loan_amount": {"type": "number"},
                    "income": {"type": "number"},
                    "existing_liabilities": {"type": "number"}
                },
                "required": ["loan_amount", "income", "existing_liabilities"]
            }
        },
        {
            "name": "detect_anomalies",
            "description": "Detect financial anomalies in application",
            "input_schema": {
                "type": "object",
                "properties": {
                    "applicant_data": {"type": "object"}
                },
                "required": ["applicant_data"]
            }
        }
    ]

    def process_tool_call(tool_name: str, tool_input: Dict[str, Any]) -> str:
        """Process tool calls from the agent"""
        from mcp_servers.risk_rules_server import (
            calculate_financial_metrics,
            assess_credit_score_risk,
            assess_loan_amount_risk,
            detect_anomalies
        )
        import json

        try:
            if tool_name == "calculate_metrics":
                result = calculate_financial_metrics(tool_input["applicant_data"])
            elif tool_name == "assess_credit_risk":
                result = assess_credit_score_risk(tool_input["credit_score"])
            elif tool_name == "assess_loan_risk":
                result = assess_loan_amount_risk(
                    tool_input["loan_amount"],
                    tool_input["income"],
                    tool_input["existing_liabilities"]
                )
            elif tool_name == "detect_anomalies":
                anomalies = detect_anomalies(tool_input["applicant_data"])
                result = {"anomalies": anomalies, "count": len(anomalies)}
            else:
                result = {"error": f"Unknown tool: {tool_name}"}

            return json.dumps(result)
        except Exception as e:
            logger.error(f"Error processing tool {tool_name}: {e}")
            return json.dumps({"error": str(e)})

    def run_analysis(applicant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run financial risk analysis"""
        messages = [
            {
                "role": "user",
                "content": f"""Please perform a comprehensive financial risk analysis for this applicant:

Applicant ID: {applicant_data.get('applicant_id')}
Income: ${applicant_data.get('income'):,.0f}
Credit Score: {applicant_data.get('credit_score')}
Loan Amount: ${applicant_data.get('loan_amount'):,.0f}
Existing Liabilities: ${applicant_data.get('existing_liabilities'):,.0f}

Analyze their financial situation thoroughly."""
            }
        ]

        logger.info(f"Starting risk analysis for {applicant_data.get('applicant_id')}")

        # Agent loop
        max_iterations = 10
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
                            "analysis": block.text,
                            "applicant_id": applicant_data.get("applicant_id")
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
            "applicant_id": applicant_data.get("applicant_id")
        }

    return {
        "agent_name": "FinancialRiskAgent",
        "run": run_analysis,
        "system_prompt": system_prompt,
        "tools": tools
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    agent = create_financial_risk_agent()

    test_data = {
        "applicant_id": "APP-001",
        "income": 75000,
        "credit_score": 750,
        "loan_amount": 250000,
        "existing_liabilities": 50000
    }
    result = agent["run"](test_data)
    print(f"Result: {result}")
