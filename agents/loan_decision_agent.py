"""
LoanDecisionAgent
Synthesizes all analyses and generates final loan decision
"""

import logging
from typing import Any, Dict
from anthropic import Anthropic

logger = logging.getLogger(__name__)


def create_loan_decision_agent() -> Dict[str, Any]:
    """Create LoanDecisionAgent with Claude"""

    client = Anthropic()

    system_prompt = """You are a senior loan decision officer responsible for final lending decisions.
Your role is to synthesize all applicant and financial analyses into a final recommendation.

When making a decision, you MUST:
1. Review the applicant profile analysis
2. Review the financial risk analysis
3. Use the decision synthesis tool to generate the decision
4. Provide clear justification for the decision

Output a structured decision including:
- Classification (APPROVED / REJECTED / REVIEW)
- Risk Score (0-1)
- Confidence Level (0-1)
- Key Decision Factors
- Clear Explanation

Be fair, consistent, and consider all factors in your decision."""

    tools = [
        {
            "name": "synthesize_decision",
            "description": "Synthesize decision from all analyses",
            "input_schema": {
                "type": "object",
                "properties": {
                    "applicant_data": {"type": "object"},
                    "applicant_profile_analysis": {"type": "object"},
                    "financial_risk_analysis": {"type": "object"}
                },
                "required": [
                    "applicant_data",
                    "applicant_profile_analysis",
                    "financial_risk_analysis"
                ]
            }
        }
    ]

    def process_tool_call(tool_name: str, tool_input: Dict[str, Any]) -> str:
        """Process tool calls from the agent"""
        from mcp_servers.decision_synthesis_server import synthesize_decision
        import json

        try:
            if tool_name == "synthesize_decision":
                result = synthesize_decision(
                    tool_input["applicant_data"],
                    tool_input["applicant_profile_analysis"],
                    tool_input["financial_risk_analysis"]
                )
            else:
                result = {"error": f"Unknown tool: {tool_name}"}

            return json.dumps(result)
        except Exception as e:
            logger.error(f"Error processing tool {tool_name}: {e}")
            return json.dumps({"error": str(e)})

    def run_decision(
        applicant_data: Dict[str, Any],
        applicant_profile: Dict[str, Any],
        financial_risk: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate final loan decision"""
        import json

        messages = [
            {
                "role": "user",
                "content": f"""Review the following analyses and make a final loan decision:

APPLICANT PROFILE ANALYSIS:
{applicant_profile.get('analysis', str(applicant_profile))}

FINANCIAL RISK ANALYSIS:
{financial_risk.get('analysis', str(financial_risk))}

APPLICANT DATA:
- Income: ${applicant_data.get('income'):,.0f}
- Credit Score: {applicant_data.get('credit_score')}
- Loan Amount: ${applicant_data.get('loan_amount'):,.0f}

Please synthesize this information into a final decision."""
            }
        ]

        logger.info(f"Starting decision synthesis for {applicant_data.get('applicant_id')}")

        max_iterations = 10
        iteration = 0
        captured_decision_data = None

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
                            "decision_summary": block.text,
                            "decision_data": captured_decision_data,
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
                        # Capture structured decision data from synthesize_decision tool
                        if block.name == "synthesize_decision":
                            try:
                                captured_decision_data = json.loads(result)
                                logger.info(f"Captured decision data: classification={captured_decision_data.get('classification')}, "
                                          f"risk_score={captured_decision_data.get('risk_score')}, "
                                          f"confidence={captured_decision_data.get('confidence_level')}")
                            except (json.JSONDecodeError, TypeError) as e:
                                logger.error(f"Failed to parse decision data: {e}")

                messages.append({"role": "user", "content": tool_results})

        return {
            "status": "error",
            "message": "Max iterations reached",
            "decision_data": captured_decision_data,
            "applicant_id": applicant_data.get("applicant_id")
        }

    return {
        "agent_name": "LoanDecisionAgent",
        "run": run_decision,
        "system_prompt": system_prompt,
        "tools": tools
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    agent = create_loan_decision_agent()

    test_applicant = {"applicant_id": "APP-001", "income": 75000, "credit_score": 750, "loan_amount": 250000}
    test_profile = {"analysis": "Strong applicant with stable income and excellent credit"}
    test_risk = {"analysis": "Low financial risk, acceptable DTI ratios"}

    result = agent["run"](test_applicant, test_profile, test_risk)
    print(f"Result: {result}")
