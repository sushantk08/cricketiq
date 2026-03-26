from typing import List
from fastapi import HTTPException, status
import numpy as np
from sqlalchemy.orm import Session
from backend.app.ml.win_probability import win_predictor
from backend.app.models.cricket import (
    DecisionReplayRecord,
    Delivery,
    Innings,
    Match,
    Player,
)
from backend.app.schemas.replay import (
    DecisionPoint,
    DecisionReplayRequest,
    DecisionReplayResponse,
)
from backend.app.services.player_service import (
    compute_player_analytics,
    get_phase_label,
)


def get_match_decision_points(
    db: Session, match_id: int
) -> List[DecisionPoint]:
  inn2 = (
      db.query(Innings)
      .filter(Innings.match_id == match_id, Innings.innings_number == 2)
      .first()
  )
  inn1 = (
      db.query(Innings)
      .filter(Innings.match_id == match_id, Innings.innings_number == 1)
      .first()
  )
  if not inn2 or not inn1:
    return []

  target = inn1.total_runs + 1

  critical_overs = (
      db.query(Delivery)
      .filter(
          Delivery.innings_id == inn2.id,
          Delivery.ball_number == 1,
          Delivery.over_number >= 10,
      )
      .all()
  )

  points = []
  for d in critical_overs:
    balls_bowled = d.over_number * 6
    balls_remaining = max(0, 120 - balls_bowled)
    runs_required = max(0, target - d.cumulative_runs)

    phase = get_phase_label(d.over_number).capitalize()
    reason = (
        f"{phase} phase bowling decision with {runs_required} runs required off"
        f" {balls_remaining} balls."
    )

    points.append(
        DecisionPoint(
            over_number=d.over_number,
            display_over=f"{d.over_number}.1",
            batter_id=d.batter_id,
            batter_name=d.batter.name,
            actual_bowler_id=d.bowler_id,
            actual_bowler_name=d.bowler.name,
            score_at_time=d.cumulative_runs,
            wickets_at_time=d.cumulative_wickets,
            runs_required=runs_required,
            balls_remaining=balls_remaining,
            context_reason=reason,
        )
    )

  return points


def simulate_decision_replay(
    db: Session, req: DecisionReplayRequest
) -> DecisionReplayResponse:
  print(
      f"[Decision Replay] Received request: match_id={req.match_id},"
      f" over_number={req.over_number},"
      f" alternative_bowler_id={req.alternative_bowler_id}"
  )

  inn2 = (
      db.query(Innings)
      .filter(Innings.match_id == req.match_id, Innings.innings_number == 2)
      .first()
  )
  inn1 = (
      db.query(Innings)
      .filter(Innings.match_id == req.match_id, Innings.innings_number == 1)
      .first()
  )
  if not inn2 or not inn1:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=(
            f"Match {req.match_id} does not have both completed innings in the"
            " database."
        ),
    )

  over_delivs = (
      db.query(Delivery)
      .filter(
          Delivery.innings_id == inn2.id,
          Delivery.over_number == req.over_number,
      )
      .order_by(Delivery.ball_number)
      .all()
  )
  if not over_delivs:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=(
            f"No deliveries found for match {req.match_id}, innings {inn2.id},"
            f" over {req.over_number}."
        ),
    )

  first_ball = over_delivs[0]
  target = inn1.total_runs + 1

  runs_before = first_ball.cumulative_runs - first_ball.runs_batter
  wickets_before = first_ball.cumulative_wickets - (
      1 if first_ball.is_wicket else 0
  )
  balls_rem_before = max(0, 120 - (req.over_number * 6))
  runs_req_before = max(0, target - runs_before)
  wkts_hand_before = max(0, 10 - wickets_before)

  actual_runs_scored = sum(d.runs_batter + d.runs_extras for d in over_delivs)
  actual_wickets_taken = sum(1 for d in over_delivs if d.is_wicket)

  balls_rem_after = max(0, balls_rem_before - 6)
  runs_req_actual_after = max(0, runs_req_before - actual_runs_scored)
  wkts_hand_actual_after = max(0, wkts_hand_before - actual_wickets_taken)

  actual_win_prob = win_predictor.predict(
      runs_req_actual_after, balls_rem_after, wkts_hand_actual_after
  )

  alt_bowler = (
      db.query(Player).filter(Player.id == req.alternative_bowler_id).first()
  )
  if not alt_bowler:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Bowler with ID {req.alternative_bowler_id} not found.",
    )

  alt_stats = compute_player_analytics(db, req.alternative_bowler_id)
  phase_label = get_phase_label(req.over_number)

  if (
      alt_stats
      and alt_stats.get("bowling")
      and phase_label in alt_stats["bowling"]["phases"]
  ):
    phase_econ = alt_stats["bowling"]["phases"][phase_label]["economy"]
    exp_runs_alt = round(phase_econ if phase_econ > 0 else 8.5, 1)
    phase_wkts = alt_stats["bowling"]["phases"][phase_label]["wickets"]
    exp_wkts_alt = 1 if phase_wkts > 0 else 0
  else:
    exp_runs_alt = 8.5
    exp_wkts_alt = 0

  runs_req_alt_after = max(0, runs_req_before - int(round(exp_runs_alt)))
  wkts_hand_alt_after = max(0, wkts_hand_before - exp_wkts_alt)

  alt_win_prob = win_predictor.predict(
      runs_req_alt_after, balls_rem_after, wkts_hand_alt_after
  )

  actual_bowling_prob = round((1.0 - actual_win_prob) * 100, 2)
  alt_bowling_prob = round((1.0 - alt_win_prob) * 100, 2)
  impact = round(alt_bowling_prob - actual_bowling_prob, 2)

  quality_score = float(np.clip(50.0 - (impact * 1.5), 5.0, 95.0))

  if impact > 5.0:
    verdict = f"Suboptimal Choice: {alt_bowler.name} was statistically favored"
    explanation = (
        f"Bowling {alt_bowler.name} in over {req.over_number} had an expected"
        f" economy of {exp_runs_alt:.1f} rpo versus {actual_runs_scored} runs"
        f" conceded by {first_ball.bowler.name}. Estimated defensive win"
        f" probability would have improved by {impact:+.1f} percentage points."
    )
  elif impact < -5.0:
    verdict = (
        f"Sound Decision: {first_ball.bowler.name} was the superior option"
    )
    explanation = (
        f"{first_ball.bowler.name} delivered an effective over"
        f" ({actual_runs_scored} runs, {actual_wickets_taken} wickets)."
        f" Substituting {alt_bowler.name} (projected {exp_runs_alt:.1f} runs)"
        f" would have reduced defensive win probability by {abs(impact):.1f}"
        " percentage points."
    )
  else:
    verdict = "Neutral Impact: Comparable tactical options"
    explanation = (
        f"Both {first_ball.bowler.name} and {alt_bowler.name} projected similar"
        f" match equity (impact {impact:+.1f} percentage points)."
    )

  disclaimer = (
      "Statistical estimate derived from historical phase distributions and"
      " model predictions; does not guarantee counterfactual certainty."
  )

  record = DecisionReplayRecord(
      match_id=req.match_id,
      over_number=req.over_number,
      actual_bowler_id=first_ball.bowler_id,
      alternative_bowler_id=alt_bowler.id,
      batter_id=first_ball.batter_id,
      actual_win_prob=actual_bowling_prob,
      alternative_win_prob=alt_bowling_prob,
      decision_impact=impact,
      expected_runs_actual=float(actual_runs_scored),
      expected_runs_alternative=exp_runs_alt,
      decision_quality_score=round(quality_score, 1),
      explanation=explanation,
  )
  db.add(record)
  db.commit()
  db.refresh(record)

  return DecisionReplayResponse(
      replay_id=record.id,
      match_id=record.match_id,
      over_number=record.over_number,
      display_over=f"{record.over_number}.0",
      batter_name=first_ball.batter.name,
      actual_bowler_name=first_ball.bowler.name,
      alternative_bowler_name=alt_bowler.name,
      actual_win_prob=actual_bowling_prob,
      alternative_win_prob=alt_bowling_prob,
      decision_impact=impact,
      expected_runs_actual=float(actual_runs_scored),
      expected_runs_alternative=exp_runs_alt,
      decision_quality_score=round(quality_score, 1),
      tactical_verdict=verdict,
      explanation=explanation,
      uncertainty_disclaimer=disclaimer,
      created_at=record.created_at,
  )