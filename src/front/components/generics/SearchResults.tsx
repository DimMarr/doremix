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
            <div class={`absolute top-full left-0 right-0 mt-2 bg-gray-800 rounded-lg shadow-lg max-h-96 overflow-y-auto z-50 ${className}`}>
                <div class="p-4 text-gray-400 text-center">
                    No results found
                </div>
            </div>
        );
    }

    return (
        <div class={`absolute top-full left-0 right-0 mt-2 bg-gray-800 rounded-lg shadow-lg max-h-96 overflow-y-auto z-50 ${className}`}>
            {/* Tracks section */}
            {tracks.length > 0 && (
                <div class="p-4">
                    <h3 class="text-sm font-semibold text-gray-400 mb-2">TRACKS</h3>
                    {tracks.map((track, index) => {
                        const artistName = track.artist?.name ? ` - ${track.artist.name}` : '';
                        return (
                            <div
                                class="p-2 hover:bg-gray-700 rounded cursor-pointer"
                                data-track-index={index}
                            >
                                {`${track.title ?? 'Unknown'}${artistName}`}
                            </div>
                        );
                    })}
                </div>
            )}

            {/* Playlists section */}
            {playlists.length > 0 && (
                <div class="p-4 border-t border-gray-700">
                    <h3 class="text-sm font-semibold text-gray-400 mb-2">PLAYLISTS</h3>
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
