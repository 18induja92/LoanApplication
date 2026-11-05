"""
ApplicantProfileAgent
Analyzes applicant background, employment, and creditworthiness
"""

import logging
from typing import Any, Dict
from anthropic import Anthropic

logger = logging.getLogger(__name__)


def create_applicant_profile_agent() -> Dict[str, Any]:
    """Create ApplicantProfileAgent with Claude"""

    client = Anthropic()

    system_prompt = """You are an expert loan officer specializing in applicant profile analysis.
Your role is to thoroughly analyze an applicant's background, employment history, and creditworthiness.

When given an applicant ID, you MUST:
1. Get the applicant's profile from ApplicantDB
2. Calculate their income stability score
3. Assess their employment risk
4. Review their credit history
5. Check application completeness

Use the provided tools to gather information and provide a comprehensive profile analysis.

Output a structured analysis including:
- Income Stability Score (0-1)
- Employment Risk (LOW/MEDIUM/HIGH)
- Credit History Assessment
- Completeness Flags (if any)
- Overall Profile Strength
- Key Observations

Be thorough and objective in your analysis."""

    tools = [
        {
            "name": "get_applicant_profile",
            "description": "Retrieve applicant profile information from database",
            "input_schema": {
                "type": "object",
                "properties": {
                    "applicant_id": {
                        "type": "string",
                        "description": "The unique applicant identifier"
                    }
                },
                "required": ["applicant_id"]
            }
        },
        {
            "name": "calculate_income_stability",
            "description": "Calculate income stability score based on income and employment duration",
            "input_schema": {
                "type": "object",
                "properties": {
                    "applicant_id": {"type": "string"},
                    "income": {"type": "number"},
                    "employment_duration_years": {"type": "integer"}
                },
                "required": ["applicant_id", "income", "employment_duration_years"]
            }
        },
        {
            "name": "assess_employment_risk",
            "description": "Assess employment risk based on employment type and duration",
            "input_schema": {
                "type": "object",
                "properties": {
                    "employment_type": {"type": "string"},
                    "employment_duration_years": {"type": "integer"}
                },
                "required": ["employment_type", "employment_duration_years"]
            }
        },
        {
            "name": "get_credit_history",
            "description": "Retrieve credit history summary for applicant",
            "input_schema": {
                "type": "object",
                "properties": {
                    "applicant_id": {"type": "string"}
                },
                "required": ["applicant_id"]
            }
        },
        {
            "name": "check_application_completeness",
            "description": "Check if application has all required information",
            "input_schema": {
                "type": "object",
                "properties": {
                    "applicant_data": {
                        "type": "object",
                        "description": "The applicant data to validate"
                    }
                },
                "required": ["applicant_data"]
            }
        }
    ]

    def process_tool_call(tool_name: str, tool_input: Dict[str, Any], app_data: Dict[str, Any] = None) -> str:
        """Process tool calls from the agent"""
        from mcp_servers.applicant_db_server import (
            get_applicant_profile,
            calculate_income_stability,
            assess_employment_risk,
            get_credit_history,
            check_application_completeness
        )
        import json

        try:
            if tool_name == "get_applicant_profile":
                result = get_applicant_profile(tool_input["applicant_id"], app_data)
            elif tool_name == "calculate_income_stability":
                result = calculate_income_stability(
                    tool_input["applicant_id"],
                    tool_input["income"],
                    tool_input["employment_duration_years"]
                )
            elif tool_name == "assess_employment_risk":
                result = assess_employment_risk(
                    tool_input["employment_type"],
                    tool_input["employment_duration_years"]
                )
            elif tool_name == "get_credit_history":
                result = get_credit_history(tool_input["applicant_id"])
            elif tool_name == "check_application_completeness":
                result = check_application_completeness(tool_input["applicant_data"])
            else:
                result = {"error": f"Unknown tool: {tool_name}"}

            return json.dumps(result)
        except Exception as e:
            logger.error(f"Error processing tool {tool_name}: {e}")
            return json.dumps({"error": str(e)})

    def run_analysis(applicant_id: str, applicant_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Run the applicant profile analysis"""
        # If no applicant data provided, create from basic info
        if applicant_data is None:
            applicant_data = {}

        # Include applicant data in the context for the agent
        data_context = f"\nApplicant Data from Application:\n{applicant_data}" if applicant_data else ""

        messages = [
            {
                "role": "user",
                "content": f"Please analyze the profile for applicant {applicant_id} and provide a comprehensive assessment.{data_context}"
            }
        ]

        logger.info(f"Starting profile analysis for {applicant_id}")

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

            # Add assistant response to messages
            messages.append({"role": "assistant", "content": response.content})

            # Check if we're done
            if response.stop_reason == "end_turn":
                # Extract final text response
                for block in response.content:
                    if hasattr(block, "text"):
                        return {
                            "status": "success",
                            "analysis": block.text,
                            "applicant_id": applicant_id
                        }
                break

            # Process tool calls
            if response.stop_reason == "tool_use":
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        tool_name = block.name
                        tool_input = block.input

                        logger.info(f"Agent called tool: {tool_name}")

                        result = process_tool_call(tool_name, tool_input, applicant_data)
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result
                        })

                # Add tool results to messages
                messages.append({"role": "user", "content": tool_results})

        return {
            "status": "error",
            "message": "Max iterations reached without completion",
            "applicant_id": applicant_id
        }

    return {
        "agent_name": "ApplicantProfileAgent",
        "run": run_analysis,
        "system_prompt": system_prompt,
        "tools": tools
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    agent = create_applicant_profile_agent()

    # Test the agent
    result = agent["run"]("APP-001")
    print(f"Result: {result}")
