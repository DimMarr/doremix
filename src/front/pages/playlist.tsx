import { TrackRepository } from "@repositories/trackRepository";
import { Button, AddTrackModal } from "@components/index";
import { TrackListHeader } from "@components/tracks/header";
import { TrackRow } from "@components/tracks/row";
import { AlertManager } from "@utils/alertManager";
import { trackPlayerInstance } from "@layouts/mainLayout";
import { YoutubePlayerState } from "@store/trackPlayer";
import { PlaylistRepository } from "@repositories/index";
import Playlist, { Visibility } from "@models/playlist";
import type { Track } from "@models/track";

interface PageParams {
  id: string;
}



function getIconForVisibility(visibility: Visibility) {
  switch (visibility.toLowerCase()) {
    case Visibility.private:
      return (
        <svg class="w-3.5 h-3.5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
          <path d="M7 11V7a5 5 0 0110 0v4" />
        </svg>
      );
    case Visibility.public:
      return (
        <svg class="w-3.5 h-3.5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10" />
          <path d="M2 12h20" />
          <path d="M12 2a15.3 15.3 0 014 10 15.3 15.3 0 01-4 10 15.3 15.3 0 01-4-10 15.3 15.3 0 014-10z" />
        </svg>
      );
    default:
      return (
        <svg class="w-3.5 h-3.5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2" />
          <circle cx="9" cy="7" r="4" />
          <path d="M23 21v-2a4 4 0 00-3-3.87" />
          <path d="M16 3.13a4 4 0 010 7.75" />
        </svg>
      );
  }
}

function getVisibilityElement(visibility: Visibility) {
  const containerClass = "flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-semibold border uppercase tracking-wider cursor-pointer transition-all duration-200 relative group shadow-sm hover:shadow-md";

  let colorClass = "";
  switch (visibility.toLowerCase()) {
    case Visibility.private:
      colorClass = "bg-red-500/10 text-red-500 border-red-500/20 hover:bg-red-500/20";
      break;
    case Visibility.public:
      colorClass = "bg-green-500/10 text-green-500 border-green-500/20 hover:bg-green-500/20";
      break;
    case Visibility.open:
      colorClass = "bg-purple-500/10 text-purple-500 border-purple-500/20 hover:bg-purple-500/20";
      break;
    default:
      colorClass = "bg-blue-500/10 text-blue-500 border-blue-500/20 hover:bg-blue-500/20";
      break;
  }

  if (visibility === Visibility.open) {
    return (
      <div class={`${containerClass} ${colorClass} cursor-not-allowed opacity-80`}>
        <div class="flex items-center gap-2">
          {getIconForVisibility(visibility) as 'safe'}
          <span>{visibility}</span>
          <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
          </svg>
        </div>
      </div>
    )
  }

  return (
    <div class={`${containerClass} ${colorClass}`}>
      <select id="visibility-select" class="appearance-none bg-transparent border-none outline-none cursor-pointer absolute inset-0 w-full h-full opacity-0 z-10">
        <option value={visibility} selected class="hidden">{visibility}</option>
        {visibility === Visibility.public && <option value={Visibility.private} class="bg-gray-900 text-white">Private</option>}
        {visibility === Visibility.private && <option value={Visibility.public} class="bg-gray-900 text-white">Public</option>}
        {visibility === Visibility.shared && (
          <>
            <option value={Visibility.private} class="bg-gray-900 text-white">Private</option>
            <option value={Visibility.public} class="bg-gray-900 text-white">Public</option>
          </>
        )}
      </select>

      <div class="flex items-center gap-2 pointer-events-none">
        {getIconForVisibility(visibility) as 'safe'}
        <span>{visibility}</span>
        {/* Dropdown arrow */}
        <svg class="w-3 h-3 opacity-60 group-hover:opacity-100 transition-opacity" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
        </svg>
      </div>
    </div>
  );
}


function renderTrackList(playlist: Playlist): string {
  const tracks = playlist.tracks || [];
  const currentTrack = trackPlayerInstance.getCurrentTrack();
  const playerState = trackPlayerInstance.getPlayerState();

  return (
    <div>
      <TrackListHeader />
      {tracks.map((track, index) => (
        <TrackRow
          track={track}
          index={index}
          playlist={playlist}
          trackPlayer={trackPlayerInstance}
          current_track={[YoutubePlayerState.UNSTARTED, YoutubePlayerState.CUED].includes(playerState) ? null : currentTrack}
        />
      )) as 'safe'}
    </div>
  );
}

export async function PlaylistDetailPage(
  container: HTMLElement | null,
  onBack: () => void,
  params: PageParams
) {
  if (!container) return;

  const playlistId = parseInt(params.id, 10);
  const repo = new PlaylistRepository();
  let playlist = await repo.getById(playlistId);

  // Local state
  let tracks: Track[] = playlist.tracks || [];

  const updateHeader = () => {
    const headerContainer = container.querySelector('#playlist-header-info');
    if (headerContainer) {
      headerContainer.innerHTML = (
        <>
          {getVisibilityElement(playlist.visibility) as 'safe'}
          <h1 safe class="font-bold text-4xl mt-2">{playlist.name}</h1>
          <p safe class="text-muted-foreground text-lg">{playlist.description || ''}</p>
        </>
      );
      bindVisibilityChange();
    }
  }

  const bindVisibilityChange = () => {
    const select = container.querySelector('#visibility-select');
    if (select) {
      select.addEventListener('change', handleVisibilityChange);
    }
  }

  const handleVisibilityChange = async (e: Event) => {
    const target = e.target as HTMLSelectElement;
    const newVis = target.value as Visibility; // "public" or "private"

    // Optimistic update
    const oldVis = playlist.visibility;
    playlist.visibility = newVis;
    updateHeader();

    // Determine backend enum value (uppercase)
    const backendVis = newVis === Visibility.public ? "PUBLIC" : "PRIVATE";

    try {
      await repo.update(playlist.idPlaylist!, { visibility: backendVis as any });
      new AlertManager().success(`Playlist is now ${newVis}`);
    } catch (err) {
      console.error("Failed to update visibility", err);
      new AlertManager().error("Failed to update visibility");
      // Revert
      playlist.visibility = oldVis;
      updateHeader();
    }
  };

  const updateTrackListDisplay = () => {
    const trackListContainer = container.querySelector('#track-list-container');
    if (trackListContainer) {
      trackListContainer.innerHTML = renderTrackList({ ...playlist, tracks });
    }
  };

  const handleAddTrack = () => {
    const modalContainer = container.querySelector('#modal-container');
    if (!modalContainer) return;

    const { render } = AddTrackModal({
      playlistId: playlist.idPlaylist,
      onClose: () => {
        modalContainer.innerHTML = '';
      },
      onTrackAdded: (newTrack: Track) => {
        tracks = [...tracks, newTrack];
        trackPlayerInstance.setPlaylist({ ...playlist, tracks });
        updateTrackListDisplay();
        modalContainer.innerHTML = '';
      }
    });
    render(modalContainer);
  };

  const handleDeleteTrack = async (trackIndex: number) => {
    const track = tracks[trackIndex];
    if (!track) return;

    const wasPlaying = trackPlayerInstance.getCurrentTrack()?.idTrack === track.idTrack;

    // On supprime la playlist du track store.
    tracks = tracks.filter((_, i) => i !== trackIndex);
    playlist.tracks = tracks;
    trackPlayerInstance.setPlaylist({ ...playlist });

    // Si la track supprimée était en cours on la stoppe et on passe à la track suivante (s'il reste des tracks)
    if (wasPlaying) {
      trackPlayerInstance.stopVideo();
      if (tracks.length > 0) {
        trackPlayerInstance.nextTrack();
      }
    }

    updateTrackListDisplay();

    try {
      await new TrackRepository().delete(playlist.idPlaylist, track.idTrack);
    } catch (err) {
      console.error(err);
      new AlertManager().error("Failed to remove track");

      // S'il y a une erreur lors de la suppression du track, on revient en arrière en affichant la track qui n'a pas pu être supprimé.
      tracks.splice(trackIndex, 0, track);
      playlist.tracks = tracks;
      trackPlayerInstance.setPlaylist({ ...playlist });
      updateTrackListDisplay();
    }
  };

  const handlePlayTrack = (index: number) => {
    if (trackPlayerInstance.playlist?.idPlaylist !== playlist.idPlaylist) {
      trackPlayerInstance.setPlaylist({ ...playlist, tracks });
    }
    trackPlayerInstance.playTrack(index);
  };

  // Render page
  container.innerHTML = (
    <div>
      <div id="modal-container"></div>

      <div class="mb-8">
        <Button id="back-button" variant="ghost" size="sm">← Back</Button>
      </div>

      <div class="flex items-start gap-8 my-8">
        <div class="flex flex-col items-center gap-4">
          <img
            src={playlist.image}
            class="w-48 h-48 rounded-md object-cover shadow-2xl"
            alt={playlist.name}
          />
          <Button id="add-track-button" variant="outline" size="md">Add Track</Button>
        </div>
        <div id="playlist-header-info" class="pt-2 flex flex-col gap-2">
          {getVisibilityElement(playlist.visibility) as 'safe'}
          <h1 safe class="font-bold text-4xl mt-2">{playlist.name}</h1>
          <p safe class="text-muted-foreground text-lg">{playlist.description || ''}</p>
        </div>
      </div>

      <div id="track-list-container" class="flex flex-col gap-4">
        {renderTrackList({ ...playlist, tracks }) as 'safe'}
      </div>
    </div>
  );

  // Initialize functionality
  updateTrackListDisplay();
  bindVisibilityChange();

  // Event delegation
  container.onclick = (e: MouseEvent) => {
    const target = e.target as HTMLElement;

    if (target.closest('#back-button')) {
      onBack();
      return;
    }

    if (target.closest('#add-track-button')) {
      handleAddTrack();
      return;
    }

    const deleteButton = target.closest('.delete-track') as HTMLElement | null;
    if (deleteButton) {
      e.stopPropagation();
      const trackIndex = Number(deleteButton.getAttribute('data-track-index'));
      if (!Number.isNaN(trackIndex)) {
        handleDeleteTrack(trackIndex);
      }
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
