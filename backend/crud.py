# backend/crud.py

from backend.database import SessionLocal
from backend.models import LLMRequest
from sqlalchemy import desc, func


def get_recent_logs(limit: int = 100):
    """
    Return most recent `limit` logs as list of dicts.
    """
    db = SessionLocal()
    try:
        rows = (
            db.query(LLMRequest)
            .order_by(desc(LLMRequest.created_at))
            .limit(limit)
            .all()
        )
        result = []
        for r in rows:
            result.append({
                "id": r.id,
                "prompt": (r.prompt[:300] + "...") if r.prompt and len(r.prompt) > 300 else (r.prompt or ""),
                "model": r.model,
                "status": r.status,
                "tokens_in": r.tokens_in,
                "tokens_out": r.tokens_out,
                "latency": r.latency,
                "error_message": r.error_message,
                "session_id": getattr(r, "session_id", None),
               "created_at": r.created_at.isoformat() if r.created_at else None,

               "feedback_rating": r.feedback_rating,
               "feedback_comment": r.feedback_comment

            })
        return result

    finally:
        db.close()


def create_request_log(prompt, response, model, tokens_in, tokens_out,
                       latency, status, session_id=None, error_message=None,
                       cost=0.0):
    """
    Persist a request log and return the SQLAlchemy model instance.
    """
    db = SessionLocal()
    try:
        log = LLMRequest(
            prompt=prompt,
            response=response,
            model=model,
            tokens_in=tokens_in or 0,
            tokens_out=tokens_out or 0,
            latency=latency or 0.0,
            status=status,
            error_message=error_message,
            cost=cost,
            session_id=session_id,
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log

    finally:
        db.close()


def get_metrics_summary():
    """
    Return aggregated metrics summary for the dashboard.
    """
    db = SessionLocal()
    try:
        total_requests = db.query(func.count(LLMRequest.id)).scalar() or 0
        total_success = db.query(func.count(LLMRequest.id)) \
            .filter(LLMRequest.status == "success").scalar() or 0
        total_errors = db.query(func.count(LLMRequest.id)) \
            .filter(LLMRequest.status == "error").scalar() or 0

        avg_latency = db.query(func.avg(LLMRequest.latency)).scalar() or 0
        max_latency = db.query(func.max(LLMRequest.latency)).scalar() or 0

        tokens_in = db.query(func.sum(LLMRequest.tokens_in)).scalar() or 0
        tokens_out = db.query(func.sum(LLMRequest.tokens_out)).scalar() or 0

        most_used_model = (
            db.query(LLMRequest.model, func.count(LLMRequest.model))
            .group_by(LLMRequest.model)
            .order_by(func.count(LLMRequest.model).desc())
            .first()
        )

        return {
            "total_requests": total_requests,
            "total_success": total_success,
            "total_errors": total_errors,
            "success_rate": round((total_success / total_requests) * 100, 2) if total_requests else 0,
            "error_rate": round((total_errors / total_requests) * 100, 2) if total_requests else 0,
            "avg_latency_ms": round(avg_latency, 2),
            "max_latency_ms": round(max_latency, 2),
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "most_used_model": most_used_model[0] if most_used_model else None
        }

    finally:
        db.close()


def get_token_usage_trend(limit: int = 50):
    """
    Return recent token usage rows (latest first).
    """
    db = SessionLocal()
    try:
        rows = (
            db.query(
                LLMRequest.created_at,
                LLMRequest.tokens_in,
                LLMRequest.tokens_out,
                LLMRequest.model,
                LLMRequest.latency,
                LLMRequest.status,
            )
            .order_by(desc(LLMRequest.created_at))
            .limit(limit)
            .all()
        )

        data = []
        for row in rows:
            data.append({
                "timestamp": row.created_at.isoformat() if row.created_at else None,
                "tokens_in": row.tokens_in,
                "tokens_out": row.tokens_out,
                "model": row.model,
                "latency": row.latency,
                "status": row.status,
            })

        return data

    finally:
        db.close()


def get_latency_trend(limit: int = 50):
    """
    Return recent latency logs.
    """
    db = SessionLocal()
    try:
        rows = (
            db.query(
                LLMRequest.created_at,
                LLMRequest.latency,
                LLMRequest.model,
                LLMRequest.status,
            )
            .order_by(desc(LLMRequest.created_at))
            .limit(limit)
            .all()
        )

        data = []
        for row in rows:
            data.append({
                "timestamp": row.created_at.isoformat() if row.created_at else None,
                "latency_ms": row.latency,
                "model": row.model,
                "status": row.status,
            })

        return data

    finally:
        db.close()


def get_error_trend(limit: int = 50):
    """
    Return recent error logs.
    """
    db = SessionLocal()
    try:
        rows = (
            db.query(
                LLMRequest.created_at,
                LLMRequest.error_message,
                LLMRequest.model,
            )
            .filter(LLMRequest.status == "error")
            .order_by(desc(LLMRequest.created_at))
            .limit(limit)
            .all()
        )

        data = []
        for row in rows:
            data.append({
                "timestamp": row.created_at.isoformat() if row.created_at else None,
                "error_message": row.error_message,
                "model": row.model,
            })

        return data

    finally:
        db.close()


def get_live_alerts():
    """
    Basic alert system.
    """
    db = SessionLocal()
    alerts = []

    try:
        # High latency
        high_latency = (
            db.query(LLMRequest)
            .filter(LLMRequest.latency != None)
            .filter(LLMRequest.latency > 3000)
            .order_by(desc(LLMRequest.created_at))
            .first()
        )
        if high_latency:
            alerts.append({
                "type": "latency",
                "message": f"High latency detected: {high_latency.latency} ms",
                "timestamp": high_latency.created_at.isoformat() if high_latency.created_at else None,
            })

        # Error rate
        total = db.query(func.count(LLMRequest.id)).scalar() or 0
        errors = db.query(func.count(LLMRequest.id)) \
            .filter(LLMRequest.status == "error").scalar() or 0

        if total and (errors / total) * 100 > 30:
            alerts.append({
                "type": "error_rate",
                "message": f"High error rate detected: {round((errors/total)*100, 2)}%",
            })

        # Token spike
        token_spike = (
            db.query(LLMRequest)
            .filter((LLMRequest.tokens_in > 1000) | (LLMRequest.tokens_out > 2000))
            .order_by(desc(LLMRequest.created_at))
            .first()
        )
        if token_spike:
            alerts.append({
                "type": "token_spike",
                "message": f"Token spike detected (IN: {token_spike.tokens_in}, OUT: {token_spike.tokens_out})",
                "timestamp": token_spike.created_at.isoformat() if token_spike.created_at else None,
            })

        return alerts

    finally:
        db.close()

def update_feedback(request_id: int, rating: int | None, comment: str | None):
    db = SessionLocal()
    try:
        log = db.query(LLMRequest).filter(LLMRequest.id == request_id).first()
        if not log:
            return False

        log.feedback_rating = rating
        log.feedback_comment = comment
        db.commit()
        return True
    finally:
        db.close()

