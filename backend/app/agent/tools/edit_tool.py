"""
Tool 2: Edit Interaction Tool
Uses LLM to identify which specific fields the user wants to change,
then merges only those fields — leaving everything else intact.
"""
import json
import re
from langchain_core.messages import HumanMessage, SystemMessage


def edit_interaction_tool(user_input: str, current_form: dict, llm) -> dict:
    """
    Detect and apply targeted field edits from a user's natural language request.
    Only mutates the fields the user explicitly requested — preserves the rest.
    """
    current_form_json = json.dumps(current_form, indent=2, default=str)

    system_prompt = f"""You are a pharmaceutical CRM form editor assistant.

The user wants to update specific fields in an existing HCP interaction record.

Current form state:
{current_form_json}

Based on the user's edit request, return ONLY a JSON object containing the fields to change.
Include ONLY the fields the user explicitly mentioned — do NOT include unchanged fields.

Valid fields and their constraints:
- hcp_name: string
- date: string in YYYY-MM-DD format
- interaction_type: must be one of [in-person, phone, email, virtual]
- sentiment: must be one of [positive, neutral, negative]
- products_discussed: array of strings
- materials_shared: array of strings
- follow_up_required: boolean (true or false)
- notes: string

Return ONLY the JSON object with fields to update. No explanation, no markdown fences."""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"User edit request: {user_input}")
    ]

    response = llm.invoke(messages)
    raw = response.content.strip()

    # Strip markdown fences
    if "```json" in raw:
        raw = raw.split("```json")[1].split("```")[0].strip()
    elif "```" in raw:
        raw = raw.split("```")[1].split("```")[0].strip()

    try:
        changes = json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            try:
                changes = json.loads(match.group())
            except Exception:
                return {
                    "extracted_data": {},
                    "updated_form": current_form,
                    "response": (
                        "I couldn't parse your edit request. "
                        "Try something like: 'Change the sentiment to positive' "
                        "or 'Update the date to 2024-02-10'."
                    )
                }
        else:
            return {
                "extracted_data": {},
                "updated_form": current_form,
                "response": "Please be more specific about what you'd like to change and how."
            }

    # Apply only the identified changes
    valid_keys = {
        "hcp_name", "date", "interaction_type", "sentiment",
        "products_discussed", "materials_shared", "follow_up_required", "notes"
    }
    updated_form = dict(current_form)
    applied = {}
    for key, value in changes.items():
        if key in valid_keys:
            updated_form[key] = value
            applied[key] = value

    if not applied:
        return {
            "extracted_data": {},
            "updated_form": current_form,
            "response": "I couldn't identify any valid field to update. Please specify a known field."
        }

    changed_fields = list(applied.keys())
    return {
        "extracted_data": applied,
        "updated_form": updated_form,
        "response": (
            f"✏️ Updated field(s): **{', '.join(changed_fields)}**. "
            f"All other fields remain unchanged."
        )
    }
