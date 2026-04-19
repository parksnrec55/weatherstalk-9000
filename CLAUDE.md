# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

weatherstalk-9000 is a weather station app for rural Georgia. It has a Python FastAPI backend that serves both the REST API and the frontend HTML page.

## Running the Backend

```bash
cd backend
source .venv/bin/activate
uvicorn main:app --reload
```

The server starts at `http://localhost:8000`. The venv is at `backend/.venv` (Python 3.12).

## Architecture

**Single-process, no build step.** FastAPI serves the frontend and the API from the same process:

- `GET /` → serves `backend/src/index.html` directly via `FileResponse`
- `POST /weatherdata/` → create a weather reading
- `GET /weatherdata/` → list readings (paginated, max 100)
- `GET /weatherdata/{id}` → single reading
- `DELETE /weatherdata/{id}` → delete a reading

**Data model** (`WeatherData` in `backend/main.py`): `id`, `location`, `time` (string), `temp` (float), `humidity` (float). Stored in `backend/database.db` (SQLite, created on startup).

**Frontend** (`backend/src/index.html`): A single self-contained HTML file with inline CSS and JS. It currently displays hardcoded placeholder values. The JS comments at the bottom of the file show where to wire up live data from the API. The `frontend/` directory at the repo root is empty — the active HTML lives under `backend/src/`.

## Dependencies

Managed via the `.venv` in `backend/`. Key packages: `fastapi`, `sqlmodel`, `uvicorn`. Install with:

```bash
cd backend && python -m venv .venv && source .venv/bin/activate && pip install fastapi sqlmodel uvicorn
```
