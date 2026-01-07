import { Button } from "@components/generics/index";
import { TrackListHeader } from "@components/tracks/header";
import { TrackRow } from "@components/tracks/row";
import { removeTrackFromPlaylist } from "@services/api";

function TrackList(playlist, trackPlayer) {
  const tracks = playlist.tracks || [];

  const current_track = trackPlayer.getCurrentTrack();

  // Return the JSX block; previously missing return caused nothing to render
  return (
    <div>
      <TrackListHeader />
      {tracks.map((track, index) => (
        <TrackRow
          track={track}
          index={index}
          playlist={playlist}
          trackPlayer={trackPlayer}
          current_track={current_track}
        />
      ))}
    </div>
  );
}

export function PlaylistDetailPage(container, playlist, trackPlayer, onBack) {
  if (!container) return;

  const pageHtml = (
    <div>
      <div class="flex items-center mb-8 gap-4">
        <Button id="back-button" variant="ghost" size="sm">
          ← Back
        </Button>
      </div>

      <div class="flex items-center gap-8 my-8">
        <img src={playlist.image} class="w-48 h-48 rounded-md object-cover" alt={playlist.name} />
        <div>
          <h1 class="font-bold text-4xl">{playlist.name}</h1>
          <p class="text-muted-foreground text-lg">{playlist.description || ''}</p>
        </div>
      </div>

      <div id="track-list-container" class="flex flex-col gap-4">{TrackList(playlist, trackPlayer)}</div>
    </div>
  );


  const proxyPlaylist = new Proxy(playlist, {
    set(target, prop, value) {
      target[prop] = value;
      Reflect.set(target, prop, value);

      // Re-render the track list when the playlist is updated
      const trackListContainer = container.querySelector('#track-list-container');
      if (trackListContainer) {
        trackListContainer.innerHTML = '';
        trackListContainer.innerHTML = TrackList(proxyPlaylist, trackPlayer);
      }

      return true;
    }

  });

  container.innerHTML = pageHtml;

  const trackListContainer = container.querySelector('#track-list-container');

  // Use event delegation on container
  container.onclick = (e) => {
    const backButton = e.target.closest('#back-button');
    if (backButton) {
      onBack();
      return;
    }
  };

  // Handle track interactions (play/delete) via delegation on the list container
  if (trackListContainer) {
    trackListContainer.onclick = (e) => {
      const target = e.target as HTMLElement;
      const deleteButton = target.closest('.delete-track') as HTMLElement | null;
      const row = target.closest('[data-track-index]') as HTMLElement | null;

      if (deleteButton) {
        e.stopPropagation();
        const trackIndex = Number(deleteButton.getAttribute('data-track-index'));

        removeTrackFromPlaylist(
          proxyPlaylist.idPlaylist,
          proxyPlaylist.tracks[trackIndex].idTrack,
        ).then(() => {
        }).catch((err) => {
          console.error('Failed to remove track from playlist:', err);
        });

        proxyPlaylist.tracks = proxyPlaylist.tracks.filter((_, i) => i !== trackIndex);
      }

      if (row) {
        const index = Number(row.getAttribute('data-track-index'));
        if (Number.isNaN(index)) return;
        if (trackPlayer.playlist?.idPlaylist !== playlist.idPlaylist) {
          trackPlayer.setPlaylist(playlist);
        }
        trackPlayer.playTrack(index);
      }
    };
  }
}
