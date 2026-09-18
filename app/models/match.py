from datetime import datetime
from pydantic import BaseModel, Field 

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
    
class TeamStats(BaseModel):
    shots_on_goal: int | None = None
    shots_off_goal: int | None = None
    total_shots: int | None = None
    blocked_shots: int | None = None
    possession: str | None = None
    corners: int | None = None
    offsides: int | None = None
    fouls: int | None = None
    yellow_cards: int | None = None
    red_cards: int | None = None
    
class MatchDetail(Match):
    venue: str | None = None
    city: str | None = None
    referee: str | None = None
    events: list[MatchEvent] = Field(default_factory=list)
    home_stats: TeamStats | None = None
    away_stats: TeamStats | None = None