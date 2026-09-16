from fastapi import APIRouter

from app.models.team import Team

from app.models.match import Match

from app.services.soccer_api import (
    get_team_by_id,
    get_team_matches
)
router = APIRouter(
    prefix="/teams",
    tags=["Teams"]
)

@router.get("/{team_id}", response_model=Team)
async def team_by_id(team_id: int):
    return await get_team_by_id(team_id)

@router.get("/{team_id}/matches", response_model=list[Match])
async def team_matches(team_id: int, season: int):
    return await get_team_matches(team_id, season)