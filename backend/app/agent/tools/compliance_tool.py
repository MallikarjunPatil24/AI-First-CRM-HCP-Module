"""
Tool 4: Compliance Checker Tool
Scans interaction content for off-label promotion, unsubstantiated claims,
and other pharma regulatory compliance violations using LLM classification.
"""
import json
from langchain_core.messages import HumanMessage, SystemMessage


def compliance_check_tool(user_input: str, current_form: dict, llm) -> dict:
    """
    Perform a pharma compliance audit on the interaction data and user message.
    Returns a structured compliance report without modifying the form.
    """
    current_form_json = json.dumps(current_form, indent=2, default=str)

    system_prompt = f"""You are a senior pharmaceutical regulatory compliance officer with expertise in:
- FDA promotional regulations
- OIG pharma guidelines
- ABPI/EFPIA codes of practice
- Off-label promotion rules

Analyze the following HCP interaction record and user message for compliance issues.

Interaction Record:
{current_form_json}

Check for ALL of the following potential violations:
1. **Off-label promotion** — discussing unapproved uses of a drug
2. **Unsubstantiated efficacy claims** — claims not backed by approved labeling
3. **Missing fair balance** — not mentioning risks/side effects alongside benefits
4. **Inappropriate inducements** — gifts, meals, or benefits beyond fair market value
5. **Data privacy concerns** — improper handling of patient info
6. **Non-compliant language** — superlatives, comparatives without data support

Structure your response as:

**Overall Status:** [COMPLIANT ✅ | WARNING ⚠️ | NON-COMPLIANT 🚨]

**Issues Found:**
- List each issue clearly (or "None identified" if clean)

**Risk Level:** [LOW | MEDIUM | HIGH]

**Recommendations:**
- Specific, actionable corrective steps

Be precise, professional, and cite which aspect of the interaction triggered each finding."""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Compliance check requested for interaction. Additional context: {user_input}")
    ]

    response = llm.invoke(messages)
    content = response.content.strip()

    # Choose emoji based on detected status
    if "NON-COMPLIANT" in content.upper():
        header_emoji = "🚨"
    elif "WARNING" in content.upper():
        header_emoji = "⚠️"
    else:
        header_emoji = "✅"

    return {
        "extracted_data": {},
        "updated_form": current_form,   # Compliance check never modifies form
        "response": f"{header_emoji} **Pharma Compliance Report**\n\n{content}"
    }
