from datetime import date

from fastapi import APIRouter

from app.models.match import Match

from app.services.soccer_api import get_matches_by_date

router = APIRouter(
    prefix="/matches",
    tags=["Matches"]
)

@router.get("/today", response_model=list[Match])
async def today_matches():
    today = date.today().isoformat()
    return await get_matches_by_date(today)

@router.get("/date/{match_date}", response_model=list[Match])
async def matches_by_date(match_date: date):
    return await get_matches_by_date(match_date.isoformat())