"""
Tool 5: Auto Summary Tool
Generates a concise, professional narrative summary of the current
HCP interaction and optionally populates the notes field if empty.
"""
import json
from langchain_core.messages import HumanMessage, SystemMessage


def auto_summary_tool(user_input: str, current_form: dict, llm) -> dict:
    """
    Generate a polished interaction summary from the current form state.
    If notes field is empty, auto-populates it with the summary.
    """
    current_form_json = json.dumps(current_form, indent=2, default=str)

    system_prompt = f"""You are a pharmaceutical CRM documentation specialist.

Generate a concise, professional summary of the following HCP interaction record.

Interaction Data:
{current_form_json}

Requirements:
- Write 2–4 sentences in professional, past-tense narrative style
- Include: HCP name, date, interaction type, products discussed
- Reflect the sentiment and mention follow-up if required
- Be specific — avoid filler phrases
- Write as if recording in an official pharma CRM system

After the summary, on a new line add:
SHOULD_UPDATE_NOTES: YES or NO
(YES only if the current notes field is empty or significantly less detailed than your summary)"""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Generate summary. Context: {user_input}")
    ]

    response = llm.invoke(messages)
    raw = response.content.strip()

    # Parse SHOULD_UPDATE_NOTES directive
    should_update = False
    summary = raw

    if "SHOULD_UPDATE_NOTES:" in raw:
        parts = raw.split("SHOULD_UPDATE_NOTES:", 1)
        summary = parts[0].strip()
        directive = parts[1].strip().upper()
        should_update = directive.startswith("YES")

    # Update notes field if warranted
    updated_form = dict(current_form)
    if should_update and not current_form.get("notes"):
        updated_form["notes"] = summary

    return {
        "extracted_data": {},
        "updated_form": updated_form,
        "response": f"📋 **Interaction Summary**\n\n{summary}"
    }
