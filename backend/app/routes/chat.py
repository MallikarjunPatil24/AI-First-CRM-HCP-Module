"""
API Routes: /chat and /save
All business logic lives in the LangGraph agent — routes are thin adapters.
"""
from datetime import date as date_type
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from ..schemas import ChatRequest, ChatResponse, SaveRequest, SaveResponse
from ..agent.graph import compiled_graph
from ..db.database import get_db
from ..db.models import Interaction

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Accepts a user message + current form state, runs the LangGraph pipeline,
    returns the AI-updated form and a human-readable response message.
    """
    try:
        initial_state = {
            "user_input":     request.message,
            "intent":         "",
            "extracted_data": {},
            "current_form":   request.current_form,
            "updated_form":   request.current_form,
            "response":       "",
        }

        result = compiled_graph.invoke(initial_state)

        return ChatResponse(
            updated_form=result.get("updated_form", request.current_form),
            ai_message=result.get("response", "Request processed."),
            intent=result.get("intent", ""),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Agent error: {str(exc)}"
        )


@router.post("/save", response_model=SaveResponse)
async def save_interaction(request: SaveRequest, db: Session = Depends(get_db)):
    """
    Persist the finalized interaction form to PostgreSQL.
    """
    try:
        form = request.form_data

        # Parse date string to Python date object
        interaction_date = None
        if form.get("date"):
            try:
                interaction_date = date_type.fromisoformat(form["date"])
            except (ValueError, TypeError):
                interaction_date = None

        interaction = Interaction(
            hcp_name=form.get("hcp_name"),
            date=interaction_date,
            interaction_type=form.get("interaction_type"),
            sentiment=form.get("sentiment"),
            products=form.get("products_discussed", []),
            materials=form.get("materials_shared", []),
            follow_up=bool(form.get("follow_up_required", False)),
            notes=form.get("notes"),
        )

        db.add(interaction)
        db.commit()
        db.refresh(interaction)

        return SaveResponse(
            id=interaction.id,
            message=f"Interaction saved successfully (ID: {interaction.id})"
        )

    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(exc)}"
        )


@router.get("/interactions")
async def list_interactions(db: Session = Depends(get_db)):
    """List all saved interactions (for debugging / future use)."""
    interactions = db.query(Interaction).order_by(Interaction.created_at.desc()).limit(50).all()
    return [
        {
            "id": i.id,
            "hcp_name": i.hcp_name,
            "date": i.date.isoformat() if i.date else None,
            "interaction_type": i.interaction_type,
            "sentiment": i.sentiment,
            "products": i.products,
            "materials": i.materials,
            "follow_up": i.follow_up,
            "notes": i.notes,
            "created_at": i.created_at.isoformat() if i.created_at else None,
        }
        for i in interactions
    ]
