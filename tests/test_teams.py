from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_get_team(monkeypatch):
    async def mock_get_team_by_id(team_id: int):
        return {
            "team_id": 42,
            "name": "Arsenal",
            "code": "ARS",
            "country": "England",
            "founded": 1886,
            "national": False,
            "logo": "https://example.com/arsenal.png"
        }

    monkeypatch.setattr(
        "app.routes.teams.get_team_by_id",
        mock_get_team_by_id
    )

    response = client.get("/teams/42")

    assert response.status_code == 200

    data = response.json()

    assert data["team_id"] == 42
    assert data["name"] == "Arsenal"
    assert data["code"] == "ARS"
    assert data["country"] == "England"


def test_invalid_team_id():
    response = client.get("/teams/0")

    assert response.status_code == 422