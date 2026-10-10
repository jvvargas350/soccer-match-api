from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.db_models import TeamDB, LeagueDB, MatchDB


# Create an isolated SQLite database for these tests.
test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
)


@pytest.fixture
def client():
    # Start every test with a clean database.
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.pop(get_db, None)

    Base.metadata.drop_all(bind=test_engine)


def create_sample_match():
    """Insert one league, two teams, and one match."""

    with TestingSessionLocal() as db:
        league = LeagueDB(
            api_league_id=39,
            name="Premier League",
            league_type="League",
            country="England",
        )

        home_team = TeamDB(
            api_team_id=42,
            name="Arsenal",
            country="England",
            national=False,
        )

        away_team = TeamDB(
            api_team_id=39,
            name="Wolves",
            country="England",
            national=False,
        )

        db.add_all([league, home_team, away_team])
        db.flush()

        match = MatchDB(
            api_fixture_id=123456,
            league_id=league.id,
            home_team_id=home_team.id,
            away_team_id=away_team.id,
            kickoff=datetime(2026, 10, 10, 15, 0, tzinfo=timezone.utc),
            status="Match Finished",
            home_score=2,
            away_score=1,
            venue="Emirates Stadium",
            city="London",
            referee="Test Referee",
        )

        db.add(match)
        db.commit()


def test_get_saved_matches_returns_empty_list(client):
    response = client.get("/saved/matches")

    assert response.status_code == 200
    assert response.json() == []


def test_get_saved_matches_returns_saved_match(client):
    create_sample_match()

    response = client.get("/saved/matches")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["api_fixture_id"] == 123456
    assert data[0]["status"] == "Match Finished"
    assert data[0]["home_score"] == 2
    assert data[0]["away_score"] == 1
    assert data[0]["created_at"] is not None


def test_get_saved_matches_includes_related_data(client):
    create_sample_match()

    response = client.get("/saved/matches")

    assert response.status_code == 200

    match = response.json()[0]

    assert match["league"]["name"] == "Premier League"
    assert match["league"]["api_league_id"] == 39

    assert match["home_team"]["name"] == "Arsenal"
    assert match["home_team"]["api_team_id"] == 42

    assert match["away_team"]["name"] == "Wolves"
    assert match["away_team"]["api_team_id"] == 39
    
def test_get_saved_match_by_id_returns_match(client):
    create_sample_match()

    response = client.get("/saved/matches/123456")

    assert response.status_code == 200

    match = response.json()

    assert match["api_fixture_id"] == 123456
    assert match["status"] == "Match Finished"
    assert match["home_score"] == 2
    assert match["away_score"] == 1

    assert match["league"]["name"] == "Premier League"
    assert match["home_team"]["name"] == "Arsenal"
    assert match["away_team"]["name"] == "Wolves"


def test_get_saved_match_by_id_not_found(client):
    response = client.get("/saved/matches/999999999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Saved match not found"
    }


def test_get_saved_match_by_id_invalid_id(client):
    response = client.get("/saved/matches/-1")

    assert response.status_code == 422
    
    
def test_filter_saved_matches_by_league(client):
    create_sample_match()

    response = client.get("/saved/matches?league_id=39")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["api_fixture_id"] == 123456


def test_filter_saved_matches_by_team(client):
    create_sample_match()

    response = client.get("/saved/matches?team_id=42")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["home_team"]["name"] == "Arsenal"


def test_filter_saved_matches_by_away_team(client):
    create_sample_match()

    response = client.get("/saved/matches?team_id=39")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["away_team"]["name"] == "Wolves"


def test_filter_saved_matches_by_status(client):
    create_sample_match()

    response = client.get(
        "/saved/matches",
        params={"status": "Match Finished"},
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["status"] == "Match Finished"


def test_filter_saved_matches_no_matches(client):
    create_sample_match()

    response = client.get("/saved/matches?league_id=999999")

    assert response.status_code == 200
    assert response.json() == []


def test_filter_saved_matches_invalid_team_id(client):
    response = client.get("/saved/matches?team_id=-1")

    assert response.status_code == 422