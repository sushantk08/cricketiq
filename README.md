# CricketIQ

AI-Powered Cricket Strategy, Performance & Decision Intelligence Platform.

## Overview
CricketIQ is a full-stack cricket intelligence platform designed for fans, analysts, coaches, and teams. It delivers tactical insights, win probability modeling, automated turning point detection, and counterfactual "what-if" analysis through Decision Replay.

## Status
Project initialization in progress.

## Backend Setup

### Prerequisites

* Python 3.10+

### Installation

1. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   ```

   **On Windows:**

   ```bash
   venv\Scripts\activate
   ```

   **On macOS/Linux:**

   ```bash
   source venv/bin/activate
   ```

2. Install the backend dependencies:

   ```bash
   pip install -r backend/requirements.txt
   ```

3. Run the development server:

   ```bash
   uvicorn backend.app.main:app --reload
   ```

4. Open the application in your browser:

   ```text
   http://127.0.0.1:8000
   ```

5. Open the interactive API documentation:

   ```text
   http://127.0.0.1:8000/docs
   ```

## Database Setup
1. Ensure PostgreSQL is installed and running locally.
2. Create the application database:
   ```bash
   createdb cricketiq
3. Seed sample cricket data (teams, players, venue, match, and deliveries):
   ```bash
   python -m backend.app.database.seed

## API Endpoints

### Authentication
- `POST /api/auth/register` — Register a new user account with role selection (`FAN`, `ANALYST`, `COACH`, `ADMIN`).
- `POST /api/auth/login` — Authenticate credentials and receive a JWT Bearer access token.
- `GET /api/auth/me` — Retrieve the current authenticated user profile (requires Bearer token).

## Database Schema (Relational)
- `users`: Authentication, credentials, and user roles (`FAN`, `ANALYST`, `COACH`, `ADMIN`).
- `teams`: Cricket teams with names and codes.
- `players`: Cricket players with roles, batting styles, bowling styles, and team affiliations.
- `venues`: Match grounds with city and country details.
- `matches`: Match fixtures with team relationships, status, toss details, and venue.
- `innings`: Match innings records (runs, wickets, total overs, batting/bowling teams).
- `deliveries`: Ball-by-ball delivery event data with batter, bowler, runs, extras, wickets, and cumulative progression state.

### Matches
- `GET /api/matches` — List all matches with team fixtures and venues.
- `GET /api/matches/{id}` — Retrieve detailed match overview.
- `GET /api/matches/{id}/scorecard` — Compute and retrieve the complete innings scorecard (batting figures, bowling figures, and totals).
- `GET /api/matches/{id}/deliveries` — Retrieve the ordered ball-by-ball delivery event stream.

### Players & Analytics
- `GET /api/players` — List players with optional `team_id` and `role` filters.
- `GET /api/players/{id}` — Get player profile details.
- `GET /api/players/{id}/stats` — Compute granular batting/bowling statistics (averages, strike rates, dot %, boundary %, and phase performance across Powerplay, Middle, and Death overs).

### Machine Learning Predictions
- `POST /api/predictions/win-probability` — Calculate win percentage for any custom match state (runs required, balls remaining, wickets in hand).
- `GET /api/predictions/matches/{id}/curve` — Retrieve the ball-by-ball win probability progression curve for a match chase.

### Match Analytics & Turning Points
- `GET /api/matches/{id}/turning-points` — Detect and rank significant match inflection points by win-probability shift ($\Delta P$), wickets, and boundary momentum.


### Decision Replay (Signature "What-If" Analysis)
- `GET /api/matches/{id}/decision-points` — List high-leverage tactical moments available for replay.
- `POST /api/replay/simulate` — Simulate a counterfactual decision (e.g. alternate bowler in the 17th over) and compare expected runs, win probability, and decision impact ($\Delta \text{Win\%}$).
- `GET /api/replay/{id}` — Retrieve a previously saved Decision Replay analysis.

### Scenario Simulator
- `POST /api/scenarios/simulate` — Alter match state variables (score, overs, wickets, target) and compute projected scores, win probability, required run rates, and risk assessments.

### Strategy & Matchups
- `GET /api/matchups?batter_id={id}&bowler_id={id}` — Head-to-head matchup statistics (runs, balls faced, strike rate, dismissals, advantage classification).
- `POST /api/strategy/bowling` — Rank and recommend the best bowling options against a specific batter in a chosen phase.
- `POST /api/strategy/batting` — Recommend tactical batting approach (attack, strike rotation, consolidation) against an active bowler.

### AI Analyst & Match Reports
- `POST /api/ai/analyze-match` — Generate an AI match report synthesizing ground-truth database facts, top performers, and critical turning points.
- `POST /api/ai/analyze-player` — Generate scouting evaluations and tactical recommendations for a player.
- `POST /api/ai/ask` — Natural-language Q&A grounded in verified match analytics.

### External Cricket API Integration
- `GET /api/sync/external-live` — Preview normalized external match feeds via the Cricket API adapter.
- `POST /api/sync/matches` — Synchronize and ingest external fixtures into internal PostgreSQL models.