import { Track } from "../../models/track";
import Playlist from "../../models/playlist";

export interface SearchResultsProps {
    tracks: Track[];
    playlists: Playlist[];
    onTrackClick: (track: Track) => void;
    onPlaylistClick: (playlist: Playlist) => void;
    className?: string;
}

export function createSearchResults(props: SearchResultsProps): HTMLDivElement {
    const { tracks, playlists, onTrackClick, onPlaylistClick, className = "" } = props;

    const container = document.createElement("div");
    container.className = `absolute top-full left-0 right-0 mt-2 bg-gray-800 rounded-lg shadow-lg max-h-96 overflow-y-auto z-50 ${className}`;

    // If no results
    if (tracks.length === 0 && playlists.length === 0) {
        const empty = document.createElement("div");
        empty.className = "p-4 text-gray-400 text-center";
        empty.textContent = "No results found";
        container.appendChild(empty);
        return container;
    }

    // Tracks section
    if (tracks.length > 0) {
        const tracksSection = document.createElement("div");
        tracksSection.className = "p-4";

        const tracksTitle = document.createElement("h3");
        tracksTitle.className = "text-sm font-semibold text-gray-400 mb-2";
        tracksTitle.textContent = "TRACKS";
        tracksSection.appendChild(tracksTitle);

        tracks.forEach((track) => {
            const trackItem = document.createElement("div");
            trackItem.className = "p-2 hover:bg-gray-700 rounded cursor-pointer";
            const artistName = track.artist?.name ? ` - ${track.artist.name}` : '';
            trackItem.textContent = `${track.title ?? 'Unknown'}${artistName}`;
            trackItem.onclick = () => onTrackClick(track);
            tracksSection.appendChild(trackItem);
        });

        container.appendChild(tracksSection);
    }

    // Playlists section
    if (playlists.length > 0) {
        const playlistsSection = document.createElement("div");
        playlistsSection.className = "p-4 border-t border-gray-700";

        const playlistsTitle = document.createElement("h3");
        playlistsTitle.className = "text-sm font-semibold text-gray-400 mb-2";
        playlistsTitle.textContent = "PLAYLISTS";
        playlistsSection.appendChild(playlistsTitle);

        playlists.forEach((playlist) => {
            const playlistItem = document.createElement("div");
            playlistItem.className = "p-2 hover:bg-gray-700 rounded cursor-pointer";
            playlistItem.textContent = playlist.name ?? 'Unknown Playlist';
            playlistItem.onclick = () => onPlaylistClick(playlist);
            playlistsSection.appendChild(playlistItem);
        });

        container.appendChild(playlistsSection);
    }

    return container;
}
