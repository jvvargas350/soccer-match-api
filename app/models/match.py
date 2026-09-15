from datetime import datetime
from pydantic import BaseModel 

class Match(BaseModel):
    fixture_id: int
    league: str
    home_team: str
    away_team: str
    kickoff: datetime
    status: str
    home_score: int | None = None
    away_score: int | None = None