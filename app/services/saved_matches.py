from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.db_models.match import MatchDB


def get_saved_matches(db: Session):
    statement = (
        select(MatchDB)
        .options(
            joinedload(MatchDB.league),
            joinedload(MatchDB.home_team),
            joinedload(MatchDB.away_team)
        )
        .order_by(MatchDB.kickoff.desc())
    )

    matches = db.scalars(statement).all()

    return matches