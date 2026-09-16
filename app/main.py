from fastapi import FastAPI

from app.routes.matches import router as matches_router

app = FastAPI(
    title="Soccer Match API",
    description="API for soccer match data",
    version="0.1.0",
)

app.include_router(matches_router)



@app.get("/")
def home():
    return {"message": "Soccer Match API is running"}
@app.get("/health")
def health_check():
    return {"status": "ok"}