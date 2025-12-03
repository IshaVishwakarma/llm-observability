# backend/main.py

import os
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.crud import (
    create_request_log,
    get_recent_logs,
    get_metrics_summary,
    get_token_usage_trend,
    get_latency_trend,
    get_error_trend,
    get_live_alerts,
)

from backend.database import Base, engine, SessionLocal
from backend.callbacks import MetricsCallback
from backend.models import LLMRequest

from dotenv import load_dotenv
load_dotenv()

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="LLM Observability Backend")

# --------------------------------
# CORS
# --------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://127.0.0.1",
        "http://localhost:8501",
        "http://127.0.0.1:8501",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------
# Schemas
# --------------------------------
class LLMQuery(BaseModel):
    prompt: str
    model: str = "llama-3.1-8b-instant"
    temperature: float = 0.7
    max_tokens: int = 256
    session_id: Optional[str] = None


class CompareRequest(BaseModel):
    prompt: str
    model_a: str
    model_b: str
    temperature: float = 0.7
    max_tokens: int = 256
    session_id: Optional[str] = None


class FeedbackPayload(BaseModel):
    request_id: int
    rating: Optional[int] = None
    comment: Optional[str] = None


# --------------------------------
# Health Check
# --------------------------------
@app.get("/health")
def health():
    return {"status": "ok"}


# --------------------------------
# LLM Query
# --------------------------------
@app.post("/api/v1/llm/query")
def query_llm(payload: LLMQuery):
    from langchain_groq import ChatGroq

    VALID_MODELS = {
        "llama-3.1-8b-instant",
        "llama-3.3-70b-versatile",
        "openai/gpt-oss-20b",
    }

    if payload.model not in VALID_MODELS:
        raise HTTPException(400, f"Invalid Model: {payload.model}")

    cb = MetricsCallback()

    # Initialize model
    try:
        llm = ChatGroq(
            model=payload.model,
            temperature=payload.temperature,
            max_tokens=payload.max_tokens,
            callbacks=[cb],
        )
    except Exception as e:
        raise HTTPException(500, f"LLM Init Failed: {e}")

    # Invoke model
    try:
        llm.invoke(payload.prompt)
    except Exception as e:
        log = create_request_log(
            prompt=payload.prompt,
            response="",
            model=payload.model,
            tokens_in=cb.tokens_in,
            tokens_out=cb.tokens_out,
            latency=cb.latency,
            status="error",
            session_id=payload.session_id,
            error_message=str(e),
        )
        raise HTTPException(
            status_code=500,
            detail={"message": str(e), "request_id": log.id},
        )

    # Success log
    log = create_request_log(
        prompt=payload.prompt,
        response=cb.response_text,
        model=payload.model,
        tokens_in=cb.tokens_in,
        tokens_out=cb.tokens_out,
        latency=cb.latency,
        status="success",
        session_id=payload.session_id,
        cost=0.0,
    )

    return {
        "request_id": log.id,
        "response": cb.response_text,
        "tokens_in": cb.tokens_in,
        "tokens_out": cb.tokens_out,
        "latency_ms": cb.latency,
    }


# --------------------------------
# Compare Models
# --------------------------------
@app.post("/api/v1/llm/compare")
def compare_models(payload: CompareRequest):
    from langchain_groq import ChatGroq

    VALID_MODELS = {
        "llama-3.1-8b-instant",
        "llama-3.3-70b-versatile",
        "openai/gpt-oss-20b",
    }

    if payload.model_a not in VALID_MODELS or payload.model_b not in VALID_MODELS:
        raise HTTPException(400, "Invalid model selected")

    # A
    cb_a = MetricsCallback()
    llm_a = ChatGroq(
        model=payload.model_a,
        temperature=payload.temperature,
        max_tokens=payload.max_tokens,
        callbacks=[cb_a],
    )
    llm_a.invoke(payload.prompt)

    # B
    cb_b = MetricsCallback()
    llm_b = ChatGroq(
        model=payload.model_b,
        temperature=payload.temperature,
        max_tokens=payload.max_tokens,
        callbacks=[cb_b],
    )
    llm_b.invoke(payload.prompt)

    # Store logs
    create_request_log(
        prompt=payload.prompt,
        response=cb_a.response_text,
        model=payload.model_a,
        tokens_in=cb_a.tokens_in,
        tokens_out=cb_a.tokens_out,
        latency=cb_a.latency,
        status="success",
        session_id=payload.session_id,
    )

    create_request_log(
        prompt=payload.prompt,
        response=cb_b.response_text,
        model=payload.model_b,
        tokens_in=cb_b.tokens_in,
        tokens_out=cb_b.tokens_out,
        latency=cb_b.latency,
        status="success",
        session_id=payload.session_id,
    )

    return {
        "model_a": {
            "name": payload.model_a,
            "response": cb_a.response_text,
            "tokens_in": cb_a.tokens_in,
            "tokens_out": cb_a.tokens_out,
            "latency": cb_a.latency,
        },
        "model_b": {
            "name": payload.model_b,
            "response": cb_b.response_text,
            "tokens_in": cb_b.tokens_in,
            "tokens_out": cb_b.tokens_out,
            "latency": cb_b.latency,
        },
    }


# --------------------------------
# Logs & Metrics Endpoints
# --------------------------------
@app.get("/api/v1/logs")
def read_logs(limit: int = 50):
    return {"ok": True, "logs": get_recent_logs(limit)}


@app.get("/api/v1/metrics/summary")
def metrics_summary():
    return get_metrics_summary()


@app.get("/api/v1/metrics/token-trend")
def token_trend(limit: int = 50):
    return {"data": get_token_usage_trend(limit)}


@app.get("/api/v1/metrics/latency-trend")
def latency_trend(limit: int = 50):
    return {"data": get_latency_trend(limit)}


@app.get("/api/v1/metrics/error-trend")
def error_trend(limit: int = 50):
    return {"data": get_error_trend(limit)}


@app.get("/api/v1/alerts")
def alerts():
    return {"alerts": get_live_alerts()}


# --------------------------------
# User Analytics
# --------------------------------
@app.get("/api/v1/user/analytics/{session_id}")
def user_analytics(session_id: str):
    from sqlalchemy import func
    db = SessionLocal()

    try:
        total_requests = db.query(func.count(LLMRequest.id))\
            .filter(LLMRequest.session_id == session_id).scalar() or 0

        total_tokens = db.query(
            func.sum(LLMRequest.tokens_in + LLMRequest.tokens_out)
        ).filter(LLMRequest.session_id == session_id).scalar() or 0

        avg_latency = db.query(
            func.avg(LLMRequest.latency)
        ).filter(LLMRequest.session_id == session_id).scalar()

        top_model = db.query(
            LLMRequest.model, func.count(LLMRequest.model)
        ).filter(LLMRequest.session_id == session_id)\
         .group_by(LLMRequest.model)\
         .order_by(func.count(LLMRequest.model).desc())\
         .first()

        return {
            "session_id": session_id,
            "total_requests": total_requests,
            "total_tokens": total_tokens,
            "avg_latency_ms": round(avg_latency, 2) if avg_latency else 0,
            "top_model": top_model[0] if top_model else None,
        }
    finally:
        db.close()


# --------------------------------
# Feedback Endpoint (FIXED)
# --------------------------------
@app.post("/api/v1/llm/feedback")
def submit_feedback(payload: FeedbackPayload):
    db = SessionLocal()
    try:
        log = db.query(LLMRequest).filter(LLMRequest.id == payload.request_id).first()

        if not log:
            raise HTTPException(404, "Request ID not found")

        log.feedback_rating = payload.rating
        log.feedback_comment = payload.comment

        db.commit()
        return {"ok": True, "message": "Feedback saved"}
    finally:
        db.close()
