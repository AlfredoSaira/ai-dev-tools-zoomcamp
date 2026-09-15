# Boardly

A mini kanban board — single user, one board, four fixed columns
(New / To Do / In Progress / Done). Built for Homework 2 of
[ai-dev-tools-zoomcamp](https://github.com/DataTalksClub/ai-dev-tools-zoomcamp).

See [`_docs/specs.md`](_docs/specs.md) for the full spec.

## Running locally

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Opens at http://localhost:5173. The backend is currently mocked in
`frontend/src/api.js` — no backend needs to be running yet.

### Backend

```bash
cd backend
uv sync
uv run fastapi dev src/boardly_backend/main.py
```

Opens at http://localhost:8000 (interactive docs at `/docs`). Contract is
defined in [`openapi.yaml`](openapi.yaml), backed by SQLite via SQLAlchemy
(`backend/boardly.db`, created automatically). The store is database-agnostic
— set `DATABASE_URL` (see `backend/.env.example`) to point at Postgres or
another engine instead, no code changes needed.

Run backend tests:

```bash
cd backend
uv run pytest
```

### Frontend ↔ backend

The frontend talks to the backend at `http://localhost:8000` (configurable
via `VITE_API_URL`, see `frontend/.env.example`). Run both dev servers to
use the app end to end.
