from pydantic import BaseModel

class Team(BaseModel):
    team_id: int
    name: str
    code: str | None = None
    country: str
    founded: int | None = None
    national: bool
    logo: str | None = None