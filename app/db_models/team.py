from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TeamDB(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    api_team_id: Mapped[int] = mapped_column(
        Integer,
        unique=True,
        index=True,
        nullable=False
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    code: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True
    )

    country: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    founded: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    national: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False
    )

    logo: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )
    
    home_matches = relationship(
    "MatchDB",
    foreign_keys="MatchDB.home_team_id",
    back_populates="home_team"
    )

    away_matches = relationship(
        "MatchDB",
        foreign_keys="MatchDB.away_team_id",
        back_populates="away_team"
    )