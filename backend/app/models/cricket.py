from datetime import datetime, timezone
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from backend.app.database.session import Base

def utc_now():
    return datetime.now(timezone.utc)


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    short_name = Column(
        String, nullable=False
    )  # e.g., 'IND', 'AUS', 'CSK', 'MI'
    created_at = Column(DateTime, default=utc_now, nullable=False)

    players = relationship(
        "Player", back_populates="team", cascade="all, delete-orphan"
    )


class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    role = Column(
        String, nullable=False
    )  # 'BATTER', 'BOWLER', 'ALL_ROUNDER', 'WICKETKEEPER'
    batting_style = Column(
        String, nullable=True
    )  # 'Right-hand bat', 'Left-hand bat'
    bowling_style = Column(
        String, nullable=True
    )  # 'Right-arm fast', 'Left-arm orthodox', etc.
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    team = relationship("Team", back_populates="players")


class Venue(Base):
    __tablename__ = "venues"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    city = Column(String, nullable=False)
    country = Column(String, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)


class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    match_type = Column(String, default="T20", nullable=False)
    status = Column(String, default="UPCOMING", nullable=False)
    team1_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    team2_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    venue_id = Column(Integer, ForeignKey("venues.id"), nullable=True)
    winner_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    toss_winner_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    toss_decision = Column(String, nullable=True)
    match_date = Column(DateTime, default=utc_now, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    team1 = relationship("Team", foreign_keys=[team1_id])
    team2 = relationship("Team", foreign_keys=[team2_id])
    winner = relationship("Team", foreign_keys=[winner_id])
    toss_winner = relationship("Team", foreign_keys=[toss_winner_id])
    venue = relationship("Venue")
    innings = relationship(
        "Innings", back_populates="match", cascade="all, delete-orphan"
    )


class Innings(Base):
    __tablename__ = "innings"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False)
    innings_number = Column(Integer, nullable=False)  # 1 or 2
    batting_team_id = Column(
        Integer, ForeignKey("teams.id"), nullable=False
    )
    bowling_team_id = Column(
        Integer, ForeignKey("teams.id"), nullable=False
    )
    total_runs = Column(Integer, default=0, nullable=False)
    total_wickets = Column(Integer, default=0, nullable=False)
    total_overs = Column(Float, default=0.0, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    match = relationship("Match", back_populates="innings")
    batting_team = relationship("Team", foreign_keys=[batting_team_id])
    bowling_team = relationship("Team", foreign_keys=[bowling_team_id])
    deliveries = relationship(
        "Delivery", back_populates="innings", cascade="all, delete-orphan"
    )


class Delivery(Base):
    __tablename__ = "deliveries"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(
        Integer, ForeignKey("matches.id"), index=True, nullable=False
    )
    innings_id = Column(
        Integer, ForeignKey("innings.id"), index=True, nullable=False
    )
    over_number = Column(
        Integer, nullable=False
    )  # 0 to 19 for a standard 20-over match
    ball_number = Column(Integer, nullable=False)  # 1 to 6 (or legal ball index)
    batter_id = Column(
        Integer, ForeignKey("players.id"), index=True, nullable=False
    )
    bowler_id = Column(
        Integer, ForeignKey("players.id"), index=True, nullable=False
    )
    non_striker_id = Column(
        Integer, ForeignKey("players.id"), nullable=True
    )

    runs_batter = Column(Integer, default=0, nullable=False)
    runs_extras = Column(Integer, default=0, nullable=False)
    extra_type = Column(
        String, nullable=True
    )  # 'wide', 'noball', 'bye', 'legbye', None

    is_wicket = Column(Boolean, default=False, nullable=False)
    dismissal_type = Column(
        String, nullable=True
    )  # 'bowled', 'caught', 'lbw', 'runout', etc.
    player_dismissed_id = Column(
        Integer, ForeignKey("players.id"), nullable=True
    )

    cumulative_runs = Column(Integer, default=0, nullable=False)
    cumulative_wickets = Column(Integer, default=0, nullable=False)

    innings = relationship("Innings", back_populates="deliveries")
    batter = relationship("Player", foreign_keys=[batter_id])
    bowler = relationship("Player", foreign_keys=[bowler_id])
    non_striker = relationship("Player", foreign_keys=[non_striker_id])
    player_dismissed = relationship(
        "Player", foreign_keys=[player_dismissed_id]
    )

class DecisionReplayRecord(Base):
    __tablename__ = "decision_replays"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False)
    over_number = Column(Integer, nullable=False)
    actual_bowler_id = Column(
        Integer, ForeignKey("players.id"), nullable=False
    )
    alternative_bowler_id = Column(
        Integer, ForeignKey("players.id"), nullable=False
    )
    batter_id = Column(Integer, ForeignKey("players.id"), nullable=False)

    actual_win_prob = Column(Float, nullable=False)
    alternative_win_prob = Column(Float, nullable=False)
    decision_impact = (
        Column(Float, nullable=False)
    )  # Alternative win % - Actual win %
    expected_runs_actual = Column(Float, nullable=False)
    expected_runs_alternative = Column(Float, nullable=False)
    decision_quality_score = Column(Float, nullable=False)  # 0 to 100
    explanation = Column(String, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    match = relationship("Match")
    actual_bowler = relationship("Player", foreign_keys=[actual_bowler_id])
    alternative_bowler = relationship(
        "Player", foreign_keys=[alternative_bowler_id]
    )
    batter = relationship("Player", foreign_keys=[batter_id])