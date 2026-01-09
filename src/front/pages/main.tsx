import PlaylistRepository from "@repositories/playlistRepository";
import { PlaylistDetailPage } from "@pages/playlist";
import { createMainLayout } from "@layouts/mainLayout";
import { Router } from "../router";
import { Card } from "@components/generics/index";
import { createSearchInput, createSearchResults } from "@components/generics/index";
import SearchRepository from "@repositories/searchRepository";

async function HomePage(container, trackPlayer) {
  container.innerHTML = "";

  const repo = new PlaylistRepository();
  const playlists = await repo.getPlaylists();
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
    let searchResultsElement: HTMLElement | null = null;

    const searchInput = createSearchInput({
      placeholder: "Search tracks and playlists...",
      onSearch: async (query: string) => {
        if (searchResultsElement) {
          searchResultsElement.remove();
          searchResultsElement = null;
        }

        if (!query) return;

        const results = await searchRepo.search(query);
        searchResultsElement = createSearchResults({
          tracks: results.tracks,
          playlists: results.playlists,
          onTrackClick: (track) => {
            trackPlayer.playSingleTrack(track);
            if (searchResultsElement) {
              searchResultsElement.remove();
              searchResultsElement = null;
            }
          },
          onPlaylistClick: (playlist) => {
            trackPlayer.setPlaylist(playlist);
            trackPlayer.playTrack(0);
            if (searchResultsElement) {
              searchResultsElement.remove();
              searchResultsElement = null;
            }
          },
        });

        searchInput.appendChild(searchResultsElement);
      },
    });

    searchSection.appendChild(searchInput);
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

export default async function init() {
  const { mainContent, trackPlayer } = await createMainLayout();
  const router = new Router(mainContent, trackPlayer);

  router.register("/", (container, params, player) => {
    HomePage(container, player);
  });

  router.register("/playlist/:id", async (container, params, player) => {
    const repo = new PlaylistRepository();
    const playlistId = parseInt(params.id, 10);
    const playlist = await repo.getPlaylistById(playlistId);
    if (playlist) {
      PlaylistDetailPage(container, playlist, player, () =>
        router.navigate("/"),
      );
    } else {
      container.innerHTML = "Playlist not found";
    }
  });

  router.onRouteChange();
}

init();
