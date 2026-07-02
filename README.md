# CricketIQ

**AI-Powered Cricket Strategy, Performance & Decision Intelligence Platform.**

CricketIQ is a full-stack cricket intelligence platform designed to help fans, analysts, coaches, and cricket teams understand:

> **What is happening? Why is it happening? What could happen next? What tactical options are available?**

The platform combines historical ball-by-ball cricket data, statistical analytics, machine learning, scenario simulation, matchup intelligence, turning-point detection, counterfactual analysis, and AI-assisted reporting into a single application.

## Live Demo

**Production:** https://cricketiq.duckdns.org

The current AWS deployment uses HTTPS, an AWS Elastic IP, Nginx reverse proxying, FastAPI, AWS RDS PostgreSQL, MongoDB, Redis, and a persistent Celery worker.

> The live environment is a project/demo deployment and should not be treated as a production service with enterprise-grade guarantees.

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
- Redis + Celery background processing
- Historical Cricsheet data processing
- Dockerized local development
- AWS deployment with Nginx and HTTPS
- GitHub Actions CI/CD validation

---

# Architecture

## Application Architecture

```text
                               CricketIQ
                                   │
                ┌──────────────────┴──────────────────┐
                │                                     │
         React + Vite Frontend                  FastAPI Backend
                │                                     │
         React Router / UI                      REST API Layer
                │                                     │
                └──────────────────┬──────────────────┘
                                   │
             ┌─────────────────────┼─────────────────────┐
             │                     │                     │
             ▼                     ▼                     ▼
       PostgreSQL              MongoDB                Redis
       Relational DB           AI Reports          Celery Broker
             │                     │                     │
             └─────────────────────┼─────────────────────┘
                                   │
                          Analytics / ML Layer
                                   │
                   ┌───────────────┼───────────────┐
                   │               │               │
                Pandas           NumPy        scikit-learn
                   │               │               │
                   └───────────────┴───────────────┘
```

## Current AWS Deployment

```text
                           Internet
                               │
                               ▼
                    https://cricketiq.duckdns.org
                               │
                         Docker Nginx
                           :443 / :80
                               │
                               ▼
                     CricketIQ Web Layer
                         Nginx on :8080
                               │
             ┌─────────────────┴─────────────────┐
             │                                   │
             ▼                                   ▼
       React Production Build                /api/* proxy
                                                 │
                                                 ▼
                                      FastAPI / Uvicorn :8001
                                                 │
                               ┌─────────────────┼─────────────────┐
                               │                 │                 │
                               ▼                 ▼                 ▼
                         AWS RDS PostgreSQL   MongoDB           Redis
                                               │                 │
                                               │                 ▼
                                               │             Celery Worker
                                               │
                                               ▼
                                          AI Reports
```

### AWS deployment components currently used

- AWS EC2 for the application host
- AWS RDS PostgreSQL for relational application data
- Docker MongoDB for document storage
- Docker Redis for Celery messaging/result storage
- FastAPI managed by `systemd`
- Celery worker managed by `systemd`
- Nginx for static frontend serving and reverse proxying
- DuckDNS for the public hostname
- Let's Encrypt for HTTPS certificates
- AWS Elastic IP for a stable public address

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
- Redis
- Celery
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
- AWS EC2
- AWS RDS PostgreSQL
- AWS Elastic IP
- DuckDNS
- Let's Encrypt / Certbot
- GitHub Actions

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
│   │   ├── ml/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── main.py
│   │   └── worker.py
│   │
│   ├── data/
│   │   └── historical/
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
│   ├── package-lock.json
│   ├── package.json
│   └── vite.config.js
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
- Required run rate
- Match progression

### API

```text
POST /api/predictions/win-probability
```

The application can also generate ball-by-ball win-probability curves for a match.

### Model Evaluation

The deployed historical model is evaluated chronologically using earlier match data for training and later match data for testing.

A verified evaluation run during the current AWS deployment produced:

```text
Rows:       364,406
Accuracy:   84.38%
Brier Score: 0.10976
```

These metrics describe the evaluated historical dataset and are **not** a guarantee of future prediction performance.

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

The detector focuses on meaningful events instead of treating every delivery as a turning point.

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
          ┌─────────────────┼─────────────────┐
          │                 │                 │
          ▼                 ▼                 ▼
   Bowling Strategy   Match Situation   Scenario Model
          │                 │                 │
          └─────────────────┼─────────────────┘
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

Strategy Lab uses a limited candidate pool for tactical analysis so expensive historical analytics are not unnecessarily executed for every player in the complete catalog.

Option-level probabilities are decision-adjusted heuristic estimates and should not be interpreted as an independently trained win-probability model.

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

### LLM Configuration

An external OpenAI-compatible provider is optional. When no usable `LLM_API_KEY` is configured, the application can fall back to built-in data-driven responses for supported flows.

Default provider settings in the project are:

```env
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_MODEL=openai/gpt-oss-20b
```

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

### Current AWS database

The deployed application uses **AWS RDS PostgreSQL**. The database is private and is accessed from the EC2 application host rather than being exposed directly to the internet.

---

## MongoDB

MongoDB is used for flexible document-oriented information such as AI-generated reports.

Example collection:

```text
ai_reports
```

For local Docker development, the default project compose setup provides MongoDB. In the current AWS deployment, MongoDB runs on the EC2 host in Docker and is consumed by the FastAPI application and Celery worker.

---

## Redis & Celery

Redis is used as the Celery broker and result backend.

```text
FastAPI
   │
   ▼
Redis
   │
   ▼
Celery Worker
   │
   ├── generate_match_report
   └── health_check
```

The current AWS deployment runs Redis in Docker and the Celery worker as a persistent `systemd` service.

---

# Historical Data Pipeline

CricketIQ uses historical T20 data to support:

- Player analytics
- Match analysis
- Matchups
- Win probability
- Strategy recommendations
- Historical model training

The historical pipeline is based on **Cricsheet T20 match data**.

The development/deployment pipeline can generate:

```text
win_probability.csv
player_delivery_history.csv
```

Generated historical datasets are intentionally excluded from Git.

### Current deployed dataset sizes

A verified AWS deployment run generated:

```text
player_delivery_history.csv → 781,953 rows
win_probability.csv         → 364,406 rows
```

### Generate player historical data

The importer expects the Cricsheet T20 ZIP archive at:

```text
~/Downloads/t20s.zip
```

Download it from Cricsheet, then run:

```bash
mkdir -p ~/Downloads
wget -O ~/Downloads/t20s.zip https://cricsheet.org/downloads/t20s.zip
```

Generate the player dataset:

```bash
python -c "from pathlib import Path; from backend.app.data.cricsheet_importer import write_player_historical_dataset; n=write_player_historical_dataset(Path('backend/data/historical/player_delivery_history.csv')); print(f'Generated player_delivery_history.csv with {n} rows')"
```

Generate the win-probability dataset:

```bash
python -c "from pathlib import Path; from backend.app.data.cricsheet_importer import write_training_dataset; n=write_training_dataset(Path('backend/data/historical/win_probability.csv')); print(f'Generated win_probability.csv with {n} rows')"
```

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

CricketIQ is fully containerized for local development and testing.

### Docker services

```text
PostgreSQL
MongoDB
Redis
FastAPI Backend
Celery Worker
React Frontend
```

### Start the complete local stack

```bash
docker compose up -d --build
```

### Check services

```bash
docker compose ps
```

> The AWS deployment is intentionally **hybrid** rather than identical to the local Compose stack: PostgreSQL is moved to AWS RDS, while FastAPI and Celery are managed by `systemd`, and MongoDB/Redis run in Docker on the EC2 host.

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

Example configuration for local development:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-secure-password
POSTGRES_DB=cricketiq

JWT_SECRET_KEY=your-secure-jwt-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

MONGODB_URL=mongodb://localhost:27018
REDIS_URL=redis://localhost:6379/0

LLM_API_KEY=
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_MODEL=openai/gpt-oss-20b

CRICKET_API_KEY=
CRICKET_API_BASE_URL=https://api.cricapi.com/v1
```

For production, use the actual infrastructure connection strings and secrets for that environment.

Never commit the real `.env` file.

---

# Local Backend Development

Create a virtual environment:

```bash
python -m venv venv
```

## Windows

```powershell
venv\Scripts\activate
```

## Linux / macOS

```bash
source venv/bin/activate
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

Start the backend from the repository root:

```bash
uvicorn backend.app.main:app --reload
```

Backend URL:

```text
http://127.0.0.1:8000
```

---

# FastAPI Documentation

During local development, Swagger UI is available at:

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

In the AWS deployment, FastAPI runs internally on `127.0.0.1:8001` and public application requests are routed through Nginx.

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

For a clean lockfile-based install:

```bash
npm ci
```

Start the development server:

```bash
npm run dev
```

Typical Vite development URL:

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

The production frontend is served through Nginx.

The frontend uses relative `/api/...` URLs so the browser communicates with the backend through the same public hostname rather than a hard-coded localhost address.

---

# AWS Deployment

The current live deployment is hosted in **AWS US East (N. Virginia), `us-east-1`**.

## Main components

```text
EC2
 ├── Nginx
 ├── FastAPI
 ├── Celery Worker
 ├── MongoDB (Docker)
 └── Redis (Docker)

RDS
 └── PostgreSQL
```

## Public hostname

```text
https://cricketiq.duckdns.org
```

## Deployment characteristics

- Single EC2 application host
- AWS RDS PostgreSQL
- Private PostgreSQL networking from EC2 to RDS
- Nginx HTTPS reverse proxy
- Let's Encrypt certificate
- DuckDNS hostname
- AWS Elastic IP
- FastAPI persistent `systemd` service
- Celery persistent `systemd` service
- Redis container with automatic restart
- MongoDB container with automatic restart
- Public API exposed through HTTPS Nginx routing

## Current production service commands

Check FastAPI:

```bash
sudo systemctl status cricketiq --no-pager
```

Check Celery:

```bash
sudo systemctl status cricketiq-celery --no-pager
```

Check Nginx:

```bash
sudo systemctl status nginx --no-pager
```

Check Redis:

```bash
docker ps --format 'table {{.Names}}\t{{.Status}}' | grep cricketiq_redis
```

Check MongoDB:

```bash
docker ps --format 'table {{.Names}}\t{{.Status}}' | grep genericrx_mongo
```

## Deployment verification performed

The current AWS deployment was manually verified with the following working paths:

```text
HTTPS frontend
HTTPS /api/teams
FastAPI health endpoint
Historical model evaluation
AI match analysis
Redis connectivity
Celery task execution
MongoDB authenticated connectivity
Celery → MongoDB AI report persistence
```

A background report task completed successfully during deployment and returned a MongoDB report identifier.

---

# Testing

CricketIQ includes automated backend tests using pytest.

Run:

```bash
python -m pytest backend/tests -v
```

The test suite covers application areas such as:

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

Always run the current repository test suite before publishing a new release; test counts can change as the project evolves.

---

# CI/CD

GitHub Actions validates the application through automated workflows.

The CI pipeline is designed to cover:

```text
Backend Environment
        │
        ▼
Historical Dataset Preparation
        │
        ▼
Alembic Migrations
        │
        ▼
Database Seed
        │
        ▼
Backend Tests

        +

Frontend Production Build

        +

Docker Image Builds
```

CI verification includes areas such as:

- PostgreSQL integration
- MongoDB integration
- Historical dataset preparation
- Database migrations
- Seed execution
- Backend tests
- Frontend production build
- Docker image builds

The current AWS deployment does **not** automatically deploy on every Git push; deployment changes are currently performed manually on the EC2 host.

---

# Security

Before treating the project as a hardened production service:

- Generate a strong random JWT secret.
- Use strong PostgreSQL credentials.
- Keep `.env` outside version control.
- Store API keys in managed secret storage where appropriate.
- Restrict CORS origins for the final public environment.
- Use HTTPS.
- Restrict public database access.
- Avoid hard-coded production credentials.
- Apply least-privilege access.
- Enable cloud logging and monitoring.
- Protect administrative accounts.
- Rotate credentials when required.
- Add API rate limiting for public endpoints.

The deployed environment has a strong random JWT secret and keeps `.env` ignored by Git. The seed process still contains a development admin account, so the administrative credential should be changed before any serious production use.

---

# Authentication

The seed process creates a development administrator account for local/demo workflows.

The repository intentionally does **not** publish the development password in this README.

Before public production use:

1. Change the development administrator password.
2. Confirm administrative account protection.
3. Use a unique production JWT secret.
4. Review account verification rules.

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
        ├──────────┬──────────┐
        ▼          ▼          ▼
     Matchup    Bowling    Scenario
     Analysis   Strategy     Model
        │          │          │
        └──────────┼──────────┘
                   │
                   ▼
            Tactical Options
                   │
                   ▼
          Recommendation List
                   │
                   ▼
            Decision Summary
```

---

# Current Project Status

CricketIQ currently provides a functional full-stack application containing:

- React frontend
- FastAPI backend
- PostgreSQL
- MongoDB
- Redis
- Celery background processing
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
- Docker deployment for local development
- Nginx API proxy
- AWS deployment
- HTTPS domain
- Automated backend testing
- GitHub Actions CI/CD validation

### Current AWS verification snapshot

```text
Public HTTPS site:        Working
FastAPI backend:          Working
RDS PostgreSQL:           Connected
MongoDB:                  Connected
Redis:                    Working
Celery worker:            Working
AI report persistence:    Working
Historical datasets:      Generated
Historical model API:     Working
React production build:   Passing
```

### Current public application

```text
https://cricketiq.duckdns.org
```

---

# Known Limitations

### Historical Data

Large historical CSV files are generated separately and intentionally excluded from Git version control.

### Strategy Lab

Strategy Lab uses a limited candidate set to control computational cost. Its option-level probability is a decision-adjusted heuristic and not a separately trained probability model.

### AI Analysis

AI-generated outputs depend on the configured LLM provider. Without a usable external LLM API key, supported AI flows can use built-in fallback responses.

### External Live Data

Live match availability depends on the configured external cricket API provider and its available data.

### Production Infrastructure

The current AWS deployment is a practical project/demo deployment. It still needs additional hardening for a larger production workload, including managed secret storage, centralized logging/monitoring, rate limiting, stronger isolation of supporting services, and automated deployment workflows.

### Certificate Renewal

Let's Encrypt certificates are installed and Certbot renewal is scheduled. The current deployment uses Certbot's standalone authenticator, which requires temporary access to port 80 during renewal. Renewal hooks are configured to stop and restart the shared Nginx container. A renewal dry-run during setup received a temporary Let's Encrypt `rateLimited / Service busy` response; the live certificates remained valid.

---

# Future Enhancements

Potential future improvements include:

- Automated AWS deployment through GitHub Actions
- Real-time event streaming
- Redis-backed application caching
- More Celery background workloads
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
- Centralized secret management
- Custom production domain instead of a free DuckDNS hostname

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


```text
MIT License
```


# Author

**Sushant Kulkarni**

CricketIQ  
AI-Powered Cricket Strategy, Performance & Decision Intelligence Platform.
