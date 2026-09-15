Boardly — a single-user mini kanban board (New / To Do / In Progress / Done).

Documents

- `_docs/specs.md` - the spec: user stories, acceptance criteria, non-goals

Commands

_(to be filled in as the frontend and backend are built)_

Rules

- `_docs/specs.md` is the source of truth for scope. Anything not in it is
  out of scope until the user asks for it explicitly.
- Backend calls from the frontend are centralized in one module so the mock
  can be swapped for the real backend without touching the rest of the UI.
- Keep the backend database-agnostic (SQLAlchemy) even though SQLite is the
  only database used here.
- Write tests before implementing backend endpoints.
- Commit regularly.
