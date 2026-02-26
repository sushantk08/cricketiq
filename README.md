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
