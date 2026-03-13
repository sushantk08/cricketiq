from fastapi import FastAPI

from backend.app.api.analytics import router as analytics_router
from backend.app.api.auth import router as auth_router
from backend.app.api.matches import router as matches_router
from backend.app.api.players import router as players_router
from backend.app.api.predictions import router as predictions_router
from backend.app.api.replay import router as replay_router
from backend.app.api.scenarios import router as scenarios_router
from backend.app.database.session import Base, engine
import backend.app.models

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CricketIQ API",
    description="AI-Powered Cricket Strategy, Performance & Decision Intelligence Platform",
    version="0.1.0",
)

app.include_router(auth_router)
app.include_router(matches_router)
app.include_router(players_router)
app.include_router(predictions_router)
app.include_router(analytics_router)
app.include_router(replay_router)
app.include_router(scenarios_router)


@app.get("/")
def root():
    return {"message": "Welcome to CricketIQ API"}


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "cricketiq-backend"}