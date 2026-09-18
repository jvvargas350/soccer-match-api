from fastapi import APIRouter

from app.models.league import League
from app.models.standing import Standing
from app.services.soccer_api import (get_league_by_id, get_league_standings)

router = APIRouter(
    prefix="/leagues",
    tags=["Leagues"]
)

@router.get("/{league_id}", response_model=League)
async def league_by_id(league_id: int):
    return await get_league_by_id(league_id)

@router.get("/{league_id}/standings", response_model=list[Standing])
async def league_standings(league_id: int, season: int):
    return await get_league_standings(league_id, season)