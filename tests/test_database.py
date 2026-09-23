import pytest

from app.services.soccer_api import save_team_to_database

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.db_models.team import TeamDB


engine = create_engine(
    "sqlite:///:memory:"
)

TestingSessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

Base.metadata.create_all(bind=engine)


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