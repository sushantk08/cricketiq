from fastapi import FastAPI

app = FastAPI(
    title="CricketIQ API",
    description="AI-Powered Cricket Strategy, Performance & Decision Intelligence Platform",
    version="0.1.0",
)


@app.get("/")
def root():
    return {"message": "Welcome to CricketIQ API"}


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "cricketiq-backend"}