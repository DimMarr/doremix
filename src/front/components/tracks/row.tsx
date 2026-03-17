import { secondsToReadableTime } from "@components/utils";
import { Track } from "@models/track";
import { PlaylistRepository } from "@repositories/playlistRepository";
import { canEdit } from "@utils/rights";

export async function TrackRow({ track, index, current_track, playlistId }: { track: Track; index: number, current_track?: Track, playlistId: number }) {
  const artistText = track.artists?.map(a => a.name).join(', ') || 'Unknown';
  const repo = new PlaylistRepository();
  let playlist = await repo.getById(playlistId);
  const isEditable = await canEdit(repo, playlist);

  return (
    <div
      id={`track-${index}`}
      class={`group grid grid-cols-[2rem_1fr_1fr_4rem_3rem] items-center gap-4 px-4 py-2 rounded-md transition-all duration-300 ease-in-out hover:bg-neutral-800 cursor-pointer ${current_track?.idTrack === track.idTrack ? "playing" : ""}`}
      data-track-index={index}
      data-track-id={track.idTrack}
      draggable={isEditable ? "true" : "false"}
    >
      <div class="relative flex items-center gap-2">
        {isEditable && (
          <div class="cursor-grab text-neutral-500 hover:text-white opacity-0 group-hover:opacity-100 transition-opacity">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="9" cy="12" r="1" /><circle cx="9" cy="5" r="1" /><circle cx="9" cy="19" r="1" /><circle cx="15" cy="12" r="1" /><circle cx="15" cy="5" r="1" /><circle cx="15" cy="19" r="1" />
            </svg>
          </div>
        )}
        <span class="track-number">{index + 1}</span>
      </div>
      <span safe class="font-medium track-title">{track.title}</span>
      <span safe>{artistText}</span>
      <span safe>{secondsToReadableTime(track.durationSeconds)}</span>
      {await canEdit(repo, playlist) &&
        <button
          class="opacity-0 group-hover:opacity-100 transition-opacity hover:text-destructive flex items-center justify-center cursor-pointer delete-track"
          data-track-id={track.idTrack}
          data-track-index={index}
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M3 6h18"></path>
            <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"></path>
            <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"></path>
          </svg>
        </button>
      }
    </div>
  );
}
