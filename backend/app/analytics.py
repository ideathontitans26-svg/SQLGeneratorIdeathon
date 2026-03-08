"""Analytics service for query generation performance monitoring."""
from datetime import datetime, timedelta
from sqlalchemy import func, and_
from sqlalchemy.orm import Session
from .models import QueryRecord


def get_analytics_summary(db: Session, days: int = 7) -> dict:
    """Get analytics summary for the dashboard."""
    since = datetime.utcnow() - timedelta(days=days)
    
    total = db.query(QueryRecord).count()
    successful = db.query(QueryRecord).filter(QueryRecord.success == True).count()
    success_rate = (successful / total * 100) if total > 0 else 0
    
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    queries_today = db.query(QueryRecord).filter(QueryRecord.created_at >= today_start).count()
    
    by_model = db.query(QueryRecord.model_used, func.count(QueryRecord.id)).filter(
        QueryRecord.created_at >= since
    ).group_by(QueryRecord.model_used).all()
    queries_by_model = {m: c for m, c in by_model}
    
    avg_time = db.query(func.avg(QueryRecord.execution_time_ms)).filter(
        QueryRecord.execution_time_ms.isnot(None)
    ).scalar()
    
    recent = db.query(QueryRecord).order_by(QueryRecord.created_at.desc()).limit(10).all()
    
    return {
        "total_queries": total,
        "success_rate": round(success_rate, 1),
        "queries_by_model": queries_by_model,
        "queries_today": queries_today,
        "avg_execution_time_ms": round(avg_time, 1) if avg_time else None,
        "recent_queries": [
            {
                "id": r.id,
                "prompt": r.prompt[:80] + "..." if len(r.prompt) > 80 else r.prompt,
                "model_used": r.model_used,
                "success": r.success,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in recent
        ]
    }
