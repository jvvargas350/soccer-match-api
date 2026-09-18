from fastapi import APIRouter, Query, Path

from app.models.player import Player, PlayerStatistics
from app.services.soccer_api import (get_player_by_id, get_player_statistics)


router = APIRouter(
    prefix="/players",
    tags=["Players"]
)

@router.get("/{player_id}/statistics",response_model=PlayerStatistics)
async def player_statistics(
    player_id: int = Path(gt=0), 
    season: int = Query(ge=2000, le=2100), 
    league_id: int = Query(gt=0)
    ):
    return await get_player_statistics(player_id, season, league_id)

@router.get("/{player_id}", response_model=Player)
async def player_by_id(player_id: int = Path(gt=0), season: int = Query(ge=2000, le=2100)):
    return await get_player_by_id(player_id, season)