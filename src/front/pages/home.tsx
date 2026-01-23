import { initSearchBar, SearchBar } from "@components/generics";
import { buildCardsFromPlaylists, Card, initCardsElements } from "@components/generics/card";
import { setupPlaylistAndTrackModals } from "@components/playlists";
import PlaylistRepository from "@repositories/playlistRepository";

export async function HomePage(container) {
  container.innerHTML = "";

  const playlists = await PlaylistRepository.getPublic();

  const playlistCards = buildCardsFromPlaylists(playlists);

  const pageHtml = (
    <div>
      {/* Search section */}
      <div id="searchSection" class="mb-8"></div>

      {
        Card({
          children: (
            <div>
              { /* Header */ }
              <div class="flex items-center justify-between mb-4">
                <h2 class="text-lg font-semibold leading-none tracking-tight">Top Playlists</h2>
                <div id="addPlaylistSection"></div>
              </div>

              { /* Playlist Cards */ }
              <div class="flex p-0! gap-10 mt-4 mb-2 overflow-auto">
                {playlistCards as 'safe'}
              </div>
            </div>
          )
        })
      }
      <div id="modal-container"></div>
    </div>
  );

  container.innerHTML = pageHtml;


  // Setup moadles d'ajout de track et de playlist.
  setupPlaylistAndTrackModals();

  // Setup composant de recherche.
  const searchSection = document.getElementById("searchSection");
  if (searchSection) {
    searchSection.innerHTML = SearchBar({
      placeholder: "Search tracks and playlists..."
    });

    initSearchBar();
  }
  initCardsElements(container, playlists);
}
