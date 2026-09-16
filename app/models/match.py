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
    
class MatchEvent(BaseModel):
    elapsed: int | None = None 
    extra: int | None = None
    team: str
    player: str | None = None
    assist: str | None = None
    event_type: str
    detail: str
    
class MatchDetail(Match):
    venue: str | None = None
    city: str | None = None
    referee: str | None = None
    events: list[MatchEvent] =[]