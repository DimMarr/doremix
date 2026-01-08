import { createCard } from "../components/generics/index";
import {
  createSearchInput,
  createSearchResults,
} from "../components/generics/index";
import PlaylistRepository from "../repositories/playlistRepository";
import SearchRepository from "../repositories/searchRepository";
import { renderPlaylistPage } from "./playlist.js";
import { createMainLayout } from "../layouts/MainLayout.js";
import { Router } from "../router.js";

async function renderHomePage(container, trackPlayer, router) {
  container.innerHTML = "";

  // SEARCH SECTION
  const searchSection = document.createElement("div");
  searchSection.className = "mb-8";

  const searchRepo = new SearchRepository();
  let searchResultsContainer = null;
  let searchInputContainer; // ADDED

  const searchInput = createSearchInput({
    placeholder: "Search tracks and playlists...",
    onSearch: async (query) => {
      console.log("Searching for:", query);

      // Remove old results
      if (searchResultsContainer) {
        searchResultsContainer.remove();
        searchResultsContainer = null;
      }

      if (!query) return;

      // Search
      const results = await searchRepo.search(query);
      console.log("Results:", results);

      // Create results dropdown
      searchResultsContainer = createSearchResults({
        tracks: results.tracks,
        playlists: results.playlists,
        onTrackClick: (track) => {
          trackPlayer.playSingleTrack(track);

          // Close search results
          if (searchResultsContainer) {
            searchResultsContainer.remove();
            searchResultsContainer = null;
          }
        },
        onPlaylistClick: (playlist) => {
          router.navigate(`/playlist/${playlist.idPlaylist}`);

          // Close search results
          if (searchResultsContainer) {
            searchResultsContainer.remove();
            searchResultsContainer = null;
          }
        },
      });

      // CHANGED: append to searchInputContainer instead of searchSection
      searchInputContainer.appendChild(searchResultsContainer);
    },
  });

  searchInputContainer = searchInput; // ADDED

  // Close results when clicking outside
  document.addEventListener("click", (e) => {
    // CHANGED: check searchInputContainer instead of searchSection
    if (searchResultsContainer && !searchInputContainer.contains(e.target)) {
      searchResultsContainer.remove();
      searchResultsContainer = null;
    }
  });

  searchSection.appendChild(searchInput);
  container.appendChild(searchSection);

  // EXISTING TOP TRACKS SECTION
  const tracksCard = createCard({
    title: "Top Tracks",
  });

  const tracksContentCard = createCard({
    className: "flex p-0! gap-10 mt-4 mb-2 overflow-scroll",
  });

  const repo = new PlaylistRepository();
  const playlists = await repo.getPlaylists();
  const svg1 = new URL("../assets/icons/play.svg", import.meta.url).href;

  playlists.forEach((p) => {
    const card = createCard({
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

    const link = document.createElement("a");
    link.href = `/playlist/${p.idPlaylist}`;
    link.setAttribute("data-link", "");
    link.appendChild(card);

    tracksContentCard.appendChild(link);
  });

  tracksCard.appendChild(tracksContentCard);
  container.appendChild(tracksCard);
}

export default async function init() {
  const { mainContent, trackPlayer } = await createMainLayout();
  const router = new Router(mainContent, trackPlayer);

  router.register("/", (container, params, player) => {
    renderHomePage(container, player, router);
  });

  router.register("/playlist/:id", async (container, params, player) => {
    const repo = new PlaylistRepository();
    const playlistId = parseInt(params.id, 10);
    const playlist = await repo.getPlaylistById(playlistId);
    if (playlist) {
      renderPlaylistPage(container, playlist, player, () =>
        router.navigate("/"),
      );
    } else {
      container.innerHTML = "Playlist not found";
    }
  });

  router.onRouteChange();
}

init();
