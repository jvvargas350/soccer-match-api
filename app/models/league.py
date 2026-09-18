from pydantic import BaseModel

class League(BaseModel):
    league_id: int
    name: str
    league_type: str
    logo: str | None = None
    country: str | None = None
    country_code: str | None = None
    flag: str | None = None