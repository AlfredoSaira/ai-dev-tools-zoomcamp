Boardly — a single-user mini kanban board (New / To Do / In Progress / Done).

Documents

- `_docs/specs.md` - the spec: user stories, acceptance criteria, non-goals

Commands

- `cd frontend && npm run dev` - frontend dev server (http://localhost:5173)
- `cd frontend && npm run build` - production build
- `cd frontend && npm run lint` - oxlint
- `cd backend && uv sync` - install backend dependencies
- `cd backend && uv run fastapi dev src/boardly_backend/main.py` - backend dev server (http://localhost:8000, docs at /docs)
- `cd backend && uv run pytest` - backend tests
- `cd backend && uv run ruff check . && uv run ruff format --check .` - lint and format check, run before committing

Rules

- `_docs/specs.md` is the source of truth for scope. Anything not in it is
  out of scope until the user asks for it explicitly.
- Backend calls from the frontend are centralized in one module so the mock
  can be swapped for the real backend without touching the rest of the UI.
- Keep the backend database-agnostic (SQLAlchemy) even though SQLite is the
  only database used here.
- Write tests before implementing backend endpoints.
- Commit regularly.
