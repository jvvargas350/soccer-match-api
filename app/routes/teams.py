from fastapi import APIRouter, Depends, Query, Path

from app.models.team import Team, SquadPlayer

from app.models.match import Match

from sqlalchemy.orm import Session

from app.database import get_db

from app.services.soccer_api import (
    get_team_by_id,
    get_team_matches,
    get_team_squad,
    save_team_to_database
)
router = APIRouter(
    prefix="/teams",
    tags=["Teams"]
)

@router.get("/{team_id}", response_model=Team)
async def team_by_id(team_id: int= Path(gt=0)):
    return await get_team_by_id(team_id)

@router.get("/{team_id}/matches", response_model=list[Match])
async def team_matches(
    team_id: int = Path(gt=0),
    season: int = Query(ge=2000, le=2100)
    ):
    return await get_team_matches(team_id, season)

@router.get("/{team_id}/squad", response_model=list[SquadPlayer])
async def team_squad(
    team_id: int = Path(gt=0)
    ):
    return await get_team_squad(team_id)

@router.post("/{team_id}/save")
async def save_team(
    team_id: int = Path(gt=0),
    db: Session = Depends(get_db)
):
    team = await save_team_to_database(
        team_id,
        db
    )

    return {
        "message": "Team saved successfully",
        "team": {
            "id": team.id,
            "api_team_id": team.api_team_id,
            "name": team.name,
            "code": team.code,
            "country": team.country,
            "founded": team.founded,
            "national": team.national,
            "logo": team.logo
        }
    }