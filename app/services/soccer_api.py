import os 

import httpx 
from fastapi import HTTPException

from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_FOOTBALL_KEY")
if not API_KEY:
    raise ValueError("API_FOOTBALL_KEY environment variable is not set")

BASE_URL = "https://v3.football.api-sports.io"

async def make_api_request(endpoint: str, params: dict):
    url = f"{BASE_URL}{endpoint}"

    headers = {
        "x-apisports-key": API_KEY
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                url,
                headers=headers,
                params=params
            )

        response.raise_for_status()

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="Soccer data provider timed out"
        )

    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Soccer data provider returned an error: {exc.response.status_code}"
        )

    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail="Unable to connect to soccer data provider"
        )

    data = response.json()

    if data.get("errors"):
        raise HTTPException(
            status_code=502,
            detail={
                "message": "Soccer data provider returned an API error",
                "errors": data["errors"]
            }
        )

    return data

def transform_match(match: dict):
    return {
        "fixture_id": match["fixture"]["id"],
        "league": match["league"]["name"],
        "home_team": match["teams"]["home"]["name"],
        "away_team": match["teams"]["away"]["name"],
        "kickoff": match["fixture"]["date"],
        "status": match["fixture"]["status"]["long"],
        "home_score": match["goals"]["home"],
        "away_score": match["goals"]["away"]
    }

async def get_matches_by_date(
    match_date:str,
    league_id: int | None = None,
    season: int | None = None
    ):
    params = {
        "date": match_date}
    if league_id is not None:
        params["league"] = league_id
    if season is not None:
        params["season"] = season
    
    data = await make_api_request(
        "/fixtures",
        params
    )
    
    matches= []
    
    for match in data["response"]:
        match_data = transform_match(match)
        matches.append(match_data)
    
    
    return matches
def transform_events(events: list):
    transformed_events = []
    
    for event in events:
        event_data = {
            "elapsed" : event["time"]["elapsed"],
            "extra" : event["time"].get("extra"),
            "team" : event["team"]["name"],
            "player": event["player"]["name"],
            "assist": event["assist"]["name"],
            "event_type": event["type"],
            "detail": event["detail"]           
        }
        transformed_events.append(event_data)

    return transformed_events

async def get_match_by_id(fixture_id: int):
    data = await make_api_request(
        "/fixtures",
        {"id": fixture_id}
    )

    if not data["response"]:
        raise HTTPException(
            status_code=404,
            detail="Match not found"
        )
    
    match = data["response"][0]
    
    statistics = await get_match_statistics(fixture_id)
    
    events = transform_events(match.get("events", []))
    
    return {
        "fixture_id": match["fixture"]["id"],
        "league": match["league"]["name"],
        "home_team": match["teams"]["home"]["name"],
        "away_team": match["teams"]["away"]["name"],
        "kickoff": match["fixture"]["date"],
        "status": match["fixture"]["status"]["long"],
        "home_score": match["goals"]["home"],
        "away_score": match["goals"]["away"],
        "venue": match["fixture"]["venue"]["name"],
        "city": match["fixture"]["venue"]["city"],
        "referee": match["fixture"]["referee"],
        "events": events,
        "home_stats": statistics["home"],
        "away_stats": statistics["away"]
    }
def transform_statistics(statistics: list):
    stats_by_type = {
        stat["type"]: stat["value"]
        for stat in statistics
    }

    return {
        "shots_on_goal": stats_by_type.get("Shots on Goal"),
        "shots_off_goal": stats_by_type.get("Shots off Goal"),
        "total_shots": stats_by_type.get("Total Shots"),
        "blocked_shots": stats_by_type.get("Blocked Shots"),
        "possession": stats_by_type.get("Ball Possession"),
        "corners": stats_by_type.get("Corner Kicks"),
        "offsides": stats_by_type.get("Offsides"),
        "fouls": stats_by_type.get("Fouls"),
        "yellow_cards": stats_by_type.get("Yellow Cards"),
        "red_cards": stats_by_type.get("Red Cards")
    }
    
async def get_match_statistics(fixture_id: int):
    data = await make_api_request(
        "/fixtures/statistics",
        {"fixture": fixture_id}
    )

    statistics = data["response"]
    
    if len(statistics) < 2:
        return {
            "home": None,
            "away": None
        }
    home_stats = transform_statistics(statistics[0]["statistics"])
    away_stats = transform_statistics(statistics[1]["statistics"])
    
    return {
        "home": home_stats,
        "away": away_stats
    }
async def get_team_by_id(team_id: int):
    data = await make_api_request(
        "/teams",
        {"id": team_id}
    )

    if not data["response"]:
        raise HTTPException(
            status_code=404,
            detail="Team not found"
        )
    
    team = data["response"][0]["team"]
    
    return {
        "team_id": team["id"],
        "name": team["name"],
        "code": team.get("code"),
        "country": team["country"],
        "founded": team.get("founded"),
        "national": team["national"],
        "logo": team.get("logo")
    }
async def get_team_matches(
    team_id: int,
    season:int
):
    data = await make_api_request(
        "/fixtures",
        {"team": team_id, "season": season}
    )

    matches = []
    
    for match in data["response"]:
        match_data = transform_match(match)
        matches.append(match_data)
    
    return matches