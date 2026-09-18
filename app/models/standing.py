from pydantic import BaseModel

class Standing(BaseModel):
    rank: int
    team_id: int
    team_name: str
    team_logo: str | None = None
    points: int
    goals_diff: int
    played: int
    wins: int
    draws: int
    losses: int