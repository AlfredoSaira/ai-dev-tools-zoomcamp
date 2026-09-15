# Boardly — Product Spec

> Draft proposed by the coding assistant based on reasonable MVP defaults for
> Homework 2 (ai-dev-tools-zoomcamp). Review and adjust before this is
> treated as final — see open questions at the bottom.

## Summary

Boardly is a single-user mini kanban board: one board, a fixed set of
columns, and cards you can create, edit, move, and delete. Data persists
across sessions.

## Columns

1. **New** — unrefined items; may need grooming before they're ready to be
   picked up. Lives here until it's clear enough to move to To Do (possibly
   for a future sprint).
2. **To Do** — refined and ready to be worked on.
3. **In Progress** — currently being worked on.
4. **Done** — finished.

## User stories

1. As a user, I can create a card with a title and an optional description
   so I can track a piece of work.
2. As a user, I can see all cards grouped into columns (New / To Do /
   In Progress / Done) so I know the state of my work at a glance.
3. As a user, I can move a card from one column to another (drag-and-drop)
   so I can reflect progress.
4. As a user, I can edit a card's title/description so I can correct or
   refine it.
5. As a user, I can delete a card I no longer need.
6. As a user, I can refresh the page or come back later and still see all
   my cards in the column I last left them in.

## Acceptance criteria

- The board shows exactly four columns, in this fixed order: **New**,
  **To Do**, **In Progress**, **Done**.
- New cards are created in the **New** column by default.
- Creating a card requires a title (non-empty); description is optional.
- A card can be dragged from any column to any other column, in any order
  of columns (no enforced workflow direction).
- Editing and deleting a card is possible from the card itself (e.g. a
  small menu or icon on the card).
- All card data (title, description, column, position) is persisted in a
  database and survives a page refresh or server restart.
- The UI updates immediately when a card is created, moved, edited, or
  deleted (no manual refresh needed).

## Non-goals (out of scope for this homework)

- User accounts / authentication / login.
- Multiple boards — only one board exists.
- Custom columns (renaming, adding, or removing columns).
- Real-time collaboration between multiple browser tabs/users (each client
  reloads its own state; no WebSocket sync required).
- Card assignees, due dates, labels/tags, comments, or attachments.
- Card change history / audit log.

## Tech shape (per course constraints)

- `frontend/` — React + Vite, calls the backend through one centralized API
  module (mocked first, then real).
- `openapi.yaml` — contract between frontend and backend.
- `backend/` — FastAPI, managed with `uv`. Mock in-memory store first, then
  swapped for SQLAlchemy + SQLite (database-agnostic).
- Tests written before implementation for backend endpoints; frontend and
  backend tests both required before the database swap is considered done.

## Decisions confirmed by the user (2026-09-14)

- Name: **Boardly**.
- Single board, no auth, four fixed columns (New / To Do / In Progress /
  Done) — no custom columns, no multiple boards.
- Card fields: title + description only, no color tag.
