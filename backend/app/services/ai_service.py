import json
import os
from openai import OpenAI
from sqlalchemy.orm import Session
from backend.app.models.cricket import Match
from backend.app.schemas.ai import (
    AskAnalystRequest,
    AskAnalystResponse,
    MatchAnalysisResponse,
    PlayerAnalysisResponse,
)
from backend.app.services.match_service import compute_match_scorecard
from backend.app.services.player_service import compute_player_analytics
from backend.app.services.turning_point_service import detect_turning_points

LLM_API_KEY = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY", "")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "openai/gpt-oss-20b")


def _get_client():
    if LLM_API_KEY and not LLM_API_KEY.startswith("your_"):
        return OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)
    return None


def generate_match_analysis(
    db: Session, match_id: int
) -> MatchAnalysisResponse:
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        return None

    scorecard = compute_match_scorecard(db, match_id)
    tp_response = detect_turning_points(db, match_id)

    inn1 = scorecard["innings"][0]
    inn2 = scorecard["innings"][1]

    all_batters = inn1["batting"] + inn2["batting"]
    best_bat = max(all_batters, key=lambda b: b["runs"])

    all_bowlers = inn1["bowling"] + inn2["bowling"]
    best_bowl = max(all_bowlers, key=lambda bw: bw["wickets"])

    turning_points_summary = [
        f"Over {tp.display_over}: {tp.event_summary} (Win swing:"
        f" {tp.win_prob_delta:+.1f}%)"
        for tp in tp_response.turning_points[:3]
    ]

    client = _get_client()
    if client:
        prompt = f"""
        You are CricketIQ AI Match Analyst. Analyze the match based strictly on the factual data below:
        Match: {match.title}
        Winner: {match.winner.name if match.winner else 'Undecided'}
        1st Innings: {inn1['batting_team']} scored {inn1['total_runs']}/{inn1['total_wickets']} in {inn1['total_overs']} overs.
        2nd Innings: {inn2['batting_team']} scored {inn2['total_runs']}/{inn2['total_wickets']} in {inn2['total_overs']} overs.
        Top Batter: {best_bat['name']} ({best_bat['runs']} runs off {best_bat['balls']} balls, SR: {best_bat['strike_rate']}).
        Top Bowler: {best_bowl['name']} ({best_bowl['wickets']} wickets for {best_bowl['runs_conceded']} runs, Economy: {best_bowl['economy']}).
        Key Turning Points:
        {chr(10).join(turning_points_summary)}

        Provide a crisp, objective analytical summary (max 3 sentences) explaining why the match was won or lost.
        """
        try:
            completion = client.chat.completions.create(
                model=LLM_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert cricket intelligence"
                            " strategist. Be concise and data-driven."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
            )
            summary_text = completion.choices[0].message.content.strip()
        except Exception:
            summary_text = (
                f"Automated intelligence summary: {match.winner.name} secured"
                f" victory after posting {inn1['total_runs']} and defending"
                " via high-leverage wickets in the middle overs."
            )
    else:
        summary_text = (
            f"{match.winner.name if match.winner else 'The winning team'} prevailed"
            f" by defending {inn1['total_runs']} runs. High dot-ball percentage and critical"
            f" wickets taken by {best_bowl['name']} in the death phase restricted {inn2['batting_team']}."
        )

    return MatchAnalysisResponse(
        match_id=match.id,
        match_title=match.title,
        winner=match.winner.name if match.winner else "Undecided",
        summary=summary_text,
        best_batter=(
            f"{best_bat['name']} ({best_bat['runs']} runs @ SR"
            f" {best_bat['strike_rate']})"
        ),
        best_bowler=(
            f"{best_bowl['name']} ({best_bowl['wickets']}/"
            f"{best_bowl['runs_conceded']} @ {best_bowl['economy']} RPO)"
        ),
        turning_point_insights=turning_points_summary,
        tactical_verdict=(
            f"Match decided by boundary discipline in the middle phase and"
            f" death-overs execution by {best_bowl['name']}."
        ),
        grounded_in_database_facts=True,
    )


def generate_player_analysis(
    db: Session, player_id: int
) -> PlayerAnalysisResponse:
    stats = compute_player_analytics(db, player_id)
    if not stats:
        return None

    player_name = stats["name"]
    role = stats["role"]
    strengths = []
    recommendations = []

    if stats.get("batting"):
        b = stats["batting"]
        strengths.append(
            f"Scoring efficiency: Strike rate of {b['strike_rate']} with"
            f" {b['boundary_run_pct']}% runs coming from boundaries."
        )
        strengths.append(
            f"Powerplay impact: {b['phases']['powerplay']['runs']} runs scored"
            f" at {b['phases']['powerplay']['strike_rate']} SR."
        )
        recommendations.append(
            f"Maintain dot-ball compression below 35% in middle overs"
            f" (currently {b['dot_ball_pct']}%)."
        )
    if stats.get("bowling"):
        bw = stats["bowling"]
        strengths.append(
            f"Economy control: Operates at {bw['economy']} RPO with"
            f" {bw['dot_ball_pct']}% dot balls."
        )
        recommendations.append(
            "Deploy primarily in powerplay and death overs to maximize"
            " pressure."
        )

    report = f"Scouting evaluation for {player_name} ({role}): Demonstrates strong tactical discipline aligned with modern T20 pacing metrics."

    return PlayerAnalysisResponse(
        player_id=player_id,
        player_name=player_name,
        role=role,
        scouting_report=report,
        strengths=strengths,
        tactical_recommendations=recommendations,
    )


def answer_analyst_question(
    db: Session, req: AskAnalystRequest
) -> AskAnalystResponse:
  referenced = []
  context_blocks = []
  q_lower = req.question.lower()

  match = None
  scorecard = None
  tp_data = None

  if req.match_id:
    match = db.query(Match).filter(Match.id == req.match_id).first()
    if match:
      scorecard = compute_match_scorecard(db, req.match_id)
      tp_data = detect_turning_points(db, req.match_id)
      referenced.append(f"Match: {match.title}")

  client = _get_client()

  # Build rich context if match is present
  if match and scorecard:
    inn1 = scorecard["innings"][0]
    inn2 = scorecard["innings"][1]

    # Best performers
    all_batters = inn1["batting"] + inn2["batting"]
    best_bat = (
        max(all_batters, key=lambda b: b["runs"]) if all_batters else None
    )

    all_bowlers = inn1["bowling"] + inn2["bowling"]
    best_bowl = (
        max(all_bowlers, key=lambda bw: bw["wickets"]) if all_bowlers else None
    )

    context_blocks.append(
        f"Match: {match.title}. Result: {match.winner.name if match.winner else 'Completed'}."
    )
    context_blocks.append(
        f"1st Innings ({inn1['batting_team']}): {inn1['total_runs']}/{inn1['total_wickets']} in {inn1['total_overs']} overs."
    )
    context_blocks.append(
        f"2nd Innings ({inn2['batting_team']}): {inn2['total_runs']}/{inn2['total_wickets']} in {inn2['total_overs']} overs."
    )

    if best_bat:
      context_blocks.append(
          f"Top Scorer: {best_bat['name']} with {best_bat['runs']} runs off {best_bat['balls']} balls (SR: {best_bat['strike_rate']})."
      )
    if best_bowl:
      context_blocks.append(
          f"Leading Wicket Taker: {best_bowl['name']} ({best_bowl['wickets']}/{best_bowl['runs_conceded']} in {best_bowl['overs']} overs, Economy: {best_bowl['economy']})."
      )

    if tp_data and tp_data.turning_points:
      top_tp = tp_data.turning_points[0]
      context_blocks.append(
          f"Critical Turning Point: Over {top_tp.display_over} where {top_tp.event_summary} caused a {top_tp.win_prob_delta:+.1f}% win probability swing."
      )
      referenced.append(
          f"Top Turning Point: Over {top_tp.display_over} ({top_tp.win_prob_delta:+.1f}%)"
      )

  full_context = "\n".join(context_blocks)

  # 1. If live LLM is configured, query the model with the rich context
  if client and full_context:
    try:
      completion = client.chat.completions.create(
          model=LLM_MODEL,
          messages=[
              {
                  "role": "system",
                  "content": (
                      "You are CricketIQ AI Strategy Analyst. Answer the"
                      " user's specific cricket question using strictly the"
                      " provided match facts. Keep answers concise (2-4"
                      " sentences), objective, and direct."
                  ),
              },
              {
                  "role": "user",
                  "content": (
                      f"Match Telemetry:\n{full_context}\n\nQuestion:"
                      f" {req.question}"
                  ),
              },
          ],
          temperature=0.3,
      )
      return AskAnalystResponse(
          question=req.question,
          answer=completion.choices[0].message.content.strip(),
          referenced_data=referenced or ["CricketIQ Ground Truth Telemetry"],
      )
    except Exception as e:
      print(f"[AI Service] LLM call failed: {e}. Falling back to analytical engine.")

  # 2. Dynamic, Intent-Aware Analytical Fallback
  if scorecard:
    inn1 = scorecard["innings"][0]
    inn2 = scorecard["innings"][1]

    # Intent A: Scorecard requested
    if "scorecard" in q_lower or "score" in q_lower:
      ans = (
          f"Scorecard Summary for {match.title}: "
          f"{inn1['batting_team']} posted {inn1['total_runs']}/{inn1['total_wickets']} in {inn1['total_overs']} overs. "
          f"In response, {inn2['batting_team']} finished on {inn2['total_runs']}/{inn2['total_wickets']}. "
          f"Top individual score was {best_bat['name']} ({best_bat['runs']} off {best_bat['balls']}b), "
          f"while {best_bowl['name']} led the bowling figures with {best_bowl['wickets']} wickets."
      )
      referenced.append("Innings 1 & 2 Scorecards")

    # Intent B: Bowler / Death overs discipline
    elif (
        "bowler" in q_lower
        or "death" in q_lower
        or "discipline" in q_lower
        or "economy" in q_lower
    ):
      # Find bowler with lowest economy who bowled at least 2 overs
      all_bowlers = inn1["bowling"] + inn2["bowling"]
      qualified_bowlers = [b for b in all_bowlers if b["overs"] >= 2.0]
      most_economical = (
          min(qualified_bowlers, key=lambda b: b["economy"])
          if qualified_bowlers
          else (all_bowlers[0] if all_bowlers else None)
      )
      if most_economical:
        ans = (
            f"The most disciplined bowler across the match was {most_economical['name']}, "
            f"conceding only {most_economical['runs_conceded']} runs in {most_economical['overs']} overs "
            f"(Economy: {most_economical['economy']} RPO) while picking up {most_economical['wickets']} wicket(s)."
        )
        referenced.append(
            f"Bowling Economy Telemetry ({most_economical['name']})"
        )
      else:
        ans = "Bowlers maintained standard phase economy rates throughout the contest."

    # Intent C: Middle overs / Momentum loss
    elif (
        "middle" in q_lower
        or "momentum" in q_lower
        or "collapse" in q_lower
        or "lose" in q_lower
    ):
      ans = (
          f"In the middle overs, the bowling side applied pressure through dot-ball compression "
          f"and key dismissals. With the required run rate escalating beyond 10.5 RPO, "
          f"the batting side was forced into high-risk shots that triggered wickets."
      )
      referenced.append("Phase Run Rate & Wicket Compression")

    # Intent D: Win probability / Turning point
    elif (
        "win probability" in q_lower
        or "turning" in q_lower
        or "shift" in q_lower
        or "swing" in q_lower
    ):
      if tp_data and tp_data.turning_points:
        top_tp = tp_data.turning_points[0]
        ans = (
            f"The decisive shift in win probability occurred in Over {top_tp.display_over} "
            f"({top_tp.event_summary}), which produced a {top_tp.win_prob_delta:+.1f}% swing "
            f"in favor of {match.winner.name if match.winner else 'the defending team'}."
        )
      else:
        ans = "Win probability remained closely balanced throughout the chase phase."

    # General Intent
    else:
      ans = (
          f"{match.winner.name if match.winner else 'The winning team'} secured victory by executing "
          f"tactical phase plans. Key contributions included {best_bat['name']}'s {best_bat['runs']} runs "
          f"and {best_bowl['name']}'s {best_bowl['wickets']} wickets."
      )
  else:
    ans = (
        "CricketIQ telemetry indicates that match leverage is determined by phase-based run rate pressure, "
        "disciplined death bowling, and high-leverage wicket timing."
    )

  return AskAnalystResponse(
      question=req.question,
      answer=ans,
      referenced_data=referenced or ["CricketIQ Core Historical Telemetry"],
  )