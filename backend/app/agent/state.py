from typing import TypedDict, Dict, Any


class InteractionState(TypedDict):
    """
    The shared state passed through every node in the LangGraph pipeline.
    """
    user_input: str          # Raw message from the user
    intent: str              # Classified intent: log | edit | suggest | summarize | compliance
    extracted_data: Dict[str, Any]   # Data extracted or changed by the active tool
    current_form: Dict[str, Any]     # Form state at the time of the request
    updated_form: Dict[str, Any]     # Form state after tool execution
    response: str            # Human-readable AI response to display in chat
