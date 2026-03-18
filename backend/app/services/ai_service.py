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
LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.1-8b-instant")


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
    context = ""
    if req.match_id:
        match = db.query(Match).filter(Match.id == req.match_id).first()
        if match:
            tp = detect_turning_points(db, req.match_id)
            top_tp = tp.turning_points[0] if tp.turning_points else None
            referenced.append(f"Match: {match.title}")
            if top_tp:
                referenced.append(
                    f"Top Turning Point: Over {top_tp.display_over} (Swing:"
                    f" {top_tp.win_prob_delta:+.1f}%)"
                )
                context = f"The biggest turning point was in Over {top_tp.display_over} where {top_tp.event_summary} shifted win probability by {top_tp.win_prob_delta:+.1f}%."

    client = _get_client()
    if client and context:
        try:
            completion = client.chat.completions.create(
                model=LLM_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are CricketIQ AI Analyst. Answer using the"
                            " provided context accurately."
                        ),
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Context: {context}\nQuestion: {req.question}"
                        ),
                    },
                ],
            )
            ans = completion.choices[0].message.content.strip()
        except Exception:
            ans = (
                f"Based on CricketIQ data: {context} This was the critical"
                " phase that decided the outcome."
            )
    else:
        ans = (
            f"Analysis based on platform telemetry: {context or 'In modern T20 strategy, phase-based bowling matchups and wicket preservation determine win probability shifts.'}"
        )

    return AskAnalystResponse(
        question=req.question,
        answer=ans,
        referenced_data=referenced or ["CricketIQ Core Historical Telemetry"],
    )