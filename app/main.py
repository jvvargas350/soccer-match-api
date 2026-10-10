from fastapi import FastAPI

from app.routes.matches import router as matches_router

from app.routes.teams import router as teams_router

from app.routes.leagues import router as leagues_router

from app.routes.players import router as players_router

from app.routes import saved

app = FastAPI(
    title="Soccer Match API",
    description="API for soccer match data",
    version="0.1.0",
)

app.include_router(matches_router)
app.include_router(teams_router)
app.include_router(leagues_router)
app.include_router(players_router)
app.include_router(saved.router)
@app.get("/")
def home():
    return {"message": "Soccer Match API is running"}
@app.get("/health")
def health_check():
    return {"status": "ok"}