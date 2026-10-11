from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.saved_match import SavedMatch, PaginatedSavedMatches
from app.services.saved_matches import (
    get_saved_matches,
    get_saved_match_by_id,
)


router = APIRouter(prefix="/saved", tags=["Saved Data"])


@router.get("/matches", response_model=PaginatedSavedMatches)
def read_saved_matches(
    league_id: int | None = Query(default=None, gt=0),
    team_id: int | None = Query(default=None, gt=0),
    status: str | None = Query(default=None, min_length=1),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    sort_by: Literal["kickoff", "created_at"] = Query(default="kickoff"),
    sort_order: Literal["asc", "desc"] = Query(default="desc"),
    db: Session = Depends(get_db),
):
    return get_saved_matches(
        db=db,
        league_id=league_id,
        team_id=team_id,
        status=status,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.get("/matches/{fixture_id}", response_model=SavedMatch)
def read_saved_match(
    fixture_id: int = Path(gt=0),
    db: Session = Depends(get_db),
):
    match = get_saved_match_by_id(db, fixture_id)

    if match is None:
        raise HTTPException(
            status_code=404,
            detail="Saved match not found",
        )

    return match