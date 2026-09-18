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
    
class PlayerStatistics(BaseModel):
    appearances: int | None = None
    starts: int | None = None
    minutes: int | None = None
    rating: str | None = None
    goals: int | None = None
    assists: int | None = None
    shots: int | None = None
    shots_on_target: int | None = None
    passes: int | None = None
    key_passes: int | None = None
    pass_accuracy: int | None = None
    yellow_cards: int | None = None
    red_cards: int | None = None