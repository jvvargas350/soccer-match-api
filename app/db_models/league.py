from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class LeagueDB(Base):
    __tablename__ = "leagues"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    api_league_id: Mapped[int] = mapped_column(
        Integer,
        unique=True,
        index=True,
        nullable=False
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    league_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    logo: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    country: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    country_code: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

    flag: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )