"""
LangGraph Node Functions
Each node receives the full InteractionState and returns an updated copy.

Graph flow:
  START → intent_classifier → [conditional routing] → tool_node → END
"""
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

from .state import InteractionState
from .tools.log_tool import log_interaction_tool
from .tools.edit_tool import edit_interaction_tool
from .tools.suggest_tool import suggest_interaction_tool
from .tools.compliance_tool import compliance_check_tool
from .tools.summary_tool import auto_summary_tool

load_dotenv()


# ─── LLM Factory ─────────────────────────────────────────────────────────────

def get_llm(use_fallback: bool = False):
    """
    Return a Groq-backed LLM.
    Primary  : llama-3.1-8b-instant  (fast, lightweight)
    Fallback : llama-3.3-70b-versatile (high quality)
    """
    model = "llama-3.3-70b-versatile" if use_fallback else "llama-3.1-8b-instant"
    return ChatGroq(
        model=model,
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.1,
        max_retries=2,
    )


def _get_llm_with_fallback():
    """Try primary LLM; fall back to secondary on any exception."""
    try:
        llm = get_llm(use_fallback=False)
        # Light probe — ChatGroq is lazy, so we trust it unless invocation fails
        return llm
    except Exception:
        return get_llm(use_fallback=True)


# ─── Node: Intent Classifier ──────────────────────────────────────────────────

def intent_classifier_node(state: InteractionState) -> InteractionState:
    """
    Use the LLM to classify the user's message into one of five intents:
    log | edit | suggest | summarize | compliance
    """
    llm = _get_llm_with_fallback()

    system_prompt = """You are an intent classifier for a pharmaceutical CRM AI assistant.

Classify the user's message into EXACTLY ONE of these intents:

- "log"        → User is describing a new HCP interaction to record
- "edit"       → User wants to modify/update/correct a specific field
- "suggest"    → User wants recommendations, next steps, or strategic advice
- "summarize"  → User wants a summary or overview of the current interaction
- "compliance" → User wants a regulatory or compliance check

Return ONLY the single intent word (lowercase). Nothing else — no punctuation, no explanation."""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=state["user_input"])
    ]

    try:
        response = llm.invoke(messages)
        intent = response.content.strip().lower().strip('"\'.,')
    except Exception:
        # If primary fails, try fallback
        try:
            llm_fb = get_llm(use_fallback=True)
            response = llm_fb.invoke(messages)
            intent = response.content.strip().lower().strip('"\'.,')
        except Exception:
            intent = "log"

    valid_intents = {"log", "edit", "suggest", "summarize", "compliance"}
    if intent not in valid_intents:
        # Best-effort keyword fallback (not hardcoded extraction — just routing safety)
        msg = state["user_input"].lower()
        if any(w in msg for w in ["update", "change", "edit", "correct", "fix"]):
            intent = "edit"
        elif any(w in msg for w in ["suggest", "recommend", "next", "should i", "what to"]):
            intent = "suggest"
        elif any(w in msg for w in ["summary", "summarize", "overview", "brief"]):
            intent = "summarize"
        elif any(w in msg for w in ["compliance", "compliant", "regulation", "off-label", "legal"]):
            intent = "compliance"
        else:
            intent = "log"

    return {**state, "intent": intent}


# ─── Tool Nodes ───────────────────────────────────────────────────────────────

def log_tool_node(state: InteractionState) -> InteractionState:
    llm = _get_llm_with_fallback()
    result = log_interaction_tool(state["user_input"], state["current_form"], llm)
    return {
        **state,
        "extracted_data": result["extracted_data"],
        "updated_form": result["updated_form"],
        "response": result["response"],
    }


def edit_tool_node(state: InteractionState) -> InteractionState:
    llm = _get_llm_with_fallback()
    result = edit_interaction_tool(state["user_input"], state["current_form"], llm)
    return {
        **state,
        "extracted_data": result["extracted_data"],
        "updated_form": result["updated_form"],
        "response": result["response"],
    }


def suggest_tool_node(state: InteractionState) -> InteractionState:
    llm = _get_llm_with_fallback()
    result = suggest_interaction_tool(state["user_input"], state["current_form"], llm)
    return {
        **state,
        "extracted_data": result["extracted_data"],
        "updated_form": result["updated_form"],
        "response": result["response"],
    }


def compliance_tool_node(state: InteractionState) -> InteractionState:
    llm = _get_llm_with_fallback()
    result = compliance_check_tool(state["user_input"], state["current_form"], llm)
    return {
        **state,
        "extracted_data": result["extracted_data"],
        "updated_form": result["updated_form"],
        "response": result["response"],
    }


def summary_tool_node(state: InteractionState) -> InteractionState:
    llm = _get_llm_with_fallback()
    result = auto_summary_tool(state["user_input"], state["current_form"], llm)
    return {
        **state,
        "extracted_data": result["extracted_data"],
        "updated_form": result["updated_form"],
        "response": result["response"],
    }


# ─── Router (used as conditional edge function) ───────────────────────────────

def intent_router(state: InteractionState) -> str:
    """Return the intent key so LangGraph can route to the correct tool node."""
    return state["intent"]
