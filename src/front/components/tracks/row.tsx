import { secondsToReadableTime } from "@components/utils";
import { Track } from "@models/track";

export async function TrackRow({
  track,
  index,
  current_track,
  playlistId,
  canEditPlaylist,
  hideLikeButton,
}: {
  track: Track;
  index: number;
  current_track?: Track;
  playlistId: number;
  canEditPlaylist?: boolean;
  hideLikeButton?: boolean;
}) {
  const artistText = track.artists?.map((a) => a.name).join(", ") || "Unknown";
  const isLiked = track.isLiked ?? false;

  return (
    <div
      id={`track-${index}`}
      class={`group grid grid-cols-[2rem_1fr_1fr_4rem_2.5rem_3rem] items-center gap-4 px-4 py-2 rounded-md transition-colors duration-200 hover:bg-neutral-800 cursor-pointer ${
        current_track?.idTrack === track.idTrack ? "playing" : ""
      }`}
      data-track-index={index}
    >
      {/* Numéro de piste */}
      <div class="relative">
        <span class="track-number">{index + 1}</span>
      </div>

      {/* Titre */}
      <span safe class="font-medium track-title">
        {track.title}
      </span>

      {/* Artiste(s) */}
      <span safe>{artistText}</span>

      {/* Durée */}
      <span safe>{secondsToReadableTime(track.durationSeconds)}</span>

      {!hideLikeButton ? <button
        class={`like-track transition-all flex items-center justify-center cursor-pointer
          ${isLiked
            ? "text-primary opacity-100"
            : "opacity-0 group-hover:opacity-100 text-muted-foreground hover:text-primary"
          }`}
        data-track-id={track.idTrack}
        data-track-index={index}
        data-liked={isLiked ? "true" : "false"}
        title={isLiked ? "Remove from Liked tracks" : "Add to Liked tracks"}
        aria-label={isLiked ? "Unlike" : "Like"}
      >
        {/* Cœur plein si liké, cœur vide sinon */}
        {isLiked ? (
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="currentColor"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
          </svg>
        ) : (
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
          </svg>
        )}
      </button> : <span />}

      {/* Bouton Supprimer — seulement si l'utilisateur peut éditer */}
      {canEditPlaylist ? (
        <button
          class="opacity-0 group-hover:opacity-100 transition-opacity hover:text-destructive flex items-center justify-center cursor-pointer delete-track"
          data-track-id={track.idTrack}
          data-track-index={index}
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path d="M3 6h18" />
            <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6" />
            <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2" />
          </svg>
        </button>
      ) : (
        <span />
      )}
    </div>
  );
}
