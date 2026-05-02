import os
from datetime import datetime, timezone

from pymongo import MongoClient


MONGODB_URL = os.getenv(
    "MONGODB_URL",
    "mongodb://localhost:27018",
)

client = MongoClient(MONGODB_URL)

db = client["cricketiq"]

ai_reports_collection = db["ai_reports"]


def save_ai_match_report(report: dict) -> str:
    document = {
        **report,
        "created_at": datetime.now(timezone.utc),
    }

    result = ai_reports_collection.insert_one(document)
    return str(result.inserted_id)