import { TrackRepository } from "@repositories/trackRepository";
import { Button, AddTrackModal } from "@components/index";
import { TrackListHeader } from "@components/tracks/header";
import { TrackRow } from "@components/tracks/row";
import { AlertManager } from "@utils/alertManager";
import { trackPlayerInstance } from "@layouts/mainLayout";
import { YoutubePlayerState } from "@store/trackPlayer";
import { PlaylistRepository } from "@repositories/index";
import type Playlist from "@models/playlist";
import type { Track } from "@models/track";

interface PageParams {
  id: string;
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
          current_track={[YoutubePlayerState.UNSTARTED, YoutubePlayerState.CUED].includes(playerState)  ? null : currentTrack}
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
  const playlist = await new PlaylistRepository().getById(playlistId);

  // Local state
  let tracks: Track[] = playlist.tracks || [];

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
            class="w-48 h-48 rounded-md object-cover"
            alt={playlist.name}
          />
          <Button id="add-track-button" variant="outline" size="md">Add Track</Button>
        </div>
        <div class="pt-2">
          <h1 safe class="font-bold text-4xl">{playlist.name}</h1>
          <p safe class="text-muted-foreground text-lg">{playlist.description || ''}</p>
        </div>
      </div>

      <div id="track-list-container" class="flex flex-col gap-4">
        {renderTrackList({ ...playlist, tracks }) as 'safe'}
      </div>
    </div>
  );

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
