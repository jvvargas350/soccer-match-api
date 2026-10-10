from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.saved_match import SavedMatch
from app.services.saved_matches import (
    get_saved_matches,
    get_saved_match_by_id,
)


router = APIRouter(prefix="/saved", tags=["Saved Data"])


@router.get("/matches", response_model=list[SavedMatch])
def read_saved_matches(
    league_id: int | None = Query(default=None, gt=0),
    team_id: int | None = Query(default=None, gt=0),
    status: str | None = Query(default=None, min_length=1),
    db: Session = Depends(get_db),
):
    return get_saved_matches(
        db=db,
        league_id=league_id,
        team_id=team_id,
        status=status,
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