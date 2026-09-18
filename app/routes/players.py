from fastapi import APIRouter

from app.models.player import Player, PlayerStatistics
from app.services.soccer_api import (get_player_by_id, get_player_statistics)


router = APIRouter(
    prefix="/players",
    tags=["Players"]
)

@router.get("/{player_id}/statistics",response_model=PlayerStatistics)
async def player_statistics(player_id: int,season: int, league_id: int):
    return await get_player_statistics(player_id,season,league_id)

@router.get("/{player_id}", response_model=Player)
async def player_by_id(player_id: int,season: int):
    return await get_player_by_id(player_id,season)