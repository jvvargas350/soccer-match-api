# Soccer Match API

A REST API built with FastAPI that retrieves and processes real-world soccer match data using API-Football.

## Features

- Retrieve soccer matches for today
- Retrieve matches for a specific date
- Process external API data into a clean response format
- Validate responses using Pydantic models
- Make asynchronous HTTP requests using HTTPX
- Securely manage the API key using environment variables

## Tech Stack

- Python
- FastAPI
- Pydantic
- HTTPX
- Uvicorn
- API-Football

## API Endpoints

### Get Today's Matches

```text
GET /matches/today
```

### Get Matches by Date

```text
GET /matches/date/{match_date}
```

Example:

```text
GET /matches/date/2026-09-15
```

## Running the Project Locally

Install the dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file and add your API-Football API key:

```text
API_FOOTBALL_KEY=your_api_key_here
```

Start the FastAPI server:

```bash
python -m uvicorn app.main:app --reload
```

Then open the FastAPI documentation at:

```text
http://127.0.0.1:8000/docs
```

## Planned Improvements

- Team and league endpoints
- PostgreSQL database
- SQLAlchemy ORM
- Automated testing with pytest
- Docker containerization
- Redis caching
- AWS deployment