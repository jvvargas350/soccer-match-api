from pydantic import BaseModel

class Team(BaseModel):
    team_id: int
    name: str
    code: str | None = None
    country: str
    founded: int | None = None
    national: bool
    logo: str | None = None
    
class SquadPlayer(BaseModel):
    player_id: int
    name: str
    age: int | None = None
    number: int | None = None
    position: str | None = None
    photo: str | None = None