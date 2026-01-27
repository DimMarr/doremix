import { Track } from "@models/track";
import Playlist from "@models/playlist";

export interface SearchResultsProps {
    tracks: Track[];
    playlists: Playlist[];
    className?: string;
}

export function SearchResults({
    tracks,
    playlists,
    className = ""
}: SearchResultsProps) {
    // If no results
    if (tracks.length === 0 && playlists.length === 0) {
        return (
            <div class={`absolute top-full left-0 right-0 mt-2 rounded-md border border-border bg-neutral-900 shadow-md z-50 ${className}`}>
                <div class="p-4 text-sm text-muted-foreground text-center">
                    No results found
                </div>
            </div>
        );
    }

    return (
        <div class={`absolute top-full left-0 right-0 mt-2 rounded-md border border-border bg-neutral-900 shadow-md max-h-96 overflow-y-auto z-50 ${className}`}>
            {tracks.length > 0 && (
                <div class="p-2">
                    <div class="px-2 py-1.5 text-xs font-medium text-muted-foreground">Tracks</div>
                    {tracks.map((track, index) => {
                        const artistName = track.artist?.name ? ` - ${track.artist.name}` : '';
                        return (
                            <div
                                class="relative flex cursor-pointer select-none items-center rounded-sm px-2 py-1.5 text-sm text-foreground outline-none hover:bg-neutral-800 hover:text-foreground transition-colors"
                                data-track-index={index}
                            >
                                <svg
                                    class="mr-2 h-4 w-4 text-muted-foreground"
                                    xmlns="http://www.w3.org/2000/svg"
                                    fill="none"
                                    viewBox="0 0 24 24"
                                    stroke="currentColor"
                                    stroke-width="2"
                                >
                                    <path d="M9 18V5l12-2v13" />
                                    <circle cx="6" cy="18" r="3" />
                                    <circle cx="18" cy="16" r="3" />
                                </svg>
                                <span>{`${track.title ?? 'Unknown'}${artistName}`}</span>
                            </div>
                        );
                    })}
                </div>
            )}

            {tracks.length > 0 && playlists.length > 0 && (
                <div class="-mx-1 h-px bg-border" />
            )}

            {playlists.length > 0 && (
                <div class="p-2">
                    <div class="px-2 py-1.5 text-xs font-medium text-muted-foreground">Playlists</div>
                    {playlists.map((playlist, index) => (
                        <a
                            href={`/playlist/${playlist.idPlaylist}`}
                            data-link
                            class="block p-2 hover:bg-gray-700 rounded cursor-pointer"
                            data-playlist-index={index}
                        >
                            {playlist.name ?? 'Unknown Playlist'}
                        </a>
                    ))}
                </div>
            )}
        </div>
    );
}
