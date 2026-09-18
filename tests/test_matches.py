from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_get_match(monkeypatch):
    async def mock_get_match_by_id(fixture_id: int):
        return {
            "fixture_id": 1519495,
            "league": "Liga Pro",
            "home_team": "Universidad Catolica",
            "away_team": "Orense SC",
            "kickoff": "2026-09-15T00:00:00Z",
            "status": "Match Finished",
            "home_score": 2,
            "away_score": 1,
            "venue": "Olimpico Atahualpa",
            "city": "Quito",
            "referee": "Test Referee",
            "events": [],
            "home_stats": None,
            "away_stats": None
        }

    monkeypatch.setattr(
        "app.routes.matches.get_match_by_id",
        mock_get_match_by_id
    )

    response = client.get("/matches/1519495")

    assert response.status_code == 200

    data = response.json()

    assert data["fixture_id"] == 1519495
    assert data["home_team"] == "Universidad Catolica"
    assert data["away_team"] == "Orense SC"
    assert data["home_score"] == 2
    assert data["away_score"] == 1


def test_invalid_fixture_id():
    response = client.get("/matches/0")

    assert response.status_code == 422
    
    
def test_today_matches(monkeypatch):
    async def mock_get_matches_by_date(
        match_date: str,
        league_id=None,
        season=None
    ):
        return [
            {
                "fixture_id": 12345,
                "league": "Premier League",
                "home_team": "Arsenal",
                "away_team": "Chelsea",
                "kickoff": "2026-09-18T19:00:00Z",
                "status": "Not Started",
                "home_score": None,
                "away_score": None
            }
        ]

    monkeypatch.setattr(
        "app.routes.matches.get_matches_by_date",
        mock_get_matches_by_date
    )

    response = client.get("/matches/today")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["fixture_id"] == 12345
    assert data[0]["home_team"] == "Arsenal"
    assert data[0]["away_team"] == "Chelsea"


def test_matches_by_date(monkeypatch):
    async def mock_get_matches_by_date(
        match_date: str,
        league_id=None,
        season=None
    ):
        assert match_date == "2026-09-18"

        return []

    monkeypatch.setattr(
        "app.routes.matches.get_matches_by_date",
        mock_get_matches_by_date
    )

    response = client.get(
        "/matches/date/2026-09-18"
    )

    assert response.status_code == 200
    assert response.json() == []