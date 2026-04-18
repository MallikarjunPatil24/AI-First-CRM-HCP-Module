"""
Tool 1: Log Interaction Tool
Uses LLM to extract structured HCP interaction data from free-form natural language.
NO regex or hardcoded extraction — fully LLM-driven.
"""
import json
from langchain_core.messages import HumanMessage, SystemMessage


def log_interaction_tool(user_input: str, current_form: dict, llm) -> dict:
    """
    Extract structured interaction fields from natural language using the LLM.
    Returns extracted_data, updated_form, and a response message.
    """
    today = __import__("datetime").date.today().isoformat()

    system_prompt = f"""You are a pharmaceutical CRM data extraction assistant specialized in HCP (Healthcare Professional) interactions.

Your job is to extract structured data from the user's natural language description of a medical rep–HCP interaction.

Return ONLY a valid JSON object with these exact keys:
{{
  "hcp_name": "Full name of the doctor/HCP (string or null)",
  "date": "Date of interaction in YYYY-MM-DD format. Use today's date ({today}) if not specified.",
  "interaction_type": "One of: in-person, phone, email, virtual — or null if unclear",
  "sentiment": "One of: positive, neutral, negative — infer from context",
  "products_discussed": ["array of drug/product names mentioned — empty array if none"],
  "materials_shared": ["array of brochures, samples, or materials mentioned — empty array if none"],
  "follow_up_required": true or false — true if follow-up is implied or requested,
  "notes": "A concise 1-2 sentence professional summary of the interaction"
}}

Rules:
- Use null only for fields that genuinely cannot be inferred
- Infer sentiment from words like: "positive response", "interested", "rejected", "concerned"
- If a follow-up is mentioned or implied, set follow_up_required to true
- Return ONLY the JSON object — no explanation, no markdown fences, no extra text"""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Extract interaction data from this message:\n\n{user_input}")
    ]

    response = llm.invoke(messages)
    raw = response.content.strip()

    # Strip markdown code fences if present
    if "```json" in raw:
        raw = raw.split("```json")[1].split("```")[0].strip()
    elif "```" in raw:
        raw = raw.split("```")[1].split("```")[0].strip()

    try:
        extracted = json.loads(raw)
    except json.JSONDecodeError:
        # Attempt to extract a JSON object from the response
        import re
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            try:
                extracted = json.loads(match.group())
            except Exception:
                return {
                    "extracted_data": {},
                    "updated_form": current_form,
                    "response": (
                        "I understood your message but had trouble structuring the data. "
                        "Could you please provide more details? For example: "
                        "'Met Dr. Smith today, discussed CardioMax, shared the brochure, positive response.'"
                    )
                }
        else:
            return {
                "extracted_data": {},
                "updated_form": current_form,
                "response": "I had trouble parsing the interaction. Please try again with more details."
            }

    # Merge non-null / non-empty values onto the existing form
    updated_form = dict(current_form)
    for key, value in extracted.items():
        if value is None:
            continue
        if isinstance(value, list) and len(value) == 0 and current_form.get(key):
            continue  # Don't overwrite existing list with empty
        updated_form[key] = value

    changed = [k for k in extracted if extracted[k] is not None]

    return {
        "extracted_data": extracted,
        "updated_form": updated_form,
        "response": (
            f"✅ I've logged the interaction details. "
            f"Extracted and filled: **{', '.join(changed) if changed else 'no new fields'}**. "
            f"Review the form on the left — all fields have been updated automatically."
        )
    }
