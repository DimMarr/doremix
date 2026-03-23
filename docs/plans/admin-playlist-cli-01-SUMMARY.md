---
phase: admin-playlist-cli
plan: 01
subsystem: cli/services
tags: [cli, admin, playlist, service-layer, exceptions]
dependency_graph:
  requires: []
  provides:
    - src/cli/src/services/admin_playlist.py (6 admin playlist service functions)
    - PlaylistError and PlaylistNotFoundError in exception hierarchy
  affects:
    - src/cli/src/utils/exceptions.py
tech_stack:
  added: []
  patterns:
    - error-mapping pattern (_map_playlist_error) matching existing _map_genre_error convention
    - make_authenticated_request for cookie-based auth with automatic token refresh
key_files:
  created:
    - src/cli/src/services/admin_playlist.py
  modified:
    - src/cli/src/utils/exceptions.py
decisions:
  - "PlaylistError inherits from Exception (not AuthError) matching GenreError convention"
  - "remove_track returns PlaylistSchema (updated playlist), add_track returns TrackSchema (new track) — mirrors backend response shapes"
  - "No TrackNotFoundError added — not needed for this phase"
metrics:
  duration: "~5 minutes"
  completed_date: "2026-03-23"
  tasks_completed: 2
  files_modified: 2
---

# Phase admin-playlist-cli Plan 01: Admin Playlist Service Layer Summary

**One-liner:** Admin playlist service with 6 functions mapped to /admin/playlists/ endpoints using PlaylistNotFoundError for 404 responses.

## Tasks Completed

| Task | Name | Commit | Files |
| ---- | ---- | ------ | ----- |
| 1 | Add PlaylistNotFoundError to exception hierarchy | 67c0cd5 | src/cli/src/utils/exceptions.py |
| 2 | Create admin_playlist service module | 17ff2b0 | src/cli/src/services/admin_playlist.py |

## What Was Built

### Task 1: Exception Hierarchy Extension
Appended `PlaylistError` (base) and `PlaylistNotFoundError` (specific) to `src/cli/src/utils/exceptions.py`, following the same pattern as `GenreError`/`GenreNotFoundError`. Neither existing class was modified.

### Task 2: Admin Playlist Service Module
Created `src/cli/src/services/admin_playlist.py` with:

- `_detail(response)` — helper to extract error detail from JSON or text response
- `_map_playlist_error(response, context)` — maps HTTP status codes to typed exceptions: 404→PlaylistNotFoundError, 403→ForbiddenError, 401→NotAuthenticatedError, else→ApiRequestError
- `get_all_playlists()` → `list[PlaylistSchema]` — GET /admin/playlists/
- `get_playlist_tracks(playlist_id)` → `list[TrackSchema]` — GET /admin/playlists/{id}/tracks
- `update_playlist(playlist_id, name, id_genre, visibility)` → `PlaylistSchema` — PATCH /admin/playlists/{id}
- `delete_playlist(playlist_id)` → `dict` — DELETE /admin/playlists/{id}
- `add_track(playlist_id, title, url)` → `TrackSchema` — POST /admin/playlists/{id}/tracks/by-url
- `remove_track(playlist_id, track_id)` → `PlaylistSchema` — DELETE /admin/playlists/{id}/track/{track_id}

## Decisions Made

- `PlaylistError` inherits from `Exception` (not `AuthError`) to mirror the `GenreError` convention — playlist errors are domain errors, not auth errors.
- `remove_track` returns `PlaylistSchema` because the backend returns the updated playlist (not a simple acknowledgment).
- `add_track` returns `TrackSchema` because the backend returns the newly created track object.
- No `TrackNotFoundError` added — plan explicitly excludes it for this phase.

## Deviations from Plan

None — plan executed exactly as written.

## Verification Results

All acceptance criteria passed:
- `grep -n "admin/playlists"` returns exactly 6 lines (one per function)
- `grep -n "PlaylistNotFoundError"` returns 2 lines (import + raise)
- All 6 function definitions present
- `remove_track` signature is `(playlist_id, track_id)` as required
- No bare `/playlists/` path without `admin` prefix
- Full import verification: `All imports OK`

## Self-Check: PASSED

- `/home/ghadi/do/do3/doremix/src/cli/src/utils/exceptions.py` — modified, contains PlaylistError and PlaylistNotFoundError
- `/home/ghadi/do/do3/doremix/src/cli/src/services/admin_playlist.py` — created, 106 lines, all 6 functions exported
- Commit 67c0cd5 — feat(cli): add PlaylistNotFoundError to exception hierarchy
- Commit 17ff2b0 — feat(cli): add admin_playlist service layer
