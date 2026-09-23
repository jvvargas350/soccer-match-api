from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.orm import Session

from app.database import get_db


from app.models.league import League
from app.models.standing import Standing
from app.models.player import TopScorer
from app.models.team import Team
from app.services.soccer_api import (get_league_by_id, 
                                     get_league_standings, 
                                     get_top_scorers, 
                                     get_league_teams, 
                                     save_league_to_database
                                     )

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

@router.post("/{league_id}/save")
async def save_league(
    league_id: int = Path(gt=0),
    db: Session = Depends(get_db)
):
    league = await save_league_to_database(
        league_id,
        db
    )

    return {
        "message": "League saved successfully",
        "league": {
            "id": league.id,
            "api_league_id": league.api_league_id,
            "name": league.name,
            "league_type": league.league_type,
            "logo": league.logo,
            "country": league.country,
            "country_code": league.country_code,
            "flag": league.flag
        }
    }