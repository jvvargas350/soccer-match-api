from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SavedLeague(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    api_league_id: int
    name: str


class SavedTeam(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    api_team_id: int
    name: str


class SavedMatch(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    api_fixture_id: int

    league: SavedLeague | None
    home_team: SavedTeam | None
    away_team: SavedTeam | None

    kickoff: datetime
    status: str

    home_score: int | None
    away_score: int | None

    venue: str | None
    city: str | None
    referee: str | None

    created_at: datetime