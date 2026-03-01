from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from backend.app.database.session import Base


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    short_name = Column(
        String, nullable=False
    )  # e.g., 'IND', 'AUS', 'CSK', 'MI'
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

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
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    team = relationship("Team", back_populates="players")


class Venue(Base):
    __tablename__ = "venues"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    city = Column(String, nullable=False)
    country = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(
        String, nullable=False
    )  # e.g., 'India vs Australia - 1st T20I'
    match_type = Column(
        String, default="T20", nullable=False
    )  # 'T20', 'ODI', 'TEST'
    status = Column(
        String, default="UPCOMING", nullable=False
    )  # 'UPCOMING', 'LIVE', 'COMPLETED'
    team1_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    team2_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    venue_id = Column(Integer, ForeignKey("venues.id"), nullable=True)
    winner_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    toss_winner_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    toss_decision = Column(String, nullable=True)  # 'bat', 'bowl'
    match_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    team1 = relationship("Team", foreign_keys=[team1_id])
    team2 = relationship("Team", foreign_keys=[team2_id])
    winner = relationship("Team", foreign_keys=[winner_id])
    toss_winner = relationship("Team", foreign_keys=[toss_winner_id])
    venue = relationship("Venue")