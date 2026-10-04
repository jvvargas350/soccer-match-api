from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class MatchDB(Base):
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    api_fixture_id: Mapped[int] = mapped_column(
        Integer,
        unique=True,
        index=True,
        nullable=False
    )

    league_id: Mapped[int | None] = mapped_column(
        ForeignKey("leagues.id"),
        nullable=True
    )

    home_team_id: Mapped[int | None] = mapped_column(
        ForeignKey("teams.id"),
        nullable=True
    )

    away_team_id: Mapped[int | None] = mapped_column(
        ForeignKey("teams.id"),
        nullable=True
    )

    kickoff: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    home_score: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    away_score: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    venue: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True
    )

    city: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    referee: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True
    )