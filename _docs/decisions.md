# Decisions

Calls made while grooming the backlog (issues #2–#26). Recorded here so
issues stop re-litigating them. Where this file and `_docs/outdated/`
disagree, this file wins.

## 1. The user model is `accounts.User`, not `django.contrib.auth.models.User`

`_docs/outdated/architecture.md`'s data model lists the user as plain
`django.contrib.auth.models.User` with a "display name" — that model has no
such field. Issue #4 instead creates `accounts.User`, subclassing
`AbstractUser` and adding `display_name`, with `AUTH_USER_MODEL` pointing at
it from the first migration.

Why: swapping the user model after other apps' tables carry a foreign key to
it means a data migration on live data. Doing it in the first task costs one
line.

Supersedes: `_docs/outdated/architecture.md`, "Identidad y membresía".

## 2. Creating a project makes the creator a FACILITATOR membership

Issue #5 doesn't just create a `Project` — it also creates a `Membership`
for the owner with role `FACILITATOR`.

Why: the plan assumes the project owner can act as facilitator by default.
Without this, the very first thing an owner does (open a feedback cycle)
would be blocked by issue #6/#7's facilitator-only checks.

## 3. Whisper without diarization means lower-confidence owner extraction — accepted, not deferred

Issue #21 uses plain `whisper-1` (no speaker labels), a deliberate deviation
from the course's reference model (which uses a diarization-capable model).
Issue #23's owner-matching by fuzzy name will produce more `NULL` owners as
a direct consequence.

Why: simplicity over precision for the MVP. This is not a bug to fix in
either issue — the facilitator's manual owner dropdown (issue #24) is the
accepted mitigation, not a workaround pending a "real" fix.

## 4. Claude, not OpenAI, for clustering and extraction — no course-pinned version exists for it

Issues #22 and #23 use the `anthropic` SDK (latest, 1.0) instead of OpenAI,
per an earlier explicit decision to deviate from the course reference (which
uses OpenAI end-to-end). Because `retroloop` never uses `anthropic`, there is
no course-verified version to pin against — 1.0 was simply the latest
available at the time this was decided.

## 5. Manually created decisions/actions skip draft review

Issue #17's manual create/edit forms default new rows to `source=MANUAL`
and `status`/`review_status=CONFIRMED` directly — no draft step.

Why: the draft-review requirement in the plan ("AI-generated actions and
decisions remain drafts until the facilitator confirms them") is explicitly
about AI output, not human input. A person typing a decision by hand is
already the confirmation.

## 6. Issues carry `mvp` or `post-mvp`; grooming follow-ups default to `post-mvp`

Issues #1–26 are labeled `mvp`; #27 (security hardening) and #28 (demo data)
are `post-mvp` — deferred until after the MVP ships. Any new follow-up issue
filed while grooming a task is `post-mvp` by default unless it's clearly
required for the MVP to function. See `_docs/process.md` and
`_docs/team/pm.md`.

## 7. No new follow-up issues were needed while grooming #2–#26

Every "out of scope" item identified during this grooming pass already had
a home in an existing issue from the original 28-task backlog. Nothing was
split out into a brand-new issue.
