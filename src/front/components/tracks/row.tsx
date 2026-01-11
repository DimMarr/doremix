import { secondsToReadableTime } from "@components/utils";
import { Track } from "@models/track";

export function TrackRow({ track, index, current_track }: { track: Track; index: number, current_track?: Track }) {
  const artistText = track.artists?.map(a => a.name).join(', ') || 'Unknown';

  return (
    <div
      id={`track-${index}`}
      class={`group grid grid-cols-[2rem_1fr_1fr_4rem_3rem] items-center gap-4 px-4 py-2 rounded-md transition-colors duration-200 hover:bg-gray-800 cursor-pointer ${current_track.idTrack === track.idTrack ? "playing" : ""}`}

      data-track-index={index}
    >
      <div class="relative">
        <span class="track-number">{index + 1}</span>
      </div>
      <span safe class="font-medium track-title">{track.title}</span>
      <span safe>{artistText}</span>
      <span safe>{secondsToReadableTime(track.durationSeconds)}</span>
      <button
        class="opacity-0 group-hover:opacity-100 transition-opacity hover:text-red-500 flex items-center justify-center cursor-pointer delete-track"
        data-track-id={track.idTrack}
        data-track-index={index}
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M3 6h18"></path>
          <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"></path>
          <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"></path>
        </svg>
      </button>
    </div>
  );
}
