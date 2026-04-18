from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Date
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from .database import Base


class Interaction(Base):
    """
    ORM model for the `interactions` table.

    Matches the PostgreSQL schema:
        interactions(
            id SERIAL PRIMARY KEY,
            hcp_name TEXT,
            date DATE,
            interaction_type TEXT,
            sentiment TEXT,
            products JSONB,
            materials JSONB,
            follow_up BOOLEAN,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    hcp_name = Column(Text, nullable=True)
    date = Column(Date, nullable=True)
    interaction_type = Column(String(50), nullable=True)
    sentiment = Column(String(20), nullable=True)
    products = Column(JSONB, nullable=True, default=list)
    materials = Column(JSONB, nullable=True, default=list)
    follow_up = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
