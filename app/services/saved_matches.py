from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.db_models.match import MatchDB


def get_saved_matches(
    db: Session,
    league_id: int | None = None,
    team_id: int | None = None,
    status: str | None = None,
    limit: int = 20,
    offset: int = 0,
):
    statement = select(MatchDB)

    if league_id is not None:
        statement = statement.where(
            MatchDB.league.has(api_league_id=league_id)
        )

    if team_id is not None:
        statement = statement.where(
            MatchDB.home_team.has(api_team_id=team_id)
            | MatchDB.away_team.has(api_team_id=team_id)
        )

    if status is not None:
        statement = statement.where(
            MatchDB.status == status
        )

    count_statement = select(func.count()).select_from(
        statement.order_by(None).subquery()
    )

    total = db.scalar(count_statement) or 0

    statement = (
        statement
        .options(
            joinedload(MatchDB.league),
            joinedload(MatchDB.home_team),
            joinedload(MatchDB.away_team),
        )
        .order_by(MatchDB.kickoff.desc(), MatchDB.id.desc())
        .limit(limit)
        .offset(offset)
    )

    matches = db.scalars(statement).all()

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_next": offset + len(matches) < total,
        "matches": matches,
    }

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