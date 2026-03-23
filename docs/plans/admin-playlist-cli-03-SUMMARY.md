---
phase: admin-playlist-cli
plan: "03"
subsystem: cli
tags: [cli, admin, playlist, testing, wiring]
dependency_graph:
  requires:
    - admin-playlist-cli-01
    - admin-playlist-cli-02
  provides:
    - admin commands reachable from CLI entry point
    - test coverage for all 6 admin_playlist service functions
  affects:
    - src/cli/src/main.py
    - src/cli/README.md
    - src/cli/tests_cli/test_admin_playlist.py
tech_stack:
  added: []
  patterns:
    - "typer add_typer for sub-app registration"
    - "unittest.mock patch for service layer tests"
key_files:
  modified:
    - src/cli/src/main.py
    - src/cli/README.md
  created:
    - src/cli/tests_cli/test_admin_playlist.py
decisions:
  - "admin_app registered as 'admin' namespace, replacing genre_app at root level"
  - "README command tree updated with full admin subtree (6 playlist + 4 genre commands)"
metrics:
  duration: "~10 minutes"
  completed_date: "2026-03-23"
  tasks_completed: 2
  tasks_total: 2
  files_modified: 2
  files_created: 1
---

# Phase admin-playlist-cli Plan 03: Wire Admin CLI and Tests Summary

## One-liner

Wired admin_app into CLI entry point as 'admin' namespace, updated README command tree with full admin subtree, and created 23 unit tests covering all 6 admin_playlist service functions.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Wire admin_app into main.py and remove genre root registration | 2163313 | src/cli/src/main.py |
| 2 | Update README.md command tree and write admin playlist tests | bed5a45 | src/cli/README.md, src/cli/tests_cli/test_admin_playlist.py |

## What Was Done

### Task 1: Wire admin_app
- Replaced `from src.commands.genre import app as genre_app` with `from src.commands.admin import admin_app`
- Replaced `root_app.add_typer(genre_app, name="genre", ...)` with `root_app.add_typer(admin_app, name="admin", ...)`
- Module imports cleanly; `doremix admin --help` now shows playlist and genre sub-groups

### Task 2: README and Tests
- Updated README `## Commandes` section: added full `|- admin` subtree with playlist (list, tracks, update, delete, add-track, remove-track) and genre (list, add, update, delete) subcommands
- Updated README Notes: removed owner-only bullet, added admin role requirement note
- Created `tests_cli/test_admin_playlist.py` with 23 tests covering:
  - `get_all_playlists`: success, empty, 401, 403
  - `get_playlist_tracks`: success, empty, 404, 401
  - `update_playlist`: success, 404, 401
  - `delete_playlist`: success-200, success-204, 404, 401
  - `add_track`: success, 404, 401, 403
  - `remove_track`: success, 404, 401, 403

## Verification Results

- `main.py`: 0 `genre_app` references, 2 `admin_app` references, imports cleanly
- README: admin subtree with all 10 commands present, no top-level genre, admin role note added
- Tests: 42 passed (23 new + 19 existing genre tests), 0 failures

## Deviations from Plan

None — plan executed exactly as written.

## Self-Check: PASSED

- src/cli/src/main.py exists and contains `admin_app`
- src/cli/README.md exists and contains `|- admin`
- src/cli/tests_cli/test_admin_playlist.py exists with 23 test functions
- Commits 2163313 and bed5a45 verified in git log
