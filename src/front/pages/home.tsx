import { initSearchBar, SearchBar } from "@components/generics";
import { buildCardsFromPlaylists, initCardsElements } from "@components/generics/card";
import { setupPlaylistAndTrackModals } from "@components/playlists";
import { PlaylistRepository } from "@repositories/index";
import { GenreRepository } from "@repositories/index";
import Playlist, { Visibility } from "@models/playlist";
import { Genre } from "@models/genre";
import { authService } from "@utils/authentication";

interface CurrentUserInfo {
  id: number;
  role: "USER" | "MODERATOR" | "ADMIN";
}

export async function HomePage(container: HTMLElement | null) {
  if (!container) return;

  container.innerHTML = "";

  const repo = new PlaylistRepository();
  const genreRepo = new GenreRepository();

  const [allPlaylists, genres] = await Promise.all([
    repo.getAll(),
    genreRepo.getAll().catch(() => [] as Genre[]),
  ]);

  const userInfos = await authService.infos() as CurrentUserInfo;
  const currentUserId = userInfos.id;
  const canManage = userInfos.role === "ADMIN" || userInfos.role === "MODERATOR";

  // Playlist système "Titres likés" — isolée et affichée séparément
  const likedPlaylist = allPlaylists.find(
    (p: Playlist) => (p as any).isLikedPlaylist === true && p.idOwner === currentUserId
  ) ?? null;

  // Playlists personnelles normales (hors "Titres likés" et hors OPEN)
  const personalPlaylists = allPlaylists.filter(
    (playlist: Playlist) =>
      playlist.idOwner === currentUserId &&
      playlist.visibility !== Visibility.open &&
      !(playlist as any).isLikedPlaylist
  );

  const publicPlaylists = await repo.getPublic();
  const sharedPlaylists = await repo.getShared();
  const openPlaylists = allPlaylists.filter(
    (playlist: Playlist) => playlist.visibility === Visibility.open
  );

  const personalCards = buildCardsFromPlaylists(personalPlaylists);
  const sharedCards = buildCardsFromPlaylists(sharedPlaylists);
  const publicCards = buildCardsFromPlaylists(publicPlaylists);
  const openCards = buildCardsFromPlaylists(openPlaylists);
  const personalCardsSafe = personalCards as unknown as "safe";
  const publicCardsSafe = publicCards as unknown as "safe";
  const openCardsSafe = openCards as unknown as "safe";

  const pageHtml = (
    <div class="px-4 py-6 md:px-8 space-y-12">
      {/* Search section */}
      <div id="searchSection" class="w-full max-w-2xl mx-auto mb-2"></div>

      {/* Genre filter chips */}
      <div id="genreFilterSection" class="w-full max-w-2xl mx-auto"></div>

      {/* Personal Playlists Section */}
      <section data-playlist-section="personal">
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
            <div id="addPlaylistSection"></div>
          </div>
        </div>

        {/* Entrée spéciale "Titres likés" — visible uniquement si elle existe */}
        {likedPlaylist && (
          <div class="mb-6">
            <a
              href={`/playlist/${likedPlaylist.idPlaylist}`}
              data-link
              class="group flex items-center gap-4 w-fit rounded-xl p-3 hover:bg-white/5 transition-colors"
            >
              <div class="w-14 h-14 rounded-lg bg-gradient-to-br from-primary/60 to-primary flex items-center justify-center shadow-md flex-shrink-0">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="28"
                  height="28"
                  viewBox="0 0 24 24"
                  fill="currentColor"
                  stroke="currentColor"
                  stroke-width="1.5"
                  class="text-black"
                >
                  <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
                </svg>
              </div>
              <p class="font-bold text-white group-hover:underline">Titres likés</p>
            </a>
          </div>
        )}

        {personalPlaylists.length > 0 ? (
          <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-8 gap-6" data-cards-grid="personal">
            {personalCardsSafe}
          </div>
        ) : (
          <div class="bg-white/5 rounded-lg p-8 text-center border border-white/10" data-empty-state="personal">
            <p class="text-white/60 mb-4">You haven&apos;t created any playlists yet.</p>
          </div>
        )}
      </section>

      {/* Shared Playlists Section */}
      {sharedPlaylists.length > 0 ? (
        <section data-playlist-section="shared">
          <div class="flex items-center justify-between mb-6">
            <div>
              <h2 class="text-3xl font-bold tracking-tight text-white/90">Shared Playlists</h2>
              <p class="text-white/60 mt-1 text-sm">Discover what people want you to hear.</p>
            </div>
            <div id="addPlaylistSection"></div>
          </div>
          <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-8 gap-6" data-cards-grid="shared">
            {sharedCards as 'safe'}
          </div>
        </section>
      ) : ""}

      {/* Public Playlists Section */}
      <section data-playlist-section="public">
        <div class="mb-6">
          <h2 class="text-3xl font-bold tracking-tight text-white/90">Public Playlists</h2>
          <p class="text-white/60 mt-1 text-sm">Discover what others are listening to</p>
        </div>

        {publicPlaylists.length > 0 ? (
          <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-8 gap-6" data-cards-grid="public">
            {publicCardsSafe}
          </div>
        ) : (
          <p class="text-white/60">No public playlists available at the moment.</p>
        )}
      </section>

      {/* Official/Open Playlists Section */}
      {openPlaylists.length > 0 && (
        <section data-playlist-section="open">
          <div class="mb-6">
            <h2 class="text-3xl font-bold tracking-tight text-white/90">Official Playlists</h2>
            <p class="text-white/60 mt-1 text-sm">Curated by Doremix</p>
          </div>
          <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-8 gap-6" data-cards-grid="open">
            {openCardsSafe}
          </div>
        </section>
      )}

      <div id="modal-container"></div>
    </div>
  );

  container.innerHTML = await pageHtml;

  setupPlaylistAndTrackModals();

  const searchSection = container.querySelector("#searchSection") as HTMLElement | null;
  if (searchSection) {
    searchSection.innerHTML = await SearchBar({
      placeholder: "Search tracks, artists, or playlists...",
      className: "w-full bg-white/10 border-none h-12 rounded-full shadow-lg backdrop-blur-sm focus-within:ring-2 focus-within:ring-primary",
      inputClassName: "text-white placeholder:text-white/50"
    });

    initSearchBar();
  }

  const genreFilterSection = container.querySelector("#genreFilterSection") as HTMLElement | null;
  if (genreFilterSection && genres.length > 0) {
    const activeGenreIds = new Set<number>();

    const renderChips = () => {
      const chipsHtml = [
        `<button
          class="genre-chip px-4 py-1.5 rounded-full text-sm font-medium transition-all duration-200 border ${
            activeGenreIds.size === 0
              ? "bg-primary text-black border-primary shadow-md shadow-primary/30"
              : "bg-white/5 text-white/70 border-white/10 hover:bg-white/10 hover:text-white"
          }"
          data-genre-chip="all"
        >All</button>`,
        ...genres.map((g: Genre) =>
          `<button
            class="genre-chip px-4 py-1.5 rounded-full text-sm font-medium transition-all duration-200 border ${
              activeGenreIds.has(g.idGenre)
                ? "bg-primary text-black border-primary shadow-md shadow-primary/30"
                : "bg-white/5 text-white/70 border-white/10 hover:bg-white/10 hover:text-white"
            }"
            data-genre-chip="${g.idGenre}"
          >${g.label}</button>`
        )
      ].join("");

      genreFilterSection.innerHTML = `<div class="flex flex-wrap gap-2 justify-center">${chipsHtml}</div>`;
    };

    const applyFilter = () => {
      const allCards = container.querySelectorAll("[data-playlist-card]");

      allCards.forEach((card) => {
        const cardGenreId = (card as HTMLElement).getAttribute("data-genre-id");
        const numericGenreId = cardGenreId ? parseInt(cardGenreId, 10) : null;

        const matches = activeGenreIds.size === 0 || (numericGenreId !== null && activeGenreIds.has(numericGenreId));
        (card as HTMLElement).style.display = matches ? "" : "none";
      });

      const sections = container.querySelectorAll("[data-playlist-section]");
      sections.forEach((section) => {
        const visibleCards = section.querySelectorAll("[data-playlist-card]");
        const anyVisible = Array.from(visibleCards).some(
          (c) => (c as HTMLElement).style.display !== "none"
        );
        (section as HTMLElement).style.display = anyVisible || activeGenreIds.size === 0 ? "" : "none";
      });
    };

    renderChips();

    genreFilterSection.addEventListener("click", (e) => {
      const chip = (e.target as HTMLElement).closest("[data-genre-chip]") as HTMLElement | null;
      if (!chip) return;

      const val = chip.getAttribute("data-genre-chip");
      if (val === "all") {
        activeGenreIds.clear();
      } else {
        const id = parseInt(val!, 10);
        if (activeGenreIds.has(id)) {
          activeGenreIds.delete(id);
        } else {
          activeGenreIds.add(id);
        }
      }

      renderChips();
      applyFilter();
    });
  }

  initCardsElements(container, [...personalPlaylists, ...publicPlaylists, ...openPlaylists]);

  const createFirstBtn = container.querySelector('#create-first-playlist-btn') as HTMLElement | null;
  if (createFirstBtn) {
    createFirstBtn.addEventListener('click', () => {
      const addPlaylistBtn = document.querySelector('[data-action="create-playlist"]');
      if (addPlaylistBtn instanceof HTMLElement) {
        addPlaylistBtn.click();
      }
    });
  }
}
