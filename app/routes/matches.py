from datetime import date

from fastapi import APIRouter

from app.models.match import Match

from app.services.soccer_api import get_matches_by_date, get_match_by_id

router = APIRouter(
    prefix="/matches",
    tags=["Matches"]
)

@router.get("/today", response_model=list[Match])
async def today_matches(league_id: int | None = None,
    season: int | None = None):
    today = date.today().isoformat()
    return await get_matches_by_date(today,
        league_id,
        season)

@router.get("/date/{match_date}", response_model=list[Match])
async def matches_by_date(match_date: date,
    league_id: int | None = None,
    season: int | None = None):
    return await get_matches_by_date(match_date.isoformat(),
        league_id,
        season)
    
@router.get("/{fixture_id}", response_model=Match)
async def match_by_id(fixture_id: int):
    return await get_match_by_id(fixture_id)