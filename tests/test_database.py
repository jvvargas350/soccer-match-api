import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.db_models.team import TeamDB
from app.db_models.league import LeagueDB
from app.db_models.match import MatchDB

from datetime import datetime, timezone

from app.services.soccer_api import (
    save_team_to_database,
    save_league_to_database,
    save_match_to_database
)

engine = create_engine(
    "sqlite:///:memory:"
)

TestingSessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

Base.metadata.create_all(bind=engine)
@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    yield

    Base.metadata.drop_all(bind=engine)

def test_save_team_to_database():
    db = TestingSessionLocal()

    team = TeamDB(
        api_team_id=42,
        name="Arsenal",
        code="ARS",
        country="England",
        founded=1886,
        national=False,
        logo="https://example.com/arsenal.png"
    )

    db.add(team)
    db.commit()
    db.refresh(team)

    saved_team = (
        db.query(TeamDB)
        .filter(TeamDB.api_team_id == 42)
        .first()
    )

    assert saved_team is not None
    assert saved_team.name == "Arsenal"
    assert saved_team.code == "ARS"
    assert saved_team.country == "England"
    assert saved_team.founded == 1886
    assert saved_team.national is False

    db.close()
    
@pytest.mark.anyio
async def test_save_team_to_database_updates_existing_team(
    monkeypatch
):
    db = TestingSessionLocal()

    async def fake_get_team_by_id(team_id):
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
        "app.services.soccer_api.get_team_by_id",
        fake_get_team_by_id
    )

    await save_team_to_database(42, db)

    saved_team = (
        db.query(TeamDB)
        .filter(TeamDB.api_team_id == 42)
        .first()
    )

    assert saved_team is not None
    assert saved_team.name == "Arsenal"

    saved_team.name = "Old Arsenal Name"
    db.commit()

    await save_team_to_database(42, db)

    teams = (
        db.query(TeamDB)
        .filter(TeamDB.api_team_id == 42)
        .all()
    )

    assert len(teams) == 1
    assert teams[0].name == "Arsenal"

    db.close()
    
@pytest.mark.anyio
async def test_save_match_to_database_creates_relationships(
    monkeypatch
):
    db = TestingSessionLocal()

    async def fake_make_api_request(endpoint, params):
        return {
            "response": [
                {
                    "fixture": {
                        "id": 1508564,
                        "date": "2026-10-03T00:00:00Z",
                        "status": {
                            "long": "Match Finished"
                        },
                        "venue": {
                            "name": "Exploria Stadium",
                            "city": "Orlando"
                        },
                        "referee": "Test Referee"
                    },
                    "league": {
                        "id": 999,
                        "name": "Test League"
                    },
                    "teams": {
                        "home": {
                            "id": 1001,
                            "name": "Home FC"
                        },
                        "away": {
                            "id": 1002,
                            "name": "Away FC"
                        }
                    },
                    "goals": {
                        "home": 1,
                        "away": 2
                    }
                }
            ]
        }

    async def fake_save_league(league_id, db):
        league = LeagueDB(
            api_league_id=league_id,
            name="Test League",
            league_type="League",
            country="Test Country"
        )

        db.add(league)
        db.commit()
        db.refresh(league)

        return league

    async def fake_save_team(team_id, db):
        team = TeamDB(
            api_team_id=team_id,
            name=(
                "Home FC"
                if team_id == 1001
                else "Away FC"
            ),
            country="Test Country",
            national=False
        )

        db.add(team)
        db.commit()
        db.refresh(team)

        return team

    monkeypatch.setattr(
        "app.services.soccer_api.make_api_request",
        fake_make_api_request
    )

    monkeypatch.setattr(
        "app.services.soccer_api.save_league_to_database",
        fake_save_league
    )

    monkeypatch.setattr(
        "app.services.soccer_api.save_team_to_database",
        fake_save_team
    )

    match = await save_match_to_database(
        1508564,
        db
    )

    assert match.api_fixture_id == 1508564
    assert match.home_score == 1
    assert match.away_score == 2

    league = db.get(LeagueDB, match.league_id)
    home_team = db.get(TeamDB, match.home_team_id)
    away_team = db.get(TeamDB, match.away_team_id)

    assert league.name == "Test League"
    assert home_team.name == "Home FC"
    assert away_team.name == "Away FC"

    db.close()
    
@pytest.mark.anyio
async def test_save_match_to_database_updates_existing_match(
    monkeypatch
):
    db = TestingSessionLocal()

    league = LeagueDB(
        api_league_id=999,
        name="Test League",
        league_type="League",
        country="Test Country"
    )

    home_team = TeamDB(
        api_team_id=1001,
        name="Home FC",
        country="Test Country",
        national=False
    )

    away_team = TeamDB(
        api_team_id=1002,
        name="Away FC",
        country="Test Country",
        national=False
    )

    db.add_all([
        league,
        home_team,
        away_team
    ])
    db.commit()

    async def fake_make_api_request(endpoint, params):
        return {
            "response": [
                {
                    "fixture": {
                        "id": 1508564,
                        "date": "2026-10-03T00:00:00Z",
                        "status": {
                            "long": "Match Finished"
                        },
                        "venue": {
                            "name": "Exploria Stadium",
                            "city": "Orlando"
                        },
                        "referee": "Test Referee"
                    },
                    "league": {
                        "id": 999
                    },
                    "teams": {
                        "home": {
                            "id": 1001
                        },
                        "away": {
                            "id": 1002
                        }
                    },
                    "goals": {
                        "home": 1,
                        "away": 2
                    }
                }
            ]
        }

    monkeypatch.setattr(
        "app.services.soccer_api.make_api_request",
        fake_make_api_request
    )

    await save_match_to_database(
        1508564,
        db
    )


    saved_match = (
        db.query(MatchDB)
        .filter(
            MatchDB.api_fixture_id == 1508564
        )
        .first()
    )

    saved_match.home_score = 0
    saved_match.away_score = 0
    db.commit()


    await save_match_to_database(
        1508564,
        db
    )

    matches = (
        db.query(MatchDB)
        .filter(
            MatchDB.api_fixture_id == 1508564
        )
        .all()
    )

    assert len(matches) == 1
    assert matches[0].home_score == 1
    assert matches[0].away_score == 2
    assert matches[0].status == "Match Finished"

    db.close()
    
def test_match_database_relationships():
    db = TestingSessionLocal()

    league = LeagueDB(
        api_league_id=500,
        name="Relationship Test League",
        league_type="League",
        country="Test Country"
    )

    home_team = TeamDB(
        api_team_id=501,
        name="Home Team",
        country="Test Country",
        national=False
    )

    away_team = TeamDB(
        api_team_id=502,
        name="Away Team",
        country="Test Country",
        national=False
    )

    db.add_all([
        league,
        home_team,
        away_team
    ])
    db.commit()

    match = MatchDB(
        api_fixture_id=503,
        league_id=league.id,
        home_team_id=home_team.id,
        away_team_id=away_team.id,
        kickoff=datetime(
            2026, 10, 4, 19, 0,
            tzinfo=timezone.utc
        ),
        status="Match Finished",
        home_score=2,
        away_score=1
    )

    db.add(match)
    db.commit()
    db.refresh(match)

    assert match.league.name == "Relationship Test League"
    assert match.home_team.name == "Home Team"
    assert match.away_team.name == "Away Team"

    assert match in league.matches
    assert match in home_team.home_matches
    assert match in away_team.away_matches

    db.close()