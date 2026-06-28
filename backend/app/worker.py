import os

from celery import Celery

from backend.app.database.mongodb import save_ai_match_report
from backend.app.database.session import SessionLocal
from backend.app.services.ai_service import generate_match_analysis


REDIS_URL = os.getenv(
    "REDIS_URL",
    "redis://localhost:6379/0",
)

celery_app = Celery(
    "cricketiq",
    broker=REDIS_URL,
    backend=REDIS_URL,
)


@celery_app.task(name="cricketiq.health_check")
def health_check() -> dict:
    """Simple background task used to verify Celery/Redis execution."""
    return {
        "status": "healthy",
        "service": "cricketiq-celery-worker",
    }


@celery_app.task(
    name="cricketiq.generate_match_report",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def generate_match_report(self, match_id: int) -> dict:
    """
    Generate an AI-assisted match report in the background
    and persist it to MongoDB.
    """
    db = SessionLocal()

    try:
        report = generate_match_analysis(db, match_id)

        if not report:
            return {
                "status": "not_found",
                "match_id": match_id,
                "report_id": None,
            }

        report_id = save_ai_match_report(
            report.model_dump()
        )

        return {
            "status": "completed",
            "match_id": match_id,
            "report_id": str(report_id),
        }

    finally:
        db.close()