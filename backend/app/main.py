from fastapi import FastAPI

from backend.app.api.auth import router as auth_router
from backend.app.database.session import Base, engine
import backend.app.models  # Registers all models with Base.metadata

# Auto-create newly registered database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CricketIQ API",
    description="AI-Powered Cricket Strategy, Performance & Decision Intelligence Platform",
    version="0.1.0",
)

app.include_router(auth_router)


@app.get("/")
def root():
    return {"message": "Welcome to CricketIQ API"}


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "cricketiq-backend"}