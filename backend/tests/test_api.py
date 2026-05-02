import uuid


def test_health_check(client):
    """Verify the health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_auth_flow(client):
    """Verify registration, login, and protected me endpoint."""
    unique_email = f"tester_{uuid.uuid4().hex[:6]}@cricketiq.com"
    password = "TestPassword123"

    # 1. Register
    reg_resp = client.post(
    "/api/auth/register",
    data={
        "email": unique_email,
        "password": password,
        "full_name": "Test Fan",
        "role": "FAN",
    },
)
    assert reg_resp.status_code == 201
    user_data = reg_resp.json()
    assert user_data["email"] == unique_email
    assert user_data["role"] == "FAN"

    # 2. Login
    login_resp = client.post(
        "/api/auth/login", json={"email": unique_email, "password": password}
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    assert token is not None

    # 3. Protected Profile
    me_resp = client.get(
        "/api/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == unique_email


def test_matches_and_scorecard(client):
    """Verify match list and computed scorecard for Match 1."""
    # List matches
    matches_resp = client.get("/api/matches")
    assert matches_resp.status_code == 200
    matches = matches_resp.json()
    assert len(matches) >= 1

    # Scorecard
    sc_resp = client.get("/api/matches/1/scorecard")
    assert sc_resp.status_code == 200
    sc_data = sc_resp.json()
    assert len(sc_data["innings"]) == 2
    inn1 = sc_data["innings"][0]
    assert len(inn1["batting"]) > 0
    assert len(inn1["bowling"]) > 0


def test_win_probability_prediction(client):
    """Verify ML win probability engine."""
    resp = client.post(
        "/api/predictions/win-probability",
        json={"runs_required": 30, "balls_remaining": 18, "wickets_in_hand": 6},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert 0.0 <= data["win_probability_batting"] <= 100.0
    assert 0.0 <= data["win_probability_bowling"] <= 100.0
    assert (
        round(
            data["win_probability_batting"]
            + data["win_probability_bowling"]
        )
        == 100
    )


def test_scenario_simulator(client):
    """Verify scenario simulation calculation."""
    resp = client.post(
        "/api/scenarios/simulate",
        json={
            "current_score": 140,
            "overs_completed": 16.0,
            "wickets_lost": 4,
            "target_runs": 180,
            "total_overs": 20,
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["runs_required"] == 40
    assert data["balls_remaining"] == 24
    assert data["risk_level"] in ["LOW", "MODERATE", "HIGH", "EXTREME"]


def test_decision_replay(client):
    """Verify counterfactual decision replay simulation."""
    # Simulate Over 16 with alternative bowler Jasprit Bumrah (ID 9)
    resp = client.post(
        "/api/replay/simulate",
        json={
            "match_id": 1,
            "over_number": 16,
            "alternative_bowler_id": 9,
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "decision_impact" in data
    assert 0.0 <= data["decision_quality_score"] <= 100.0
    assert "uncertainty_disclaimer" in data

def test_ai_match_analysis(client):
    """Verify AI match analysis returns database-grounded match facts."""
    response = client.post(
        "/api/ai/analyze-match",
        json={"match_id": 1},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["match_id"] == 1
    assert data["match_title"] == "India vs Australia - T20 Super Series"
    assert data["winner"] == "India"
    assert data["best_batter"]
    assert data["best_bowler"]
    assert isinstance(data["turning_point_insights"], list)
    assert data["grounded_in_database_facts"] is True

def test_ai_report_saved_to_mongodb(client):
    """Verify an AI match report is persisted to MongoDB."""
    from backend.app.database.mongodb import ai_reports_collection

    response = client.post(
        "/api/ai/analyze-match",
        json={"match_id": 1},
    )

    assert response.status_code == 200

    report = response.json()

    stored = ai_reports_collection.find_one(
        {"match_id": report["match_id"]},
        sort=[("created_at", -1)],
    )

    assert stored is not None
    assert stored["match_id"] == report["match_id"]
    assert stored["match_title"] == report["match_title"]
    assert stored["winner"] == report["winner"]
    assert stored["grounded_in_database_facts"] is True