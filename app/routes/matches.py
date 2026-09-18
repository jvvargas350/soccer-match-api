from datetime import date

from fastapi import APIRouter, Query, Path

from app.models.match import Match, MatchDetail

from app.services.soccer_api import (
    get_matches_by_date,
    get_match_by_id,
    get_match_statistics
)

router = APIRouter(
    prefix="/matches",
    tags=["Matches"]
)

@router.get("/today", response_model=list[Match])
async def today_matches(league_id: int | None = Query(default=None, gt=0),
    season: int | None = Query(default=None, ge=2000, le=2100)
    ):
    today = date.today().isoformat()
    return await get_matches_by_date(today,
        league_id,
        season)

@router.get("/date/{match_date}", response_model=list[Match])
async def matches_by_date(match_date: date,
    league_id: int | None = Query(default=None, gt=0),
    season: int | None = Query(default=None, ge=2000, le=2100)
    ):
    return await get_matches_by_date(match_date.isoformat(),
        league_id,
        season)

@router.get("/{fixture_id}/statistics")
async def match_statistics(
    fixture_id: int = Path(gt=0)
    ):
    return await get_match_statistics(fixture_id)

@router.get("/{fixture_id}", response_model=MatchDetail)
async def match_by_id(
    fixture_id: int = Path(gt=0)
    ):
    return await get_match_by_id(fixture_id)