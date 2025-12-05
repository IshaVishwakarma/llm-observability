# backend/models.py

from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from sqlalchemy.sql import func
from .database import Base

class LLMRequest(Base):
    __tablename__ = "llm_requests"

    id = Column(Integer, primary_key=True, index=True)
    prompt = Column(Text, nullable=False)
    response = Column(Text)
    model = Column(String(128))
    tokens_in = Column(Integer, default=0)
    tokens_out = Column(Integer, default=0)
    latency = Column(Float)
    cost = Column(Float, default=0.0)
    status = Column(String(32), default="unknown")
    error_message = Column(Text, nullable=True)
    session_id = Column(String(128), nullable=True)

   
    feedback_rating = Column(Integer, nullable=True)
    feedback_comment = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
