# CricketIQ

AI-Powered Cricket Strategy, Performance & Decision Intelligence Platform.

CricketIQ is a full-stack cricket intelligence platform designed to help fans, analysts, coaches, and cricket teams understand:

> **What is happening? Why is it happening? What could happen next? What tactical options are available?**

The platform combines historical ball-by-ball cricket data, statistical analytics, machine learning, scenario simulation, matchup intelligence, turning-point detection, counterfactual analysis, and AI-assisted reporting into a single application.

---

## Features

- Match analytics and scorecards
- Ball-by-ball delivery analysis
- Historical player intelligence
- Batter vs bowler matchup analysis
- Player comparison
- Win probability prediction
- Match win-probability curves
- Turning Point Detection
- Counterfactual Decision Replay
- Scenario Simulator
- Bowling Strategy recommendations
- Batting Strategy recommendations
- Strategy Lab
- AI-powered match analysis
- AI-powered player analysis
- Natural-language AI Analyst
- External cricket API integration
- Role-based authentication
- Admin verification workflow
- PostgreSQL relational database
- MongoDB document storage
- Dockerized full-stack deployment
- GitHub Actions CI/CD validation
- Historical Cricsheet data processing

---

# Architecture

```text
                           CricketIQ
                               │
                 ┌─────────────┴─────────────┐
                 │                           │
          React Frontend              FastAPI Backend
                 │                           │
          React Router                REST API Layer
                 │                           │
                 └─────────────┬─────────────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
                ▼              ▼              ▼
           PostgreSQL      MongoDB       Historical
           Relational      AI Reports    Cricket Data
                │              │              │
                └──────────────┼──────────────┘
                               │
                       Analytics / ML Layer
                               │
              ┌────────────────┼────────────────┐
              │                │                │
           Pandas /         NumPy /        scikit-learn
           Analytics         Models          ML Models
```

---

# Technology Stack

## Backend

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic
- PostgreSQL
- MongoDB
- PyMongo
- JWT Authentication
- Pandas
- NumPy
- scikit-learn
- pytest

## Frontend

- React
- JavaScript
- React Router
- HTML
- CSS
- Framer Motion
- Lucide React
- Recharts
- Vite

## Infrastructure

- Docker
- Docker Compose
- Nginx
- GitHub Actions
- Google Cloud Platform for production deployment

---

# Project Structure

```text
cricketiq/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── data/
│   │   ├── database/
│   │   ├── integrations/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   │
│   ├── data/
│   │   └── historical/
│   │
│   ├── migrations/
│   ├── tests/
│   ├── Dockerfile
│   ├── alembic.ini
│   └── requirements.txt
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── assets/
│   │   ├── components/
│   │   ├── context/
│   │   ├── pages/
│   │   └── services/
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── docker-compose.yml
├── .env.example
├── pytest.ini
└── README.md
```

---

# Core Modules

## 1. Match Intelligence

CricketIQ provides detailed match-level and ball-by-ball analysis.

Users can inspect:

- Match overview
- Teams
- Venue
- Scorecard
- Innings
- Deliveries
- Batting statistics
- Bowling statistics
- Win probability progression
- Turning points

### API

```text
GET /api/matches
GET /api/matches/{id}
GET /api/matches/{id}/scorecard
GET /api/matches/{id}/deliveries
GET /api/predictions/matches/{id}/curve
```

---

# 2. Win Probability

CricketIQ includes a historical T20 win-probability model.

The model uses match-state variables such as:

- Runs required
- Balls remaining
- Wickets in hand
- Match progression

### API

```text
POST /api/predictions/win-probability
```

The application can also generate ball-by-ball win-probability curves for a match.

### Model Evaluation

The historical model has been evaluated chronologically using historical training data followed by later test data.

Current verified evaluation:

```text
Accuracy: 84.38%
Brier Score: 0.10976
```

These metrics describe the evaluated historical dataset and should not be interpreted as a guarantee of future prediction performance.

---

# 3. Turning Point Detection

Turning Point Detection identifies significant changes in match momentum.

Signals can include:

- Win-probability changes
- Wickets
- Boundary momentum
- High-leverage deliveries
- Major positive momentum shifts
- Major negative momentum shifts

### API

```text
GET /api/matches/{id}/turning-points
```

The detector ranks meaningful events instead of treating every delivery as a turning point.

---

# 4. Decision Replay

Decision Replay provides counterfactual "what-if" analysis.

The purpose is to investigate questions such as:

> What might have happened if a different tactical decision had been made?

Possible scenarios include:

- Alternative bowler selection
- Alternative tactical choices
- Match-state changes

The system can compare:

- Actual scenario
- Alternative scenario
- Expected runs
- Win probability
- Decision impact
- Explanation

### APIs

```text
GET /api/matches/{id}/decision-points
POST /api/replay/simulate
GET /api/replay/{id}
```

Counterfactual results are estimates and should not be interpreted as certainty about what would have happened.

---

# 5. Scenario Simulator

The Scenario Simulator allows users to modify the current match state and inspect model-based outcomes.

### Inputs

- Current score
- Overs completed
- Wickets lost
- Target runs
- Total overs

### API

```text
POST /api/scenarios/simulate
```

### Outputs

- Projected score
- Win probability
- Required run rate
- Risk assessment
- Match-state interpretation

---

# 6. Matchup Intelligence

CricketIQ analyzes historical batter-vs-bowler interactions.

### API

```text
GET /api/matchups?batter_id={batter_id}&bowler_id={bowler_id}
```

The matchup engine provides:

- Balls faced
- Runs scored
- Strike rate
- Dismissals
- Dot-ball percentage
- Fours
- Sixes
- Matchup advantage

---

# 7. Player Intelligence

Player Intelligence combines historical delivery-level data with statistical analysis.

Available information can include:

- Batting performance
- Bowling performance
- Batting average
- Strike rate
- Bowling economy
- Dot-ball percentage
- Boundary percentage
- Phase-wise performance
- Powerplay performance
- Middle-over performance
- Death-over performance

### API

```text
GET /api/players/{id}
GET /api/players/{id}/stats
```

Historical player data is generated from Cricsheet T20 match data.

Large historical CSV datasets are intentionally excluded from Git version control.

---

# 8. Player Comparison

The Player Comparison module allows users to compare players using available historical performance data.

Comparison is useful for evaluating:

- Batters
- Bowlers
- All-rounders
- Phase performance
- Tactical roles

### API

```text
GET /api/players/compare
```

The frontend provides a dedicated player comparison interface.

---

# 9. Strategy Engine

CricketIQ includes a reusable strategy engine for tactical recommendations.

## Bowling Strategy

### API

```text
POST /api/strategy/bowling
```

The bowling recommendation engine considers:

- Bowling phase
- Phase economy
- Wickets
- Batter-vs-bowler matchup
- Recommendation score

The API supports an optional candidate limit for expensive tactical evaluations.

## Batting Strategy

### API

```text
POST /api/strategy/batting
```

The engine can recommend approaches such as:

```text
AGGRESSIVE_ATTACK
STRIKE_ROTATION
CONTROLLED_ACCELERATION
```

Recommendations consider factors such as:

- Required run rate
- Bowling economy
- Match phase
- Tactical context

---

# 10. Strategy Lab

Strategy Lab combines several CricketIQ intelligence systems into a single tactical analysis.

```text
                   Strategy Lab
                        │
       ┌────────────────┼────────────────┐
       │                │                │
       ▼                ▼                ▼
 Bowling Strategy   Match Situation   Scenario Model
       │                │                │
       └────────────────┼────────────────┘
                        │
                        ▼
                Matchup Intelligence
                        │
                        ▼
                Batting Strategy
                        │
                        ▼
              Combined Recommendation
```

### Strategy Lab Inputs

- Current batter
- Bowling team
- Current score
- Overs completed
- Wickets lost
- Target runs
- Total overs
- Match phase

### API

```text
POST /api/strategy-lab/analyze
```

### Outputs

- Ranked bowling options
- Recommendation scores
- Matchup advantage
- Phase economy
- Tactical batting approach
- Projected batting win probability
- Decision summary
- Uncertainty note

Strategy Lab uses a limited candidate pool for its tactical analysis so that expensive historical analytics are not unnecessarily executed for every player in the complete catalog.

All option-level probabilities are decision-adjusted heuristic estimates and should not be interpreted as an independently trained win-probability model.

---

# 11. AI Analyst

CricketIQ includes an AI analyst layer for natural-language cricket analysis.

### APIs

```text
POST /api/ai/analyze-match
POST /api/ai/analyze-player
POST /api/ai/ask
```

The AI layer can generate:

- Match reports
- Player scouting analysis
- Tactical explanations
- Natural-language answers to cricket questions

AI analysis is designed to be grounded in CricketIQ's available analytics and database information.

AI output should be treated as assisted analysis rather than an authoritative source of match facts.

---

# 12. External Cricket API Integration

CricketIQ includes an external cricket API adapter for live fixtures and match synchronization.

### APIs

```text
GET /api/sync/external-live
POST /api/sync/matches
```

### Environment Variables

```env
CRICKET_API_KEY=
CRICKET_API_BASE_URL=https://api.cricapi.com/v1
```

External provider credentials are supplied through environment variables and should never be hard-coded.

---

# 13. Authentication & Authorization

CricketIQ provides role-based authentication.

Supported roles:

```text
FAN
ANALYST
COACH
ADMIN
```

Authentication uses JWT bearer tokens.

### Authentication APIs

```text
POST /api/auth/register
POST /api/auth/login
GET /api/auth/me
```

The application supports account verification for analyst and coach workflows.

Administrative users can manage verification requests.

---

# Database Architecture

## PostgreSQL

PostgreSQL is the primary relational database.

Core relational tables include:

```text
users
teams
players
venues
matches
innings
deliveries
decision_replays
```

Database migrations are managed through Alembic.

### Run migrations

```bash
cd backend
alembic upgrade head
```

---

# MongoDB

MongoDB is used for flexible document-oriented information such as AI-generated reports.

Example collection:

```text
ai_reports
```

Docker configuration:

```env
MONGODB_URL=mongodb://mongodb:27017
```

---

# Historical Data Pipeline

CricketIQ uses historical T20 data to support:

- Player analytics
- Match analysis
- Matchups
- Win probability
- Strategy recommendations
- Historical model training

The historical pipeline is based on Cricsheet T20 match data.

The development/CI pipeline can generate:

```text
win_probability.csv
player_delivery_history.csv
```

Generated historical datasets are intentionally excluded from Git.

---

# Data Processing

Historical cricket data is processed using:

```text
Python
Pandas
NumPy
scikit-learn
```

The data pipeline supports:

- Match parsing
- Player catalog generation
- Delivery-level analysis
- Historical player statistics
- Model training datasets
- Win-probability datasets

---

# Docker Deployment

CricketIQ is fully containerized for local deployment.

### Docker Services

```text
PostgreSQL
MongoDB
FastAPI Backend
React + Nginx Frontend
```

### Start the complete application

```bash
docker compose up -d --build
```

### Check services

```bash
docker compose ps
```

Expected services:

```text
cricketiq_postgres
cricketiq_mongodb
cricketiq_backend
cricketiq_frontend
```

---

# Environment Configuration

Copy:

```text
.env.example
```

to:

```text
.env
```

Example configuration:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-secure-password
POSTGRES_DB=cricketiq

JWT_SECRET_KEY=your-secure-jwt-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

MONGODB_URL=mongodb://mongodb:27017

LLM_API_KEY=
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_MODEL=openai/gpt-oss-20b

CRICKET_API_KEY=
CRICKET_API_BASE_URL=https://api.cricapi.com/v1

REDIS_URL=redis://localhost:6379/0
```

Never commit the real `.env` file.

---

# Local Backend Development

Create a virtual environment:

```bash
python -m venv venv
```

## Windows

```powershell
venv\Scriptsctivate
```

Install dependencies:

```bash
pip install -r backend/requirements.txt
```

Run migrations:

```bash
cd backend
alembic upgrade head
```

Start the backend:

```bash
uvicorn backend.app.main:app --reload
```

Backend URL:

```text
http://127.0.0.1:8000
```

---

# FastAPI Documentation

Swagger UI:

```text
http://localhost:8000/docs
```

Health endpoint:

```text
http://localhost:8000/health
```

Example health response:

```json
{
  "status": "healthy",
  "service": "cricketiq-backend"
}
```

---

# Local Frontend Development

Navigate to:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

Development frontend:

```text
http://localhost:5173
```

---

# Production Frontend Build

Build the React application:

```bash
npm run build
```

Production assets are generated in:

```text
frontend/dist/
```

The production Docker image serves the React application through Nginx.

Nginx also proxies:

```text
/api/*
```

to the FastAPI backend.

---

# Testing

CricketIQ includes automated backend tests using pytest.

Run:

```bash
python -m pytest backend/tests -v
```

Current verified test coverage includes:

```text
Health Check
Authentication Flow
Matches and Scorecard
Win Probability Prediction
Historical Model Evaluation
Scenario Simulator
Decision Replay
AI Match Analysis
AI Report Persistence in MongoDB
Player Intelligence
Turning Points
Player Matchup
Live Intelligence
```

Current verified result:

```text
13 passed
```

There is currently one non-blocking dependency deprecation warning from the Starlette/AnyIO stack.

---

# CI/CD

GitHub Actions validates the application through automated workflows.

The CI pipeline includes:

```text
┌─────────────────────┐
│ Backend Environment │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Historical Dataset  │
│ Preparation         │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Alembic Migrations  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Database Seed       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Backend Tests       │
└─────────────────────┘

           +

┌─────────────────────┐
│ Frontend Build      │
└─────────────────────┘

           +

┌─────────────────────┐
│ Docker Build        │
└─────────────────────┘
```

CI verifies:

- PostgreSQL integration
- MongoDB integration
- Historical dataset preparation
- Database migrations
- Seed execution
- Backend tests
- Frontend production build
- Docker image builds

---

# Security

Before production deployment:

- Generate a strong random JWT secret.
- Use strong PostgreSQL credentials.
- Keep `.env` outside version control.
- Store API keys in managed secret storage.
- Restrict CORS origins.
- Use HTTPS.
- Restrict public database access.
- Move uploaded identity documents to managed object storage.
- Avoid hard-coded production credentials.
- Apply least-privilege access.
- Enable cloud logging and monitoring.
- Protect administrative accounts.
- Rotate credentials when required.

---

# Production Deployment on Google Cloud

CricketIQ is designed to move from the local Docker environment to Google Cloud.

A planned production architecture is:

```text
                         Internet
                            │
                            ▼
                  ┌──────────────────┐
                  │   React + Nginx  │
                  │    Cloud Run     │
                  └────────┬─────────┘
                           │
                           │ /api
                           ▼
                  ┌──────────────────┐
                  │ FastAPI Backend  │
                  │    Cloud Run     │
                  └──────┬─────┬─────┘
                         │     │
              ┌──────────┘     └──────────┐
              ▼                           ▼
      ┌────────────────┐          ┌────────────────┐
      │   Cloud SQL    │          │ MongoDB Atlas  │
      │  PostgreSQL    │          │   MongoDB      │
      └────────────────┘          └────────────────┘
```

Potential supporting Google Cloud services:

```text
Cloud Run
Cloud SQL
Artifact Registry
Secret Manager
Cloud Logging
Cloud Monitoring
```

The production deployment will use environment-specific configuration and managed secrets instead of development credentials.

---

# GCP Deployment Preparation

Before deployment:

1. Create a Google Cloud project.
2. Enable billing.
3. Enable required Google Cloud APIs.
4. Create an Artifact Registry repository.
5. Deploy PostgreSQL using Cloud SQL.
6. Configure MongoDB using MongoDB Atlas.
7. Store secrets in Secret Manager.
8. Build and push Docker images.
9. Deploy the FastAPI service to Cloud Run.
10. Deploy the frontend service to Cloud Run.
11. Configure service-to-service communication.
12. Configure the production domain and HTTPS.
13. Configure production historical data storage.
14. Add logging and monitoring.

---

# Application URLs

## Local Development

Frontend:

```text
http://localhost:3000
```

Backend:

```text
http://localhost:8000
```

Swagger:

```text
http://localhost:8000/docs
```

Health:

```text
http://localhost:8000/health
```

---

# Authentication

Default development admin account created by the seed process:

```text
Email:
admin@cricketiq.com

Password:
Admin@123
```

> Change the default administrator password before production use.

---

# Example User Flow

```text
User
 │
 ▼
Login
 │
 ▼
Dashboard
 │
 ├── Matches
 │     └── Match Intelligence
 │
 ├── Players
 │     ├── Player Intelligence
 │     └── Player Comparison
 │
 ├── Decision Replay
 │
 ├── Scenario Simulator
 │
 ├── Strategy
 │
 ├── Strategy Lab
 │
 └── AI Analyst
```

---

# Example Strategy Lab Flow

```text
User selects:

Batter
Bowling Team
Current Score
Overs Completed
Wickets Lost
Target
Match Phase

            │
            ▼

     Strategy Lab Engine

            │
     ┌──────┼──────┐
     │      │      │
     ▼      ▼      ▼
 Matchup  Bowling Scenario
 Analysis  Strategy  Model
     │      │      │
     └──────┼──────┘
            │
            ▼
     Tactical Options
            │
            ▼
   Ranked Recommendations
            │
            ▼
      Decision Summary
```

---

# Project Status

CricketIQ currently provides a functional full-stack application containing:

- React frontend
- FastAPI backend
- PostgreSQL
- MongoDB
- JWT authentication
- Role-based authorization
- Historical cricket analytics
- Cricsheet data pipeline
- Win probability model
- Match analytics
- Turning Point Detection
- Decision Replay
- Scenario Simulator
- Player Intelligence
- Player Comparison
- Matchup Intelligence
- Bowling Strategy
- Batting Strategy
- Strategy Lab
- AI Analyst
- External cricket API integration
- Docker deployment
- Nginx API proxy
- Automated backend testing
- GitHub Actions CI/CD

The current development environment has been verified with:

```text
13 backend tests passing
Frontend production build passing
Docker services running
PostgreSQL healthy
MongoDB connectivity verified
Nginx → FastAPI API routing verified
Admin authentication verified
Strategy Lab API verified
```

The next major phase is production deployment on Google Cloud Platform.

---

# Known Limitations

### Historical Data

Large historical CSV files are generated or supplied separately and are intentionally excluded from Git version control.

### Strategy Lab

Strategy Lab uses a limited candidate set to control computational cost. Its option-level probability is a decision-adjusted heuristic and not a separately trained probability model.

### AI Analysis

AI-generated outputs depend on the configured LLM provider and should be treated as assisted analysis.

### External Live Data

Live match availability depends on the configured external cricket API provider and its available data.

### Production Infrastructure

Cloud deployment, managed secret storage, production monitoring, and cloud-based document storage require separate production configuration.

---

# Future Enhancements

Potential future improvements include:

- Google Cloud production deployment
- Real-time event streaming
- Redis-backed caching
- Celery background processing
- Advanced player forecasting
- Additional machine-learning models
- Tactical alerts
- Automated match monitoring
- Expanded tournament coverage
- Team-level strategy intelligence
- Advanced team comparisons
- Cloud object storage
- Production observability
- API rate limiting
- Advanced model calibration

---

# Data & AI Disclaimer

CricketIQ is a cricket analytics and decision-support platform.

The following outputs are estimates:

- Win probabilities
- Projected scores
- Scenario simulations
- Counterfactual results
- Strategy scores
- Tactical recommendations
- AI-generated explanations

These results should not be interpreted as guarantees of actual match outcomes.

Historical data usage must comply with the applicable data provider's licensing terms and conditions.

---

# Development Notes

CricketIQ follows a modular backend architecture where domain services are separated from API routes.

For example:

```text
API Layer
   ↓
Service Layer
   ↓
Data / Model Layer
```

Strategy functionality is separated into reusable strategy services, while Strategy Lab orchestrates those components into a higher-level tactical analysis.

This separation allows individual strategy APIs to remain reusable while Strategy Lab adds contextual match-state analysis.

---

# License

Add the selected project license here before public distribution.

Example:

```text
MIT License
```

or another license appropriate for the project's intended usage and data dependencies.

---

# Author

**Sushant Kulkarni**

CricketIQ  
AI-Powered Cricket Strategy, Performance & Decision Intelligence Platform.
