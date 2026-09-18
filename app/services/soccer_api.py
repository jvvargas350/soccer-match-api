import httpx
from fastapi import HTTPException

from app.config import API_FOOTBALL_KEY, API_FOOTBALL_BASE_URL


async def make_api_request(endpoint: str, params: dict):
    url = f"{API_FOOTBALL_BASE_URL}{endpoint}"

    headers = {
        "x-apisports-key": API_FOOTBALL_KEY
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
            detail=(
                "Soccer data provider returned an error: "
                f"{exc.response.status_code}"
            )
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


def require_response(data: dict, message: str):
    if not data["response"]:
        raise HTTPException(
            status_code=404,
            detail=message
        )

    return data["response"]


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


def transform_events(events: list):
    transformed_events = []

    for event in events:
        player = event.get("player")
        assist = event.get("assist")

        event_data = {
            "elapsed": event["time"]["elapsed"],
            "extra": event["time"].get("extra"),
            "team": event["team"]["name"],
            "player": player.get("name") if player else None,
            "assist": assist.get("name") if assist else None,
            "event_type": event["type"],
            "detail": event["detail"]
        }

        transformed_events.append(event_data)

    return transformed_events


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


def transform_team(team: dict):
    return {
        "team_id": team["id"],
        "name": team["name"],
        "code": team.get("code"),
        "country": team["country"],
        "founded": team.get("founded"),
        "national": team["national"],
        "logo": team.get("logo")
    }


def transform_standing(standing: dict):
    return {
        "rank": standing["rank"],
        "team_id": standing["team"]["id"],
        "team_name": standing["team"]["name"],
        "team_logo": standing["team"]["logo"],
        "points": standing["points"],
        "goals_diff": standing["goalsDiff"],
        "played": standing["all"]["played"],
        "wins": standing["all"]["win"],
        "draws": standing["all"]["draw"],
        "losses": standing["all"]["lose"]
    }


def transform_top_scorer(item: dict):
    player = item["player"]
    statistics = item["statistics"][0]

    return {
        "player_id": player["id"],
        "player_name": player["name"],
        "photo": player["photo"],
        "team_id": statistics["team"]["id"],
        "team_name": statistics["team"]["name"],
        "team_logo": statistics["team"]["logo"],
        "appearances": statistics["games"]["appearences"],
        "goals": statistics["goals"]["total"],
        "assists": statistics["goals"]["assists"]
    }


def transform_player_statistics(statistics: dict):
    return {
        "appearances": statistics["games"]["appearences"],
        "starts": statistics["games"]["lineups"],
        "minutes": statistics["games"]["minutes"],
        "rating": statistics["games"]["rating"],
        "goals": statistics["goals"]["total"],
        "assists": statistics["goals"]["assists"],
        "shots": statistics["shots"]["total"],
        "shots_on_target": statistics["shots"]["on"],
        "passes": statistics["passes"]["total"],
        "key_passes": statistics["passes"]["key"],
        "pass_accuracy": statistics["passes"]["accuracy"],
        "yellow_cards": statistics["cards"]["yellow"],
        "red_cards": statistics["cards"]["red"]
    }


def transform_squad_player(player: dict):
    return {
        "player_id": player["id"],
        "name": player["name"],
        "age": player["age"],
        "number": player["number"],
        "position": player["position"],
        "photo": player["photo"]
    }


async def get_matches_by_date(
    match_date: str,
    league_id: int | None = None,
    season: int | None = None
):
    params = {
        "date": match_date
    }

    if league_id is not None:
        params["league"] = league_id

    if season is not None:
        params["season"] = season

    data = await make_api_request(
        "/fixtures",
        params
    )

    return [
        transform_match(match)
        for match in data["response"]
    ]


async def get_match_by_id(fixture_id: int):
    data = await make_api_request(
        "/fixtures",
        {"id": fixture_id}
    )

    response = require_response(
        data,
        "Match not found"
    )

    match = response[0]
    
    venue = match["fixture"].get("venue")

    statistics = await get_match_statistics(fixture_id)
    events = transform_events(
        match.get("events", [])
    )

    return {
        "fixture_id": match["fixture"]["id"],
        "league": match["league"]["name"],
        "home_team": match["teams"]["home"]["name"],
        "away_team": match["teams"]["away"]["name"],
        "kickoff": match["fixture"]["date"],
        "status": match["fixture"]["status"]["long"],
        "home_score": match["goals"]["home"],
        "away_score": match["goals"]["away"],
        "venue": venue.get("name") if venue else None,
        "city": venue.get("city") if venue else None,
        "referee": match["fixture"].get("referee"),
        "events": events,
        "home_stats": statistics["home"],
        "away_stats": statistics["away"]
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

    return {
        "home": transform_statistics(
            statistics[0]["statistics"]
        ),
        "away": transform_statistics(
            statistics[1]["statistics"]
        )
    }


async def get_team_by_id(team_id: int):
    data = await make_api_request(
        "/teams",
        {"id": team_id}
    )

    response = require_response(
        data,
        "Team not found"
    )

    team = response[0]["team"]

    return transform_team(team)


async def get_team_matches(
    team_id: int,
    season: int
):
    data = await make_api_request(
        "/fixtures",
        {
            "team": team_id,
            "season": season
        }
    )

    return [
        transform_match(match)
        for match in data["response"]
    ]


async def get_league_by_id(league_id: int):
    data = await make_api_request(
        "/leagues",
        {"id": league_id}
    )

    response = require_response(
        data,
        "League not found"
    )

    league_data = response[0]
    league = league_data["league"]
    country = league_data["country"]

    return {
        "league_id": league["id"],
        "name": league["name"],
        "league_type": league["type"],
        "logo": league.get("logo"),
        "country": country.get("name"),
        "country_code": country.get("code"),
        "flag": country.get("flag")
    }


async def get_league_standings(
    league_id: int,
    season: int
):
    data = await make_api_request(
        "/standings",
        {
            "league": league_id,
            "season": season
        }
    )

    response = require_response(
        data,
        "Standings not found"
    )

    standings = (
        response[0]["league"]["standings"][0]
    )

    return [
        transform_standing(standing)
        for standing in standings
    ]


async def get_top_scorers(
    league_id: int,
    season: int
):
    data = await make_api_request(
        "/players/topscorers",
        {
            "league": league_id,
            "season": season
        }
    )

    response = require_response(
        data,
        "Top scorers not found"
    )

    return [
        transform_top_scorer(item)
        for item in response
    ]


async def get_player_by_id(
    player_id: int,
    season: int
):
    data = await make_api_request(
        "/players",
        {
            "id": player_id,
            "season": season
        }
    )

    response = require_response(
        data,
        "Player not found"
    )

    player = response[0]["player"]

    return {
        "player_id": player["id"],
        "name": player["name"],
        "firstname": player["firstname"],
        "lastname": player["lastname"],
        "age": player["age"],
        "nationality": player["nationality"],
        "height": player["height"],
        "weight": player["weight"],
        "photo": player["photo"]
    }


async def get_player_statistics(
    player_id: int,
    season: int,
    league_id: int
):
    data = await make_api_request(
        "/players",
        {
            "id": player_id,
            "season": season,
            "league": league_id
        }
    )

    response = require_response(
        data,
        "Player statistics not found"
    )

    player_data = response[0]

    if not player_data["statistics"]:
        raise HTTPException(
            status_code=404,
            detail="Player statistics not found"
        )

    return transform_player_statistics(
        player_data["statistics"][0]
    )


async def get_team_squad(team_id: int):
    data = await make_api_request(
        "/players/squads",
        {"team": team_id}
    )

    response = require_response(
        data,
        "Squad not found"
    )

    players = response[0]["players"]

    return [
        transform_squad_player(player)
        for player in players
    ]


async def get_league_teams(
    league_id: int,
    season: int
):
    data = await make_api_request(
        "/teams",
        {
            "league": league_id,
            "season": season
        }
    )

    response = require_response(
        data,
        "League teams not found"
    )

    return [
        transform_team(item["team"])
        for item in response
    ]