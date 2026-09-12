# syntax=docker/dockerfile:1

FROM python:3.14-slim

# Debian trixie only packages an older ffmpeg, so the 8.1 binaries come from
# the static build image instead, per architecture.md.
COPY --from=mwader/static-ffmpeg:8.1 /ffmpeg /ffprobe /usr/local/bin/
COPY --from=ghcr.io/astral-sh/uv:0.12.13 /uv /uvx /usr/local/bin/

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_FROZEN=1 \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    PATH=/opt/venv/bin:$PATH

WORKDIR /app

# Dependencies resolve from the committed lock file before application code
# is copied, so editing a .py file does not trigger a reinstall.
COPY pyproject.toml uv.lock ./
RUN UV_COMPILE_BYTECODE=1 uv sync --frozen --no-install-project

COPY . .

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
