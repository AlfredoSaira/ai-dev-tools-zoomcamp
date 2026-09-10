Django app for weekly Start/Stop/Continue cycles and the retrospectives that
follow.

Commands

- `docker compose up` - full dev environment (db, web, worker)
- `uv sync` - install dependencies
- `uv run manage.py runserver` - dev server without Docker
- `uv run pytest` - the whole suite
- `uv run pytest tests/test_homepage.py` - one test file
- `uv run ruff check . && uv run ruff format --check .` - lint and format check, run it before committing

Rules

- `_docs/tasks.md` is the build order and `_docs/architecture.md` is the design. Read the task and the part of the architecture it touches before building it - the constraints that matter are specific to each area and live there, not here.
- Postgres is the only infrastructure.
- Configuration comes from the environment. A new setting means a new env var and a line in `.env.example`, never a hardcoded value or a checked-in secret.
- Tests live in `tests/`. `config/settings_test.py` supplies their environment, so production settings stay strict.
- Dependencies are pinned exactly in `pyproject.toml`. Do not add one without asking.
- Commit regularly.
