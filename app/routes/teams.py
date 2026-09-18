from fastapi import APIRouter, Query, Path

from app.models.team import Team, SquadPlayer

from app.models.match import Match

from app.services.soccer_api import (
    get_team_by_id,
    get_team_matches,
    get_team_squad
)
router = APIRouter(
    prefix="/teams",
    tags=["Teams"]
)

@router.get("/{team_id}", response_model=Team)
async def team_by_id(team_id: int):
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