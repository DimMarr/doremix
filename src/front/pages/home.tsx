import { initSearchBar, SearchBar } from "@components/generics";
import { buildCardsFromPlaylists, initCardsElements } from "@components/generics/card";
import { setupPlaylistAndTrackModals } from "@components/playlists";
import { PlaylistRepository } from "@repositories/index";
import { Visibility } from "@models/playlist";
import { authService } from "@utils/authentication";

export async function HomePage(container) {
  container.innerHTML = "";

  // Fetch all playlists to separate them
  const allPlaylists = await new PlaylistRepository().getAll();

  const userInfos = await authService.iduser();
  const currentUserId = userInfos.id;
  const isAdmin = userInfos.role === "ADMIN";
  const personalPlaylists = allPlaylists.filter(p => p.idOwner === currentUserId);
  const publicPlaylists = allPlaylists.filter(p => p.visibility === Visibility.public && p.idOwner !== currentUserId);
  const openPlaylists = allPlaylists.filter(p => p.visibility === Visibility.open);

  const personalCards = buildCardsFromPlaylists(personalPlaylists);
  const publicCards = buildCardsFromPlaylists(publicPlaylists);
  const openCards = buildCardsFromPlaylists(openPlaylists);

  const pageHtml = (
    <div class="px-4 py-6 md:px-8 space-y-12">
      {/* Search section */}
      <div id="searchSection" class="w-full max-w-2xl mx-auto mb-10"></div>

      {/* Personal Playlists Section */}
      <section>
        <div class="flex items-center justify-between mb-6">
          <div>
            <h2 class="text-3xl font-bold tracking-tight text-white/90">My Playlists</h2>
            <p class="text-white/60 mt-1 text-sm">Your personal collection</p>
          </div>
          <div class="flex items-center gap-3">
            {isAdmin && (
              <a href="/admin" data-link class="px-4 py-2 rounded-lg bg-neutral-700 text-white text-sm font-medium hover:bg-neutral-600 transition-colors">
                Manage
              </a>
            )}
            <div id="addPlaylistSection"></div>
          </div>
        </div>

        {personalPlaylists.length > 0 ? (
          <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-8 gap-6">
            {personalCards as 'safe'}
          </div>
        ) : (
          <div class="bg-white/5 rounded-lg p-8 text-center border border-white/10">
            <p class="text-white/60 mb-4">You haven't created any playlists yet.</p>
          </div>
        )}
      </section>

      {/* Public Playlists Section */}
      <section>
        <div class="mb-6">
          <h2 class="text-3xl font-bold tracking-tight text-white/90">Public Playlists</h2>
          <p class="text-white/60 mt-1 text-sm">Discover what others are listening to</p>
        </div>

        {publicPlaylists.length > 0 ? (
          <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-8 gap-6">
            {publicCards as 'safe'}
          </div>
        ) : (
          <p class="text-white/60">No public playlists available at the moment.</p>
        )}
      </section>

      {/* Official/Open Playlists Section */}
      {openPlaylists.length > 0 && (
        <section>
          <div class="mb-6">
            <h2 class="text-3xl font-bold tracking-tight text-white/90">Official Playlists</h2>
            <p class="text-white/60 mt-1 text-sm">Curated by Doremix</p>
          </div>
          <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-8 gap-6">
            {openCards as 'safe'}
          </div>
        </section>
      )}

      <div id="modal-container"></div>
    </div>
  );

  container.innerHTML = pageHtml;


  // Setup modals d'ajout de track et de playlist.
  setupPlaylistAndTrackModals();

  // Setup composant de recherche.
  const searchSection = document.getElementById("searchSection");
  if (searchSection) {
    searchSection.innerHTML = SearchBar({
      placeholder: "Search tracks, artists, or playlists...",
      className: "w-full bg-white/10 border-none h-12 rounded-full shadow-lg backdrop-blur-sm focus-within:ring-2 focus-within:ring-primary",
      inputClassName: "text-white placeholder:text-white/50"
    });

    initSearchBar();
  }

  // Initialize card interactions
  initCardsElements(container, [...personalPlaylists, ...publicPlaylists, ...openPlaylists]);

  // Specific handler for empty state button if present
  const createFirstBtn = document.getElementById('create-first-playlist-btn');
  if (createFirstBtn) {
    createFirstBtn.addEventListener('click', () => {
      // Trigger the add playlist modal
      // This might need adjustment depending on how AddPlaylistModal is implemented
      // identifying the button that usually opens it:
      const addPlaylistBtn = document.querySelector('[data-action="create-playlist"]');
      if (addPlaylistBtn instanceof HTMLElement) {
        addPlaylistBtn.click();
      } else {
        // Fallback or todo: verify how to trigger modal programmatically if needed
        console.log("Create playlist clicked");
      }
    });
  }
}
