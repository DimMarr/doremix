import { Card, SearchBar, SearchResults } from "@components/generics";
import PlaylistRepository from "@repositories/playlistRepository";
import SearchRepository from "@repositories/searchRepository";

export async function HomePage(container, trackPlayer) {
  container.innerHTML = "";

  const repo = new PlaylistRepository();
  const playlists = await repo.getPlaylists();
  console.log(playlists);
  const svg1 = new URL("../assets/icons/play.svg", import.meta.url).href;

  const playlistCards = playlists.map((p) => {
    const cardHtml = Card({
      title: p.name || "",
      image: p.image,
      content: p.description || "",
      icon: svg1,
      className: "px-0! max-w-[200px] md:max-w-[300px] shrink-0",
      onClickPlay: () => {
        if (trackPlayer.playlist.idPlaylist !== p.idPlaylist) {
          trackPlayer.setPlaylist(p);
        }
        trackPlayer.playTrack(0);
      },
    });

    return `<a href="/playlist/${p.idPlaylist}" data-link>${cardHtml}</a>`;
  }).join('');

  const pageHtml = (
    <div>
      {/* Search section */}
      <div id="searchSection" class="mb-8"></div>

      {
        Card({
          children: (
            <div>
              <h2 class="text-lg font-semibold leading-none tracking-tight mb-4">Top Tracks</h2>
              <div class="flex p-0! gap-10 mt-4 mb-2 overflow-scroll">
                {playlistCards}
              </div>
            </div>
          )
        })
      }
    </div>
  );

  container.innerHTML = pageHtml;

  // Add search functionality
  const searchSection = document.getElementById("searchSection");
  if (searchSection) {
    const searchRepo = new SearchRepository();
    let currentResults: { tracks: any[], playlists: any[] } | null = null;
    let debounceTimer: ReturnType<typeof setTimeout>;

    // Render search input
    searchSection.innerHTML = SearchBar({
      placeholder: "Search tracks and playlists..."
    });

    // Attach event handler to search input
    const searchInputElement = document.getElementById("search-input") as HTMLInputElement;
    if (searchInputElement) {
      searchInputElement.addEventListener("input", async (e) => {
        const target = e.target as HTMLInputElement;
        const query = target.value.trim();

        clearTimeout(debounceTimer);

        // Remove existing results
        const existingResults = searchSection.querySelector('[class*="absolute top-full"]');
        if (existingResults) {
          existingResults.remove();
        }

        if (query.length < 2) {
          currentResults = null;
          return;
        }

        // Wait 300ms before searching
        debounceTimer = setTimeout(async () => {
          const results = await searchRepo.search(query);
          currentResults = results;

          // Render search results
          const resultsHtml = SearchResults({
            tracks: results.tracks,
            playlists: results.playlists,
          });

          // Insert results into DOM
          const searchContainer = searchSection.querySelector('[class*="relative w-full"]');
          if (searchContainer) {
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = resultsHtml;
            searchContainer.appendChild(tempDiv.firstElementChild!);


            const trackItems = searchContainer.querySelectorAll('[data-track-index]');
            trackItems.forEach((item) => {
              const index = parseInt((item as HTMLElement).dataset.trackIndex || '0', 10);
              item.addEventListener('click', () => {
                trackPlayer.playSingleTrack(currentResults!.tracks[index]);

                const resultsElement = searchSection.querySelector('[class*="absolute top-full"]');
                if (resultsElement) {
                  resultsElement.remove();
                }
                currentResults = null;
              });
            });


            const playlistItems = searchContainer.querySelectorAll('[data-playlist-index]');
            playlistItems.forEach((item) => {
              const index = parseInt((item as HTMLElement).dataset.playlistIndex || '0', 10);
              item.addEventListener('click', () => {
                trackPlayer.setPlaylist(currentResults!.playlists[index]);
                trackPlayer.playTrack(0);

                const resultsElement = searchSection.querySelector('[class*="absolute top-full"]');
                if (resultsElement) {
                  resultsElement.remove();
                }
                currentResults = null;
              });
            });
          }
        }, 300);
      });
    }
  }

  // Re-attach event handlers after DOM is updated
  const cardElements = container.querySelectorAll('[data-link]');
  cardElements.forEach((link, index) => {
    const p = playlists[index];
    const iconElement = link.querySelector('img[alt="Play icon"]');
    if (iconElement) {
      iconElement.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (trackPlayer.playlist.idPlaylist !== p.idPlaylist) {
          trackPlayer.setPlaylist(p);
        }
        trackPlayer.playTrack(0);
      });
    }
  });
}
