from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.db_models.match import MatchDB


def get_saved_matches(
    db: Session,
    league_id: int | None = None,
    team_id: int | None = None,
    status: str | None = None,
):
    statement = (
        select(MatchDB)
        .options(
            joinedload(MatchDB.league),
            joinedload(MatchDB.home_team),
            joinedload(MatchDB.away_team),
        )
    )

    if league_id is not None:
        statement = statement.where(
            MatchDB.league.has(api_league_id=league_id)
        )

    if team_id is not None:
        statement = statement.where(
            (MatchDB.home_team.has(api_team_id=team_id))
            | (MatchDB.away_team.has(api_team_id=team_id))
        )

    if status is not None:
        statement = statement.where(
            MatchDB.status == status
        )

    statement = statement.order_by(MatchDB.kickoff.desc())

    return db.scalars(statement).all()


def get_saved_match_by_id(db: Session, fixture_id: int):
    statement = (
        select(MatchDB)
        .options(
            joinedload(MatchDB.league),
            joinedload(MatchDB.home_team),
            joinedload(MatchDB.away_team),
        )
        .where(MatchDB.api_fixture_id == fixture_id)
    )

    return db.scalars(statement).first()