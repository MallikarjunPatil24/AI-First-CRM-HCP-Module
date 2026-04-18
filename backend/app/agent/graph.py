"""
LangGraph StateGraph Definition
Assembles and compiles the AI agent pipeline:

  START → intent_classifier → [conditional routing via intent_router]
        → log_tool | edit_tool | suggest_tool | summary_tool | compliance_tool
        → END
"""
from langgraph.graph import StateGraph, END, START

from .state import InteractionState
from .nodes import (
    intent_classifier_node,
    intent_router,
    log_tool_node,
    edit_tool_node,
    suggest_tool_node,
    compliance_tool_node,
    summary_tool_node,
)


def build_graph() -> object:
    """Build and compile the LangGraph StateGraph."""
    builder = StateGraph(InteractionState)

    # ── Register Nodes ─────────────────────────────────────────────────────
    builder.add_node("intent_classifier", intent_classifier_node)
    builder.add_node("log_tool",          log_tool_node)
    builder.add_node("edit_tool",         edit_tool_node)
    builder.add_node("suggest_tool",      suggest_tool_node)
    builder.add_node("compliance_tool",   compliance_tool_node)
    builder.add_node("summary_tool",      summary_tool_node)

    # ── Entry Point ─────────────────────────────────────────────────────────
    builder.set_entry_point("intent_classifier")

    # ── Conditional Routing: intent → tool node ────────────────────────────
    builder.add_conditional_edges(
        "intent_classifier",
        intent_router,          # returns the intent string from state
        {
            "log":        "log_tool",
            "edit":       "edit_tool",
            "suggest":    "suggest_tool",
            "summarize":  "summary_tool",
            "compliance": "compliance_tool",
        }
    )

    # ── Terminal Edges: all tools → END ────────────────────────────────────
    builder.add_edge("log_tool",        END)
    builder.add_edge("edit_tool",       END)
    builder.add_edge("suggest_tool",    END)
    builder.add_edge("summary_tool",    END)
    builder.add_edge("compliance_tool", END)

    return builder.compile()


# Compile once at import time; reused across all requests (thread-safe)
compiled_graph = build_graph()
