from fastapi import APIRouter, Query, Path

from app.models.league import League
from app.models.standing import Standing
from app.models.player import TopScorer
from app.models.team import Team
from app.services.soccer_api import (get_league_by_id, get_league_standings, get_top_scorers, get_league_teams)

router = APIRouter(
    prefix="/leagues",
    tags=["Leagues"]
)

@router.get("/{league_id}", response_model=League)
async def league_by_id(league_id: int):
    return await get_league_by_id(league_id)

@router.get("/{league_id}/standings", response_model=list[Standing])
async def league_standings(
    league_id: int = Path(gt=0), 
    season: int = Query(ge=2000, le=2100)
    ):
    return await get_league_standings(league_id, season)

@router.get("/{league_id}/top-scorers", response_model=list[TopScorer])
async def league_top_scorers(league_id: int = Path(gt=0), season: int = Query(ge=2000, le=2100)):
    return await get_top_scorers(league_id,season)

@router.get("/{league_id}/teams", response_model=list[Team])
async def league_teams(league_id: int = Path(gt=0), season: int = Query(ge=2000, le=2100)):
    return await get_league_teams(league_id,season)