# Playlist Sorting Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Allow users to sort their personal playlists by date, name, or custom drag-and-drop order, with the chosen preference persisted in the database.

**Architecture:** A new `user_playlist_preferences` table stores `sort_mode` (enum) and `custom_order` (JSONB array of idPlaylist integers) per user. Two new FastAPI endpoints (`GET/PUT /playlists/preferences`) handle reading and writing. Sorting is applied client-side in `home.tsx` using the fetched preference; drag-and-drop uses the HTML5 Drag and Drop API. When a playlist is deleted, its ID is naturally filtered out from `custom_order` at read time.

**Tech Stack:** Python 3.12 / FastAPI / SQLAlchemy 2 async / PostgreSQL / TypeScript / KitaJS (TSX) / HTML5 Drag and Drop API

---

## File Map

**Backend — new files:**
- `src/back/models/user_playlist_preferences.py` — SQLAlchemy model for the preferences table
- `src/back/schemas/user_playlist_preferences.py` — Pydantic schemas (GET response + PUT request)
- `src/back/repositories/user_playlist_preferences_repository.py` — DB access (get, upsert)
- `src/back/tests_back/test_playlist_preferences.py` — pytest tests for the endpoints

**Backend — modified files:**
- `src/back/models/__init__.py` — import `UserPlaylistPreferences`
- `src/back/schemas/__init__.py` — import `PlaylistPreferencesSchema`, `PlaylistPreferencesUpdate`
- `src/back/routes/playlists.py` — add `GET /playlists/preferences` and `PUT /playlists/preferences`
- `src/back/tests_back/conftest.py` — add `user_playlist_preferences_router` to the test app

**Frontend — new files:**
- `src/front/repositories/playlistPreferencesRepository.ts` — fetch + save preferences

**Frontend — modified files:**
- `src/front/repositories/index.ts` — export `PlaylistPreferencesRepository`
- `src/front/pages/home.tsx` — add sort controls, apply sorting, wire drag-and-drop

---

## Task 1: Backend model — `user_playlist_preferences`

**Files:**
- Create: `src/back/models/user_playlist_preferences.py`
- Modify: `src/back/models/__init__.py`

- [ ] **Step 1: Write the model**

```python
# src/back/models/user_playlist_preferences.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from database import Base


class UserPlaylistPreferences(Base):
    __tablename__ = "user_playlist_preferences"

    idUser = Column("iduser", Integer, primary_key=True, nullable=False)
    sort_mode = Column(
        "sort_mode", String(20), nullable=False, default="date_desc"
    )
    # Ordered list of idPlaylist integers. NULL when sort_mode != 'custom'.
    custom_order = Column("custom_order", JSONB, nullable=True)
```

Valid `sort_mode` values: `"date_desc"`, `"name_asc"`, `"custom"`.

- [ ] **Step 2: Register in `__init__.py`**

In `src/back/models/__init__.py`, add the import and `__all__` entry:

```python
from .user_playlist_preferences import UserPlaylistPreferences
```

Add `"UserPlaylistPreferences"` to `__all__`.

- [ ] **Step 3: Commit**

```bash
git add src/back/models/user_playlist_preferences.py src/back/models/__init__.py
git commit -m "feat: add UserPlaylistPreferences SQLAlchemy model"
```

---

## Task 2: Backend schemas

**Files:**
- Create: `src/back/schemas/user_playlist_preferences.py`
- Modify: `src/back/schemas/__init__.py`

- [ ] **Step 1: Write the schemas**

```python
# src/back/schemas/user_playlist_preferences.py
from pydantic import BaseModel, field_validator
from typing import Optional, List

VALID_SORT_MODES = {"date_desc", "name_asc", "custom"}


class PlaylistPreferencesSchema(BaseModel):
    sort_mode: str
    custom_order: Optional[List[int]] = None


class PlaylistPreferencesUpdate(BaseModel):
    sort_mode: str
    custom_order: Optional[List[int]] = None

    @field_validator("sort_mode")
    @classmethod
    def validate_sort_mode(cls, v: str) -> str:
        if v not in VALID_SORT_MODES:
            raise ValueError(f"sort_mode must be one of {VALID_SORT_MODES}")
        return v
```

- [ ] **Step 2: Export from `schemas/__init__.py`**

Add to `src/back/schemas/__init__.py`:

```python
from .user_playlist_preferences import (
    PlaylistPreferencesSchema,
    PlaylistPreferencesUpdate,
)
```

- [ ] **Step 3: Commit**

```bash
git add src/back/schemas/user_playlist_preferences.py src/back/schemas/__init__.py
git commit -m "feat: add playlist preferences Pydantic schemas"
```

---

## Task 3: Backend repository

**Files:**
- Create: `src/back/repositories/user_playlist_preferences_repository.py`
- Modify: `src/back/repositories/__init__.py`

- [ ] **Step 1: Write the repository**

```python
# src/back/repositories/user_playlist_preferences_repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.user_playlist_preferences import UserPlaylistPreferences
from typing import Optional, List


class UserPlaylistPreferencesRepository:
    @staticmethod
    async def get(db: AsyncSession, user_id: int) -> UserPlaylistPreferences | None:
        result = await db.execute(
            select(UserPlaylistPreferences).filter(
                UserPlaylistPreferences.idUser == user_id
            )
        )
        return result.scalars().first()

    @staticmethod
    async def upsert(
        db: AsyncSession,
        user_id: int,
        sort_mode: str,
        custom_order: Optional[List[int]],
    ) -> UserPlaylistPreferences:
        result = await db.execute(
            select(UserPlaylistPreferences).filter(
                UserPlaylistPreferences.idUser == user_id
            )
        )
        prefs = result.scalars().first()
        if prefs is None:
            prefs = UserPlaylistPreferences(idUser=user_id)
            db.add(prefs)
        prefs.sort_mode = sort_mode
        prefs.custom_order = custom_order
        await db.commit()
        await db.refresh(prefs)
        return prefs
```

- [ ] **Step 2: Export from `repositories/__init__.py`**

Add to `src/back/repositories/__init__.py`:

```python
from .user_playlist_preferences_repository import UserPlaylistPreferencesRepository
```

Add `"UserPlaylistPreferencesRepository"` to `__all__`.

- [ ] **Step 3: Commit**

```bash
git add src/back/repositories/user_playlist_preferences_repository.py src/back/repositories/__init__.py
git commit -m "feat: add UserPlaylistPreferencesRepository"
```

---

## Task 4: Backend endpoints

**Files:**
- Modify: `src/back/routes/playlists.py`

- [ ] **Step 1: Write the failing tests first** (see Task 5 — write tests before implementing)

Skip ahead to Task 5, then return here.

- [ ] **Step 2: Add imports to `routes/playlists.py`**

At the top of `src/back/routes/playlists.py`, add these imports alongside the existing ones:

```python
from repositories import UserPlaylistPreferencesRepository
from schemas import PlaylistPreferencesSchema, PlaylistPreferencesUpdate
```

- [ ] **Step 3: Add GET endpoint**

Append to `src/back/routes/playlists.py`:

```python
@router.get(
    "/preferences",
    response_model=PlaylistPreferencesSchema,
    summary="Get playlist sort preferences for the current user",
)
async def get_playlist_preferences(
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    prefs = await UserPlaylistPreferencesRepository.get(db, user_id)
    if prefs is None:
        return PlaylistPreferencesSchema(sort_mode="date_desc", custom_order=None)
    return PlaylistPreferencesSchema(
        sort_mode=prefs.sort_mode, custom_order=prefs.custom_order
    )
```

**Important:** This route must be registered **before** `/{playlist_id}` in the file, or FastAPI will try to match `"preferences"` as a playlist ID. In `playlists.py` the `/{playlist_id}` routes come after the prefix-less routes, so appending at the end is fine — but double-check the route order after insertion.

- [ ] **Step 4: Add PUT endpoint**

Append to `src/back/routes/playlists.py`:

```python
@router.put(
    "/preferences",
    response_model=PlaylistPreferencesSchema,
    summary="Save playlist sort preferences for the current user",
)
async def update_playlist_preferences(
    body: PlaylistPreferencesUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    prefs = await UserPlaylistPreferencesRepository.upsert(
        db, user_id, body.sort_mode, body.custom_order
    )
    return PlaylistPreferencesSchema(
        sort_mode=prefs.sort_mode, custom_order=prefs.custom_order
    )
```

- [ ] **Step 5: Commit**

```bash
git add src/back/routes/playlists.py
git commit -m "feat: add GET/PUT /playlists/preferences endpoints"
```

---

## Task 5: Backend tests

**Files:**
- Create: `src/back/tests_back/test_playlist_preferences.py`
- Modify: `src/back/tests_back/conftest.py`

- [ ] **Step 1: Register the preferences route in the test app**

In `src/back/tests_back/conftest.py`, add the import and `include_router` call:

```python
from routes.playlists import router as playlists_router
# (already present — no duplicate needed; the preferences endpoints are on the same router)
```

The preferences endpoints share the `playlists_router` already registered in the test `app`, so no change is needed to `conftest.py` — just ensure the test file can import `UserPlaylistPreferences`.

Add this import to conftest (for the `user_playlist_preferences` fixture used in tests):

```python
from models.user_playlist_preferences import UserPlaylistPreferences
```

- [ ] **Step 2: Write the test file**

```python
# src/back/tests_back/test_playlist_preferences.py
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from models.user_playlist_preferences import UserPlaylistPreferences


class TestGetPlaylistPreferences:
    @pytest.mark.asyncio
    async def test_get_preferences_default_when_none_exist(self, client):
        """Returns date_desc defaults when no row exists for the user."""
        response = await client.get("/playlists/preferences")
        assert response.status_code == 200
        data = response.json()
        assert data["sort_mode"] == "date_desc"
        assert data["custom_order"] is None

    @pytest.mark.asyncio
    async def test_get_preferences_returns_saved_row(self, client, db: AsyncSession, sample_user):
        """Returns the stored sort_mode when a row already exists."""
        prefs = UserPlaylistPreferences(
            idUser=sample_user.idUser,
            sort_mode="name_asc",
            custom_order=None,
        )
        db.add(prefs)
        await db.commit()

        response = await client.get("/playlists/preferences")
        assert response.status_code == 200
        data = response.json()
        assert data["sort_mode"] == "name_asc"

    @pytest.mark.asyncio
    async def test_get_preferences_returns_custom_order(self, client, db: AsyncSession, sample_user):
        """Returns the custom_order array when sort_mode is custom."""
        prefs = UserPlaylistPreferences(
            idUser=sample_user.idUser,
            sort_mode="custom",
            custom_order=[3, 1, 2],
        )
        db.add(prefs)
        await db.commit()

        response = await client.get("/playlists/preferences")
        assert response.status_code == 200
        data = response.json()
        assert data["sort_mode"] == "custom"
        assert data["custom_order"] == [3, 1, 2]


class TestUpdatePlaylistPreferences:
    @pytest.mark.asyncio
    async def test_put_creates_row_on_first_save(self, client, db: AsyncSession, sample_user):
        """Creates a new preferences row when none exists."""
        response = await client.put(
            "/playlists/preferences",
            json={"sort_mode": "name_asc", "custom_order": None},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["sort_mode"] == "name_asc"

        # Verify in DB
        from sqlalchemy.future import select
        result = await db.execute(
            select(UserPlaylistPreferences).filter(
                UserPlaylistPreferences.idUser == sample_user.idUser
            )
        )
        row = result.scalars().first()
        assert row is not None
        assert row.sort_mode == "name_asc"

    @pytest.mark.asyncio
    async def test_put_updates_existing_row(self, client, db: AsyncSession, sample_user):
        """Overwrites an existing preferences row."""
        prefs = UserPlaylistPreferences(
            idUser=sample_user.idUser, sort_mode="date_desc", custom_order=None
        )
        db.add(prefs)
        await db.commit()

        response = await client.put(
            "/playlists/preferences",
            json={"sort_mode": "custom", "custom_order": [5, 3, 1]},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["sort_mode"] == "custom"
        assert data["custom_order"] == [5, 3, 1]

    @pytest.mark.asyncio
    async def test_put_rejects_invalid_sort_mode(self, client):
        """Returns 422 for an unrecognised sort_mode value."""
        response = await client.put(
            "/playlists/preferences",
            json={"sort_mode": "bogus", "custom_order": None},
        )
        assert response.status_code == 422
```

- [ ] **Step 3: Run the tests to verify they fail before implementation**

```bash
cd src/back && python -m pytest tests_back/test_playlist_preferences.py -v
```

Expected: some tests fail because the `UserPlaylistPreferences` table doesn't exist yet in SQLite test DB (model not imported by Base yet) or the endpoints aren't wired. Fix order: Task 1–4 must be done first, then come back here.

- [ ] **Step 4: Run tests again after Tasks 1–4 are complete**

```bash
cd src/back && python -m pytest tests_back/test_playlist_preferences.py -v
```

Expected: all 6 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/back/tests_back/test_playlist_preferences.py
git commit -m "test: add tests for playlist preferences endpoints"
```

---

## Task 6: Frontend repository — `PlaylistPreferencesRepository`

**Files:**
- Create: `src/front/repositories/playlistPreferencesRepository.ts`
- Modify: `src/front/repositories/index.ts`

- [ ] **Step 1: Check the index file**

Read `src/front/repositories/index.ts` to find the current exports pattern, then add the new export there.

- [ ] **Step 2: Write the repository**

```typescript
// src/front/repositories/playlistPreferencesRepository.ts
import { API_BASE_URL } from "@config/index";
import { handleHttpError } from "@utils/errorHandling";

export type SortMode = "date_desc" | "name_asc" | "custom";

export interface PlaylistPreferences {
  sort_mode: SortMode;
  custom_order: number[] | null;
}

export class PlaylistPreferencesRepository {
  async get(): Promise<PlaylistPreferences> {
    const response = await fetch(`${API_BASE_URL}/playlists/preferences`, {
      credentials: "include",
    });
    if (!response.ok) {
      handleHttpError(response, "Get playlist preferences");
      throw new Error("Failed to fetch playlist preferences");
    }
    return response.json();
  }

  async save(prefs: PlaylistPreferences): Promise<PlaylistPreferences> {
    const response = await fetch(`${API_BASE_URL}/playlists/preferences`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify(prefs),
    });
    if (!response.ok) {
      handleHttpError(response, "Save playlist preferences");
      throw new Error("Failed to save playlist preferences");
    }
    return response.json();
  }
}
```

- [ ] **Step 3: Export from `repositories/index.ts`**

Open `src/front/repositories/index.ts` and add:

```typescript
export { PlaylistPreferencesRepository } from "./playlistPreferencesRepository";
export type { PlaylistPreferences, SortMode } from "./playlistPreferencesRepository";
```

- [ ] **Step 4: Commit**

```bash
git add src/front/repositories/playlistPreferencesRepository.ts src/front/repositories/index.ts
git commit -m "feat: add PlaylistPreferencesRepository"
```

---

## Task 7: Frontend — sort controls and logic in `home.tsx`

**Files:**
- Modify: `src/front/pages/home.tsx`

This task adds:
1. A sort control row (3 buttons: Date, Name, Custom) in the "My Playlists" section header.
2. A `sortPersonalPlaylists()` function that applies the active sort to the DOM grid.
3. Loading preferences on page init and applying the saved sort.
4. Saving on sort button click.

- [ ] **Step 1: Add import for `PlaylistPreferencesRepository` and types**

At the top of `src/front/pages/home.tsx`, add:

```typescript
import { PlaylistPreferencesRepository, type SortMode } from "@repositories/index";
```

- [ ] **Step 2: Fetch preferences alongside other data**

Replace the current parallel fetch block:

```typescript
const [allPlaylists, genres] = await Promise.all([
  repo.getAll(),
  genreRepo.getAll().catch(() => [] as Genre[]),
]);
```

With:

```typescript
const prefsRepo = new PlaylistPreferencesRepository();

const [allPlaylists, genres, savedPrefs] = await Promise.all([
  repo.getAll(),
  genreRepo.getAll().catch(() => [] as Genre[]),
  prefsRepo.get().catch(() => ({ sort_mode: "date_desc" as SortMode, custom_order: null })),
]);
```

- [ ] **Step 3: Add the sort control row to the "My Playlists" section header**

In the JSX, inside `<section data-playlist-section="personal">`, replace the existing header div:

```tsx
<div class="flex items-center justify-between mb-6">
  <div>
    <h2 class="text-3xl font-bold tracking-tight text-white/90">My Playlists</h2>
    <p class="text-white/60 mt-1 text-sm">Your personal collection</p>
  </div>
  <div class="flex items-center gap-3">
    {canManage && (
      <a href="/admin" data-link class="px-4 py-2 rounded-lg bg-neutral-700 text-white text-sm font-medium hover:bg-neutral-600 transition-colors">
        Manage
      </a>
    )}
    <div class="flex items-center gap-1 bg-white/5 border border-white/10 rounded-lg p-1" id="sortControls">
      <button
        data-sort-btn="date_desc"
        class="px-3 py-1.5 rounded-md text-xs font-medium transition-colors text-white/60 hover:text-white hover:bg-white/10"
      >Date</button>
      <button
        data-sort-btn="name_asc"
        class="px-3 py-1.5 rounded-md text-xs font-medium transition-colors text-white/60 hover:text-white hover:bg-white/10"
      >Name</button>
      <button
        data-sort-btn="custom"
        class="px-3 py-1.5 rounded-md text-xs font-medium transition-colors text-white/60 hover:text-white hover:bg-white/10"
      >Custom</button>
    </div>
    <div id="addPlaylistSection"></div>
  </div>
</div>
```

- [ ] **Step 4: Add `draggable="true"` attribute to each personal playlist card**

After `container.innerHTML = await pageHtml;`, query all cards in the personal grid and mark them draggable:

```typescript
const personalGrid = container.querySelector('[data-cards-grid="personal"]') as HTMLElement | null;
if (personalGrid) {
  personalGrid.querySelectorAll("[data-playlist-card]").forEach((card) => {
    (card as HTMLElement).setAttribute("draggable", "true");
  });
}
```

- [ ] **Step 5: Add sort + drag-and-drop logic after `container.innerHTML = await pageHtml;`**

Add the following block after `container.innerHTML = await pageHtml;`:

```typescript
// --- Playlist sorting ---
let activeSortMode: SortMode = savedPrefs.sort_mode;
let customOrder: number[] = savedPrefs.custom_order ?? personalPlaylists.map((p) => p.idPlaylist!);

const getSortedPersonalPlaylists = (): number[] => {
  const ids = personalPlaylists.map((p) => p.idPlaylist!);
  if (activeSortMode === "name_asc") {
    return [...personalPlaylists]
      .sort((a, b) => (a.name ?? "").localeCompare(b.name ?? ""))
      .map((p) => p.idPlaylist!);
  }
  if (activeSortMode === "date_desc") {
    return [...personalPlaylists]
      .sort((a, b) => {
        const da = new Date(b.createdAt ?? 0).getTime();
        const db2 = new Date(a.createdAt ?? 0).getTime();
        return da - db2;
      })
      .map((p) => p.idPlaylist!);
  }
  // custom: use customOrder, filtering out IDs no longer in personalPlaylists
  const validIds = new Set(ids);
  const filtered = customOrder.filter((id) => validIds.has(id));
  // append any new playlists not yet in custom order (newest first)
  const inOrder = new Set(filtered);
  const newIds = [...personalPlaylists]
    .filter((p) => !inOrder.has(p.idPlaylist!))
    .sort((a, b) => new Date(b.createdAt ?? 0).getTime() - new Date(a.createdAt ?? 0).getTime())
    .map((p) => p.idPlaylist!);
  return [...filtered, ...newIds];
};

const applySort = () => {
  if (!personalGrid) return;
  const orderedIds = getSortedPersonalPlaylists();
  orderedIds.forEach((id) => {
    const card = personalGrid.querySelector(`[data-playlist-id="${id}"]`) as HTMLElement | null;
    if (card) personalGrid.appendChild(card);
  });
};

const highlightActiveSort = () => {
  container.querySelectorAll("[data-sort-btn]").forEach((btn) => {
    const mode = (btn as HTMLElement).getAttribute("data-sort-btn") as SortMode;
    if (mode === activeSortMode) {
      (btn as HTMLElement).className =
        "px-3 py-1.5 rounded-md text-xs font-medium transition-colors bg-primary text-black";
    } else {
      (btn as HTMLElement).className =
        "px-3 py-1.5 rounded-md text-xs font-medium transition-colors text-white/60 hover:text-white hover:bg-white/10";
    }
  });
};

// Apply saved sort on load
applySort();
highlightActiveSort();

// Sort button click handler
const sortControls = container.querySelector("#sortControls");
if (sortControls) {
  sortControls.addEventListener("click", async (e) => {
    const btn = (e.target as HTMLElement).closest("[data-sort-btn]") as HTMLElement | null;
    if (!btn) return;
    const mode = btn.getAttribute("data-sort-btn") as SortMode;
    activeSortMode = mode;
    if (mode !== "custom") {
      customOrder = getSortedPersonalPlaylists();
    }
    applySort();
    highlightActiveSort();
    await prefsRepo.save({ sort_mode: activeSortMode, custom_order: activeSortMode === "custom" ? customOrder : null });
  });
}

// Drag-and-drop for custom sort
if (personalGrid) {
  personalGrid.setAttribute("draggable", "false");
  let draggedId: number | null = null;

  personalGrid.addEventListener("dragstart", (e) => {
    const card = (e.target as HTMLElement).closest("[data-playlist-id]") as HTMLElement | null;
    if (!card) return;
    draggedId = parseInt(card.getAttribute("data-playlist-id")!, 10);
    card.classList.add("opacity-50");
  });

  personalGrid.addEventListener("dragend", (e) => {
    const card = (e.target as HTMLElement).closest("[data-playlist-id]") as HTMLElement | null;
    if (card) card.classList.remove("opacity-50");
    draggedId = null;
  });

  personalGrid.addEventListener("dragover", (e) => {
    e.preventDefault();
    const target = (e.target as HTMLElement).closest("[data-playlist-id]") as HTMLElement | null;
    if (!target || draggedId === null) return;
    const targetId = parseInt(target.getAttribute("data-playlist-id")!, 10);
    if (targetId === draggedId) return;
    // Reorder in DOM
    const draggedEl = personalGrid.querySelector(`[data-playlist-id="${draggedId}"]`) as HTMLElement | null;
    if (!draggedEl) return;
    const rect = target.getBoundingClientRect();
    const midX = rect.left + rect.width / 2;
    if (e.clientX < midX) {
      personalGrid.insertBefore(draggedEl, target);
    } else {
      personalGrid.insertBefore(draggedEl, target.nextSibling);
    }
  });

  personalGrid.addEventListener("drop", async (e) => {
    e.preventDefault();
    if (draggedId === null) return;
    // Read new order from DOM
    const newOrder = Array.from(
      personalGrid.querySelectorAll("[data-playlist-id]")
    ).map((el) => parseInt((el as HTMLElement).getAttribute("data-playlist-id")!, 10));
    customOrder = newOrder;
    activeSortMode = "custom";
    highlightActiveSort();
    await prefsRepo.save({ sort_mode: "custom", custom_order: customOrder });
  });
}
```

**Note:** The drag-and-drop listeners switch `activeSortMode` to `"custom"` automatically when the user reorders cards — even if they were previously in date/name mode. This matches the expected UX.

- [ ] **Step 6: Confirm `data-playlist-id` is present on cards (already verified)**

`buildCardsFromPlaylists` in `src/front/components/generics/card.tsx:166` already sets `"data-playlist-id": String(p.idPlaylist)` on every card. No changes needed here.

- [ ] **Step 7: Commit**

```bash
git add src/front/pages/home.tsx src/front/repositories/playlistPreferencesRepository.ts src/front/repositories/index.ts
git commit -m "feat: add playlist sorting controls and drag-and-drop to home page"
```

---

## Task 8: End-to-end smoke test

- [ ] **Step 1: Start the app and verify the preferences endpoint**

```bash
# From the back directory
curl -b <your-auth-cookie> http://localhost:5000/playlists/preferences
```

Expected response:
```json
{"sort_mode": "date_desc", "custom_order": null}
```

- [ ] **Step 2: Save a preference**

```bash
curl -b <your-auth-cookie> -X PUT http://localhost:5000/playlists/preferences \
  -H "Content-Type: application/json" \
  -d '{"sort_mode": "name_asc", "custom_order": null}'
```

Expected: `{"sort_mode": "name_asc", "custom_order": null}`

- [ ] **Step 3: Reload the home page**

Open the browser, navigate to home. The "Name" sort button should be highlighted. Personal playlists should be sorted A→Z.

- [ ] **Step 4: Drag a card to a new position**

Drag one playlist card to a different slot. The sort buttons should automatically switch to "Custom" highlighted. Reload the page — verify the custom order is preserved.

- [ ] **Step 5: Commit (if any final fixes were needed)**

```bash
git add -p
git commit -m "fix: resolve any issues found during smoke test"
```

---

## Task 9: Run the full backend test suite

- [ ] **Step 1: Run all tests**

```bash
cd src/back && python -m pytest tests_back/ -v
```

Expected: all tests pass (including the existing ones — no regressions).

- [ ] **Step 2: If any existing test fails, diagnose and fix**

The most likely failure is if `Base.metadata.create_all` in the test conftest doesn't pick up `UserPlaylistPreferences`. Verify `models/__init__.py` imports the new model (Task 1, Step 2). SQLAlchemy needs the model class to be imported before `create_all` is called.

- [ ] **Step 3: Final commit**

```bash
git add .
git commit -m "feat: playlist sorting complete — date, name, drag-and-drop with persisted preferences"
```
