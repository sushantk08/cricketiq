from fastapi import APIRouter
from backend.app.schemas.scenario import (
    ScenarioSimulateRequest,
    ScenarioSimulateResponse,
)
from backend.app.services.scenario_service import run_scenario_simulation

router = APIRouter(prefix="/api/scenarios", tags=["Scenario Simulator"])


@router.post("/simulate", response_model=ScenarioSimulateResponse)
def simulate_scenario(req: ScenarioSimulateRequest):
    return run_scenario_simulation(req)