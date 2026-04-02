import { ArtistRepository } from "@repositories/artistRepository";
import { Button } from "@components/generics";
import { TrackListHeader } from "@components/tracks/header";
import { TrackRow } from "@components/tracks/row";
import { trackPlayerInstance } from "@layouts/mainLayout";
import { YoutubePlayerState } from "@store/trackPlayer";
import Playlist, { Visibility } from "@models/playlist";
import type { Track } from "@models/track";

interface PageParams {
  id: string;
}

export async function ArtistTracksPage(
  container: HTMLElement | null,
  onBack: () => void,
  params: PageParams
) {
  if (!container) return;

  const artistId = parseInt(params.id, 10);
  const repo = new ArtistRepository();
  let artist;
  let tracks: Track[] = [];

  try {
    artist = await repo.getById(artistId);
    tracks = await repo.getTracks(artistId);
  } catch (error) {
    console.error("Failed to load artist tracks", error);
    container.innerHTML = `<div class="p-8"><Button id="back-button" variant="ghost" size="sm">← Back</Button><p class="mt-4 text-red-500">Artist not found.</p></div>`;

    container.onclick = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      if (target.closest('#back-button')) {
        onBack();
      }
    };
    return;
  }

  const dummyPlaylist = new Playlist({
    idPlaylist: -artistId, // Use negative to avoid clashes with real playlists if needed
    name: artist.name,
    description: "Artist Discography",
    tracks: tracks,
    image: artist.imageUrl || `https://ui-avatars.com/api/?name=${encodeURIComponent(artist.name || 'Artist')}&background=random&size=200`,
    visibility: Visibility.public
  });


  const updateTrackListDisplay = async () => {
    const trackListContainer = container.querySelector('#track-list-container');
    if (trackListContainer) {
      const currentTrack = trackPlayerInstance.getCurrentTrack();
      const playerState = trackPlayerInstance.getPlayerState();

      trackListContainer.innerHTML = (
        <div>
          <TrackListHeader />
          {(await Promise.all(tracks.map(async (track, index) => ( await
              <TrackRow
                  track={track}
                  index={index}
                  playlistId={dummyPlaylist.idPlaylist}
                  current_track={[YoutubePlayerState.UNSTARTED, YoutubePlayerState.CUED].includes(playerState) ? undefined : currentTrack}
                  canEditPlaylist={false}
              />
          )))) as unknown as 'safe'}
        </div>
      ) as unknown as string;
    }
  };

  const handlePlayTrack = (index: number) => {
    if (trackPlayerInstance.playlist?.idPlaylist !== dummyPlaylist.idPlaylist) {
      trackPlayerInstance.setPlaylist({ ...dummyPlaylist, tracks });
    }
    trackPlayerInstance.playTrack(index);
  };

  container.innerHTML = (
    <div>
      <div class="mb-8">
        <Button id="back-button" variant="ghost" size="sm">← Back</Button>
      </div>

      <div class="flex items-start gap-8 my-8">
        <div class="flex flex-col items-center gap-4">
          <div class="w-48 h-48 rounded-full bg-neutral-800 flex items-center justify-center text-6xl shadow-2xl border border-white/10 overflow-hidden">
            {artist.imageUrl ? <img src={artist.imageUrl} alt={artist.name} class="w-full h-full object-cover" /> : artist.name.charAt(0).toUpperCase()}
          </div>
          <div class="flex items-center gap-2">
            <button id="play-all-button" class="p-2 rounded-md border border-white/10 hover:bg-white/10 transition-colors" title="Play">
              <svg class="w-5 h-5" xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 24 24">
                <path d="M8 5v14l11-7z" />
              </svg>
            </button>
            <button id="shuffle-button" class="p-2 rounded-md border border-white/10 hover:bg-white/10 transition-colors" title="Shuffle">
              <svg class="w-5 h-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M16 3h5v5M4 20L21 3M21 16v5h-5M15 15l6 6M4 4l5 5" />
              </svg>
            </button>
          </div>
        </div>
        <div id="artist-header-info" class="pt-2 flex flex-col items-start gap-2">
          <span class="px-3 py-1 rounded-full text-xs font-semibold bg-purple-500/10 text-purple-400 border border-purple-500/20 uppercase tracking-wider">
            Artist
          </span>
          <h1 safe class="font-bold text-5xl mt-2">{artist.name}</h1>
          <p safe class="text-muted-foreground text-lg">{tracks.length} tracks</p>
        </div>
      </div>

      <div class="mb-4 mt-2">
        <div class="relative">
          <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground pointer-events-none" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8" />
            <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-4.35-4.35" />
          </svg>
          <input
            id="track-search-input"
            type="text"
            placeholder="Rechercher un titre..."
            class="w-full pl-9 pr-4 py-2 rounded-lg bg-white/5 border border-white/10 text-sm text-white placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-blue-500/40 focus:border-blue-500/40 transition-all"
          />
        </div>
      </div>

      <div id="track-list-container" class="flex flex-col gap-4">
      </div>
    </div>
  ) as unknown as string;

  updateTrackListDisplay();

  // Search filter
  const searchInput = container.querySelector('#track-search-input') as HTMLInputElement | null;
  if (searchInput) {
    searchInput.addEventListener('input', () => {
      const query = searchInput.value.toLowerCase().trim();
      const trackListContainer = container.querySelector('#track-list-container');
      if (!trackListContainer) return;

      const rows = trackListContainer.querySelectorAll('[data-track-index]');
      rows.forEach((row) => {
        const htmlRow = row as HTMLElement;
        const text = htmlRow.textContent?.toLowerCase() ?? '';
        if (!query || text.includes(query)) {
          htmlRow.style.display = '';
        } else {
          htmlRow.style.display = 'none';
        }
      });
    });
  }

  // Event delegation
  container.onclick = (e: MouseEvent) => {
    const target = e.target as HTMLElement;

    if (target.closest('#back-button')) {
      onBack();
      return;
    }

    if (target.closest('#play-all-button')) {
      if (tracks.length === 0) return;
      trackPlayerInstance.setShuffle(false);
      handlePlayTrack(0);

      const playBtn = target.closest('#play-all-button');
      const shuffleBtn = container.querySelector('#shuffle-button');
      if (playBtn) playBtn.classList.add('text-blue-500');
      if (shuffleBtn) shuffleBtn.classList.remove('text-blue-500');
      return;
    }

    if (target.closest('#shuffle-button')) {
      if (tracks.length === 0) return;
      if (trackPlayerInstance.playlist?.idPlaylist !== dummyPlaylist.idPlaylist) {
        trackPlayerInstance.setPlaylist({ ...dummyPlaylist, tracks });
      }
      trackPlayerInstance.setShuffle(true);

      const shuffleBtn = target.closest('#shuffle-button');
      const playBtn = container.querySelector('#play-all-button');
      if (shuffleBtn) shuffleBtn.classList.add('text-blue-500');
      if (playBtn) playBtn.classList.remove('text-blue-500');
      return;
    }

    const row = target.closest('[data-track-index]') as HTMLElement | null;
    if (row) {
      const index = Number(row.getAttribute('data-track-index'));
      if (!Number.isNaN(index)) {
        handlePlayTrack(index);
      }
    }
  };
}
