from pydantic import BaseModel


class TopScorer(BaseModel):
    player_id: int
    player_name: str
    photo: str | None = None
    team_id: int
    team_name: str
    team_logo: str | None = None
    appearances: int | None = None
    goals: int | None = None
    assists: int | None = None
    
class Player(BaseModel):
    player_id: int
    name: str
    firstname: str | None = None
    lastname: str | None = None
    age: int | None = None
    nationality: str | None = None
    height: str | None = None
    weight: str | None = None
    photo: str | None = None