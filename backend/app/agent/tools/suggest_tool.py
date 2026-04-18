"""
Tool 3: Smart Suggestion Tool
Analyzes current interaction state and recommends next best actions
(follow-up scheduling, sample dispatch, educational material sharing, etc.)
"""
import json
import re
from langchain_core.messages import HumanMessage, SystemMessage


def suggest_interaction_tool(user_input: str, current_form: dict, llm) -> dict:
    """
    Generate context-aware next-step recommendations based on the current interaction form.
    May lightly update follow_up_required or notes if appropriate.
    """
    current_form_json = json.dumps(current_form, indent=2, default=str)

    system_prompt = f"""You are a pharmaceutical sales strategy advisor with deep expertise in HCP engagement.

Based on the current HCP interaction data below, provide smart, actionable next-step recommendations.

Current interaction data:
{current_form_json}

User's question/context: {{user_input}}

Provide:
1. 3–5 specific, prioritized recommendations tailored to the interaction
2. Consider: follow-up timing, samples, educational materials, digital touchpoints
3. Be professional, concise, and pharma-industry-specific

At the end of your response, include a JSON block with any form field updates (ONLY if necessary):

JSON_UPDATE:
{{"follow_up_required": true/false, "notes": "append to existing notes if needed — or null"}}

Format your recommendations as a clean numbered list. Be conversational but professional."""

    messages = [
        SystemMessage(content=system_prompt.replace("{user_input}", user_input)),
        HumanMessage(content=f"Current interaction context:\n{current_form_json}\n\nUser: {user_input}")
    ]

    response = llm.invoke(messages)
    content = response.content.strip()

    # Split off any JSON_UPDATE block
    updated_form = dict(current_form)
    ai_message = content

    if "JSON_UPDATE:" in content:
        parts = content.split("JSON_UPDATE:", 1)
        ai_message = parts[0].strip()
        json_str = parts[1].strip()
        # Strip fences
        if "```" in json_str:
            json_str = re.sub(r'```[a-z]*', '', json_str).replace("```", "").strip()
        try:
            updates = json.loads(json_str)
            for key, value in updates.items():
                if key in updated_form and value is not None:
                    # For notes: append rather than replace
                    if key == "notes" and updated_form.get("notes"):
                        updated_form["notes"] = updated_form["notes"] + " | " + str(value)
                    else:
                        updated_form[key] = value
        except (json.JSONDecodeError, Exception):
            pass  # Non-critical — suggestions still shown

    return {
        "extracted_data": {},
        "updated_form": updated_form,
        "response": f"💡 **Smart Suggestions**\n\n{ai_message}"
    }
