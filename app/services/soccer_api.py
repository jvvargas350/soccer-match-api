import os 

import httpx 

from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_FOOTBALL_KEY")
if not API_KEY:
    raise ValueError("API_FOOTBALL_KEY environment variable is not set")

BASE_URL = "https://v3.football.api-sports.io"

async def get_matches_by_date(match_date:str):
    url = f"{BASE_URL}/fixtures"
    
    headers = {
        "x-apisports-key": API_KEY
        }
    params = {
        "date": match_date
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(
            url, 
            headers=headers,
            params = params
        )
    response.raise_for_status()
    
    data = response.json()
    
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