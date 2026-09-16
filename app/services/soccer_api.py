import os 

import httpx 
from fastapi import HTTPException

from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_FOOTBALL_KEY")
if not API_KEY:
    raise ValueError("API_FOOTBALL_KEY environment variable is not set")

BASE_URL = "https://v3.football.api-sports.io"

async def get_matches_by_date(
    match_date:str,
    league_id: int | None = None,
    season: int | None = None
    
    ):
    url = f"{BASE_URL}/fixtures"
    
    headers = {
        "x-apisports-key": API_KEY
        }
    params = {
        "date": match_date
    }
    if league_id is not None:
        params["league"] = league_id
    if season is not None:
        params["season"] = season
    try:
        async with httpx.AsyncClient(timeout = 10.0) as client:
            response = await client.get(
                url, 
                headers=headers,
                params = params
            )
        response.raise_for_status()
    
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Soccer data provider timed out")
        
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
    
    matches= []
    
    for match in data["response"]:
        match_data = {
            "fixture_id": match["fixture"]["id"],
            "league": match["league"]["name"],
            "home_team": match["teams"]["home"]["name"],
            "away_team": match["teams"]["away"]["name"],
            "kickoff": match["fixture"]["date"],
            "status": match["fixture"]["status"]["long"],
            "home_score": match["goals"]["home"],
            "away_score": match["goals"]["away"]
        }
        matches.append(match_data)
    
    
    return matches


async def get_match_by_id(fixture_id: int):
    url = f"{BASE_URL}/fixtures"

    headers = {
        "x-apisports-key": API_KEY
    }

    params = {
        "id": fixture_id
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

    if not data["response"]:
        raise HTTPException(
            status_code=404,
            detail="Match not found"
        )
    
    match = data["response"][0]
    
    events = []
    
    for event in match.get("events", []):
        event_data = {
            "elapsed" : event["time"]["elapsed"],
            "extra" : event["time"].get("extra"),
            "team" : event["team"]["name"],
            "player": event["player"]["name"],
            "assist": event["assist"]["name"],
            "event_type": event["type"],
            "detail": event["detail"]           
        }
        events.append(event_data)
    
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
        "referee": match["fixture"]["referee"]
    }