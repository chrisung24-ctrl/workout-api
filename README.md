# Workout Log API

A REST API for logging workout sets and viewing per-exercise stats. Built with FastAPI, SQLModel, and SQLite.

## Features
- Log sets with exercise name, reps, weight, and date
- Input validation (reps must be positive, weight can't be negative)
- Filter logs by exercise
- Stats endpoint: sets logged, max weight, and total volume

## Run locally
```
pip install -r requirements.txt
fastapi dev main.py
```
Then open http://127.0.0.1:8000/docs for the interactive API docs.

## Run tests
```
python -m pytest -v
```

## Endpoints
| Method | Path | Description |
|---|---|---|
| POST | /logs | Add a workout set |
| GET | /logs | List logs (optional `?exercise=`) |
| DELETE | /logs/{id} | Delete a log |
| GET | /stats/{exercise} | Max weight and total volume |