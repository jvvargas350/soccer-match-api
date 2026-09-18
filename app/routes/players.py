from fastapi import APIRouter

from app.models.player import Player
from app.services.soccer_api import get_player_by_id


router = APIRouter(
    prefix="/players",
    tags=["Players"]
)


@router.get("/{player_id}", response_model=Player)
async def player_by_id(player_id: int,season: int):
    return await get_player_by_id(player_id,season)