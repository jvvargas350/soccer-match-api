from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.saved_match import SavedMatch
from app.services.saved_matches import get_saved_matches


router = APIRouter(prefix="/saved", tags=["Saved Data"])


@router.get("/matches", response_model=list[SavedMatch])
def read_saved_matches(db: Session = Depends(get_db)):
    return get_saved_matches(db)