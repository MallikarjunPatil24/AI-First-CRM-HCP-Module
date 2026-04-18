"""
FastAPI Application Entry Point
AI-First CRM – HCP Interaction Module
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from .db.database import create_tables
from .routes.chat import router as chat_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: create DB tables on startup."""
    create_tables()
    print("[OK] Database tables initialized")
    yield
    print("[--] Shutting down...")


app = FastAPI(
    title="AI-First CRM – HCP Interaction Module",
    description=(
        "LangGraph + Groq powered pharma CRM where the AI controls all "
        "form fields through natural language conversations."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# ─── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routes ───────────────────────────────────────────────────────────────────
app.include_router(chat_router)


@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "running",
        "service": "AI-First CRM – HCP Interaction Module",
        "docs": "/docs",
    }
