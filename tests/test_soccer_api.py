from app.services.soccer_api import (
    transform_match,
    transform_statistics,
    transform_events,
    transform_team
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