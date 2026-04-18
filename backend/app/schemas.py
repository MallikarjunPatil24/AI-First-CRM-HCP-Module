from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class FormData(BaseModel):
    hcp_name: Optional[str] = None
    date: Optional[str] = None
    interaction_type: Optional[str] = None
    sentiment: Optional[str] = None
    products_discussed: Optional[List[str]] = []
    materials_shared: Optional[List[str]] = []
    follow_up_required: Optional[bool] = False
    notes: Optional[str] = None


class ChatRequest(BaseModel):
    message: str
    current_form: Dict[str, Any] = {}


class ChatResponse(BaseModel):
    updated_form: Dict[str, Any]
    ai_message: str
    intent: Optional[str] = None


class SaveRequest(BaseModel):
    form_data: Dict[str, Any]


class SaveResponse(BaseModel):
    id: int
    message: str
