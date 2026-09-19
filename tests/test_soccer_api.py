from fastapi import HTTPException
import pytest
import asyncio
import httpx

from app.services.soccer_api import (
    transform_match,
    transform_statistics,
    transform_events,
    transform_team,
    transform_squad_player,
    transform_top_scorer,
    transform_player_statistics,
    get_match_by_id,
    require_response,
    make_api_request
)


def test_transform_match():
    raw_match = {
        "fixture": {
            "id": 12345,
            "date": "2026-09-18T19:00:00Z",
            "status": {
                "long": "Match Finished"
            }
        },
        "league": {
            "name": "Premier League"
        },
        "teams": {
            "home": {
                "name": "Arsenal"
            },
            "away": {
                "name": "Chelsea"
            }
        },
        "goals": {
            "home": 2,
            "away": 1
        }
    }

    result = transform_match(raw_match)

    assert result == {
        "fixture_id": 12345,
        "league": "Premier League",
        "home_team": "Arsenal",
        "away_team": "Chelsea",
        "kickoff": "2026-09-18T19:00:00Z",
        "status": "Match Finished",
        "home_score": 2,
        "away_score": 1
    }


def test_transform_statistics():
    raw_statistics = [
        {
            "type": "Shots on Goal",
            "value": 7
        },
        {
            "type": "Total Shots",
            "value": 15
        },
        {
            "type": "Ball Possession",
            "value": "62%"
        },
        {
            "type": "Corner Kicks",
            "value": 8
        },
        {
            "type": "Yellow Cards",
            "value": 2
        }
    ]

    result = transform_statistics(raw_statistics)

    assert result["shots_on_goal"] == 7
    assert result["total_shots"] == 15
    assert result["possession"] == "62%"
    assert result["corners"] == 8
    assert result["yellow_cards"] == 2
    
def test_transform_events():
    raw_events = [
        {
            "time": {
                "elapsed": 25,
                "extra": None
            },
            "team": {
                "name": "Arsenal"
            },
            "player": {
                "name": "Test Player"
            },
            "assist": {
                "name": "Test Assist"
            },
            "type": "Goal",
            "detail": "Normal Goal"
        }
    ]

    result = transform_events(raw_events)

    assert len(result) == 1
    assert result[0]["elapsed"] == 25
    assert result[0]["team"] == "Arsenal"
    assert result[0]["player"] == "Test Player"
    assert result[0]["assist"] == "Test Assist"
    assert result[0]["event_type"] == "Goal"
    assert result[0]["detail"] == "Normal Goal"


def test_transform_team():
    raw_team = {
        "id": 42,
        "name": "Arsenal",
        "code": "ARS",
        "country": "England",
        "founded": 1886,
        "national": False,
        "logo": "https://example.com/arsenal.png"
    }

    result = transform_team(raw_team)

    assert result == {
        "team_id": 42,
        "name": "Arsenal",
        "code": "ARS",
        "country": "England",
        "founded": 1886,
        "national": False,
        "logo": "https://example.com/arsenal.png"
    }
    
def test_transform_event_with_missing_player_and_assist():
    raw_events = [
        {
            "time": {
                "elapsed": 90,
                "extra": 3
            },
            "team": {
                "name": "Arsenal"
            },
            "player": None,
            "assist": None,
            "type": "Card",
            "detail": "Yellow Card"
        }
    ]

    result = transform_events(raw_events)

    assert len(result) == 1
    assert result[0]["player"] is None
    assert result[0]["assist"] is None
    assert result[0]["elapsed"] == 90
    assert result[0]["extra"] == 3
    
@pytest.mark.anyio
async def test_match_with_missing_venue(monkeypatch):
    async def mock_make_api_request(endpoint: str, params: dict):
        return {
            "response": [
                {
                    "fixture": {
                        "id": 12345,
                        "date": "2026-09-18T19:00:00Z",
                        "status": {
                            "long": "Match Finished"
                        },
                        "venue": None,
                        "referee": None
                    },
                    "league": {
                        "name": "Premier League"
                    },
                    "teams": {
                        "home": {
                            "name": "Arsenal"
                        },
                        "away": {
                            "name": "Chelsea"
                        }
                    },
                    "goals": {
                        "home": 2,
                        "away": 1
                    },
                    "events": []
                }
            ]
        }

    async def mock_get_match_statistics(fixture_id: int):
        return {
            "home": None,
            "away": None
        }

    monkeypatch.setattr(
        "app.services.soccer_api.make_api_request",
        mock_make_api_request
    )

    monkeypatch.setattr(
        "app.services.soccer_api.get_match_statistics",
        mock_get_match_statistics
    )

    result = await get_match_by_id(12345)

    assert result["venue"] is None
    assert result["city"] is None
    assert result["referee"] is None

def test_require_response_returns_data():
    data = {
        "response": [
            {
                "id": 123
            }
        ]
    }

    result = require_response(
        data,
        "Not found"
    )

    assert result == [
        {
            "id": 123
        }
    ]


def test_require_response_raises_404():
    data = {
        "response": []
    }

    with pytest.raises(HTTPException) as exc:
        require_response(
            data,
            "Team not found"
        )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Team not found"
    
def test_make_api_request_timeout(monkeypatch):
    monkeypatch.setattr(
    "app.services.soccer_api.API_FOOTBALL_KEY",
    "test-api-key"
)
    async def mock_get(*args, **kwargs):
        raise httpx.TimeoutException(
            "Request timed out"
        )

    monkeypatch.setattr(
        httpx.AsyncClient,
        "get",
        mock_get
    )

    with pytest.raises(HTTPException) as exc:
        asyncio.run(
            make_api_request(
                "/fixtures",
                {"id": 123}
            )
        )

    assert exc.value.status_code == 504
    assert exc.value.detail == (
        "Soccer data provider timed out"
    )


def test_make_api_request_connection_error(monkeypatch):
    monkeypatch.setattr(
    "app.services.soccer_api.API_FOOTBALL_KEY",
    "test-api-key"
)
    async def mock_get(*args, **kwargs):
        raise httpx.RequestError(
            "Connection failed"
        )

    monkeypatch.setattr(
        httpx.AsyncClient,
        "get",
        mock_get
    )

    with pytest.raises(HTTPException) as exc:
        asyncio.run(
            make_api_request(
                "/fixtures",
                {"id": 123}
            )
        )

    assert exc.value.status_code == 503
    assert exc.value.detail == (
        "Unable to connect to soccer data provider"
    )
    
def test_make_api_request_http_error(monkeypatch):
    monkeypatch.setattr(
    "app.services.soccer_api.API_FOOTBALL_KEY",
    "test-api-key"
)
    async def mock_get(*args, **kwargs):
        request = httpx.Request(
            "GET",
            "https://example.com"
        )

        response = httpx.Response(
            500,
            request=request
        )

        raise httpx.HTTPStatusError(
            "Server error",
            request=request,
            response=response
        )

    monkeypatch.setattr(
        httpx.AsyncClient,
        "get",
        mock_get
    )

    with pytest.raises(HTTPException) as exc:
        asyncio.run(
            make_api_request(
                "/fixtures",
                {"id": 123}
            )
        )

    assert exc.value.status_code == 502
    assert exc.value.detail == (
        "Soccer data provider returned an error: 500"
    )


def test_make_api_request_api_error(monkeypatch):
    monkeypatch.setattr(
    "app.services.soccer_api.API_FOOTBALL_KEY",
    "test-api-key"
)
    class MockResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "errors": {
                    "plan": "Access denied"
                },
                "response": []
            }

    async def mock_get(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr(
        httpx.AsyncClient,
        "get",
        mock_get
    )

    with pytest.raises(HTTPException) as exc:
        asyncio.run(
            make_api_request(
                "/fixtures",
                {"id": 123}
            )
        )

    assert exc.value.status_code == 502
    assert exc.value.detail == {
        "message": (
            "Soccer data provider returned an API error"
        ),
        "errors": {
            "plan": "Access denied"
        }
    }
    
def test_transform_team_with_missing_optional_fields():
    raw_team = {
        "id": 100,
        "name": "Test FC",
        "country": "England",
        "national": False
    }

    result = transform_team(raw_team)

    assert result == {
        "team_id": 100,
        "name": "Test FC",
        "code": None,
        "country": "England",
        "founded": None,
        "national": False,
        "logo": None
    }

def test_transform_squad_player_with_missing_optional_fields():
    raw_player = {
        "id": 123,
        "name": "Test Player",
        "position": "Midfielder"
    }

    result = transform_squad_player(raw_player)

    assert result == {
        "player_id": 123,
        "name": "Test Player",
        "age": None,
        "number": None,
        "position": "Midfielder",
        "photo": None
    }

def test_transform_top_scorer_with_missing_optional_fields():
    raw_scorer = {
        "player": {
            "id": 123,
            "name": "Test Player",
            "photo": None
        },
        "statistics": [
            {
                "team": {
                    "id": 42,
                    "name": "Test FC",
                    "logo": None
                },
                "games": {},
                "goals": {}
            }
        ]
    }

    result = transform_top_scorer(raw_scorer)

    assert result == {
        "player_id": 123,
        "player_name": "Test Player",
        "photo": None,
        "team_id": 42,
        "team_name": "Test FC",
        "team_logo": None,
        "appearances": None,
        "goals": None,
        "assists": None
    }
    
def test_transform_player_statistics_with_missing_optional_fields():
    raw_statistics = {
        "games": {},
        "goals": {},
        "shots": {},
        "passes": {},
        "cards": {}
    }

    result = transform_player_statistics(raw_statistics)

    assert result == {
        "appearances": None,
        "starts": None,
        "minutes": None,
        "rating": None,
        "goals": None,
        "assists": None,
        "shots": None,
        "shots_on_target": None,
        "passes": None,
        "key_passes": None,
        "pass_accuracy": None,
        "yellow_cards": None,
        "red_cards": None
    }
    
def test_make_api_request_without_api_key(monkeypatch):
    monkeypatch.setattr(
        "app.services.soccer_api.API_FOOTBALL_KEY",
        None
    )

    with pytest.raises(HTTPException) as exc:
        asyncio.run(
            make_api_request(
                "/fixtures",
                {"id": 123}
            )
        )

    assert exc.value.status_code == 503
    assert exc.value.detail == (
        "Soccer data provider API key is not configured"
    )