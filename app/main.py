from fastapi import FastAPI

from app.routes.matches import router as matches_router

app = FastAPI()

app.include_router(matches_router)

@app.get("/")
def home():
    return {"message": "Soccer Match API is running"}
