# Playlist Cover Image Lazy Loading — Design Spec

**Date:** 2026-04-01  
**Branch:** feature/lazyloading-ordering-playlists  
**Status:** Approved

---

## Problem

Playlist cards currently resolve `coverImage` eagerly in the repository layer: if `coverImage` is null, a bundled fallback image (`playlist1.jpg`) is used. This means:

1. All cover images (real or fallback) are fetched immediately on page load, regardless of whether the card is in the viewport.
2. The card has no way to distinguish "no cover exists" from "has a real cover" — so it can never show a meaningful skeleton.
3. There is no loading state — the user sees either an image or nothing during fetch.

---

## Definition of Done

- Playlist list loads text metadata (name, vote, visibility) immediately on render
- Cover images are loaded lazily — only when the playlist card enters the viewport
- A skeleton (animated pulsing grey rectangle) is shown while the image is loading
- If a playlist has no `coverImage`, a static SVG placeholder is shown permanently
- The feature works correctly on both slow and fast network conditions

---

## Architecture

### Affected files

| File | Change |
|---|---|
| `src/front/repositories/playlistRepository.ts` | Remove `img1` fallback — pass `undefined` when `coverImage` is null |
| `src/front/components/generics/card.tsx` | Add skeleton div, change `src` → `data-src` on img, wire IntersectionObserver in `initCardsElements` |

No backend changes required. `PlaylistSchema.coverImage: Optional[str] = None` is already in place.

---

## Data Flow Change (Repository Layer)

In `playlistRepository.ts`, all five methods that map raw API data to `Playlist` objects (`getAll`, `getPublic`, `getShared`, `getById`, `adminGetAll`) currently do:

```ts
image: item.coverImage ? this.getCoverUrl(item.coverImage) : img1,
```

This becomes:

```ts
image: item.coverImage ? this.getCoverUrl(item.coverImage) : undefined,
```

The bundled `img1` import is removed entirely. The fallback is now the card's responsibility.

---

## Card Rendering (HTML Structure)

In `buildCardsFromPlaylists`, each card's image area changes based on whether `p.image` is defined:

**When `p.image` is defined (real cover exists):**
- Render a skeleton `<div>` (animated pulse, fills the same square as the image)
- Render `<img data-src={p.image}>` with **no `src`** attribute (prevents eager load)
- Add `data-has-cover="1"` on the card element so the observer knows to watch it

**When `p.image` is undefined (no cover):**
- Render the existing SVG placeholder permanently
- No skeleton, no observer

The existing `Card` component's `image != null` branch (line 77) already handles the no-image SVG fallback — this path is preserved unchanged.

---

## IntersectionObserver Wiring

Added inside `initCardsElements` in `card.tsx`, after the existing play button wiring.

```
For each card with data-has-cover="1":
  1. Find <img[data-src]> inside the card
  2. Create IntersectionObserver({ rootMargin: "50px" })
  3. On intersect:
       img.src = img.dataset.src
       observer.disconnect()
  4. img.addEventListener("load", () => hide skeleton)
  5. img.addEventListener("error", () => hide skeleton, show SVG placeholder)
```

**rootMargin: "50px"** — starts loading images 50px before they enter the viewport, avoiding a flash of skeleton on fast connections.

---

## Edge Cases

| Scenario | Behavior |
|---|---|
| Fast network / card already in viewport | Observer fires on first tick, image loads quickly, skeleton disappears |
| Slow network | Skeleton remains visible until `load` fires |
| No `coverImage` | Static SVG placeholder, no skeleton, no observer |
| Broken URL | `error` event: skeleton hidden, SVG placeholder shown |
| Cards hidden by genre filter | `display:none` cards don't intersect — observer fires correctly when they become visible again |

---

## What Is Not Changing

- Backend routes and `PlaylistSchema` — no changes needed
- `Playlist` model (`playlist.ts`) — `image?: string` field is already optional
- Play button wiring in `initCardsElements` — untouched
- `getShared` currently fetches tracks eagerly — out of scope for this feature
