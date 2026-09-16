from fastapi import APIRouter

from app.models.team import Team

from app.services.soccer_api import get_team_by_id

router = APIRouter(
    prefix="/teams",
    tags=["Teams"]
)

@router.get("/{team_id}", response_model=Team)
async def team_by_id(team_id: int):
    return await get_team_by_id(team_id)