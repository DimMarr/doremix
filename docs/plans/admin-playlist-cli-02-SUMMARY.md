---
phase: admin-playlist-cli
plan: "02"
subsystem: cli
tags:
  - cli
  - admin
  - typer
  - playlist
  - genre
dependency_graph:
  requires:
    - admin-playlist-cli-01
  provides:
    - admin_app typer entrypoint with playlist and genre sub-groups
  affects:
    - src/cli/src/commands/admin.py
tech_stack:
  added: []
  patterns:
    - Typer sub-typer hierarchy (admin_app -> playlist_app, genre_app)
    - _require_admin() guard on every command
    - Rich Table output for list/tracks commands
key_files:
  created:
    - src/cli/src/commands/admin.py
  modified: []
decisions:
  - Used aliased imports (genre_get_all, genre_create, genre_update, genre_delete) to avoid name collisions with playlist functions
  - Migrated genre commands verbatim from commands/genre.py rather than re-exporting to keep logic consistent
metrics:
  duration: "~5 minutes"
  completed: "2026-03-23"
  tasks_completed: 1
  files_created: 1
  files_modified: 0
---

# Phase admin-playlist-cli Plan 02: Admin Command Layer Summary

**One-liner:** Admin Typer app with playlist (6 cmds) and genre (4 cmds) sub-groups using aliased service imports and _require_admin() guard.

## What Was Built

Created `src/cli/src/commands/admin.py` — the command-layer entry point for all admin CLI operations.

**Structure:**
- `admin_app` — top-level Typer app
  - `playlist_app` sub-typer (name="playlist") — 6 commands
  - `genre_app` sub-typer (name="genre") — 4 commands

**Playlist commands (6):**
| Command | Description |
|---|---|
| `list` | Print table of all playlists (id, name, visibility, owner) |
| `tracks <id>` | Print tracks in a playlist (id, title) |
| `update <id>` | Update name/genre/visibility; prints detail table |
| `delete <id>` | Confirm then delete; --force skips confirmation |
| `add-track <id>` | Add track by URL/title; prints updated tracks table |
| `remove-track <id> <track_id>` | Remove track; prints updated tracks table |

**Genre commands (4, migrated from commands/genre.py):**
| Command | Description |
|---|---|
| `list` | List all genres |
| `add` | Create new genre |
| `update <id>` | Update genre label |
| `delete <id>` | Delete genre with confirmation |

## Decisions Made

1. **Aliased imports:** Genre service functions imported as `genre_get_all`, `genre_create`, `genre_update`, `genre_delete` to avoid name collision with admin_playlist service functions (`get_all_playlists`, etc.).

2. **Genre commands migrated verbatim:** Logic copied exactly from `commands/genre.py` without modification — only the `@app.command(...)` decorators changed to `@genre_app.command(...)`.

3. **`remove_track` return value:** The service returns `PlaylistSchema` but a second `get_playlist_tracks()` call is made to fetch the track list for display, per plan specification.

## Deviations from Plan

None — plan executed exactly as written.

## Verification Results

```
playlist commands: ['list', 'tracks', 'update', 'delete', 'add-track', 'remove-track']
genre commands: ['list', 'add', 'update', 'delete']
All checks passed
```

All acceptance criteria met:
- `admin_app = typer.Typer` — 1 match
- `playlist_app = typer.Typer` + `genre_app = typer.Typer` — 2 matches
- `@playlist_app.command` — 6 matches
- `@genre_app.command` — 4 matches
- `def _require_admin` — 1 match
- `/playlists/` in command file — 0 matches (HTTP in service layer only)

## Commit

- `5894c5c`: feat(cli): add admin command layer with playlist and genre sub-groups

## Self-Check: PASSED

- `/home/ghadi/do/do3/doremix/src/cli/src/commands/admin.py` — FOUND
- Commit `5894c5c` — FOUND
