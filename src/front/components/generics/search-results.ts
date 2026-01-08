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
    console.log("createSearchResults called with:", props);

    const { tracks, playlists, onTrackClick, onPlaylistClick, className = "" } = props;

    const container = document.createElement("div");
    container.className = `absolute top-full left-0 right-0 mt-2 bg-gray-800 rounded-lg shadow-lg max-h-96 overflow-y-auto z-50 ${className}`;

    console.log("Container created, className:", container.className);

    // If no results
    if (tracks.length === 0 && playlists.length === 0) {
        console.log("No results branch");
        const empty = document.createElement("div");
        empty.className = "p-4 text-gray-400 text-center";
        empty.textContent = "No results found";
        container.appendChild(empty);
        return container;
    }

    console.log("Has results, tracks.length:", tracks.length, "playlists.length:", playlists.length);

    // Tracks section
    if (tracks.length > 0) {
        console.log("Creating tracks section");
        const tracksSection = document.createElement("div");
        tracksSection.className = "p-4";

        const tracksTitle = document.createElement("h3");
        tracksTitle.className = "text-sm font-semibold text-gray-400 mb-2";
        tracksTitle.textContent = "TRACKS";
        tracksSection.appendChild(tracksTitle);
        console.log("Tracks title added");

        tracks.forEach((track, index) => {
            console.log(`Processing track ${index}:`, track);
            const trackItem = document.createElement("div");
            trackItem.className = "p-2 hover:bg-gray-700 rounded cursor-pointer";
            const artistName = track.artist?.name ? ` - ${track.artist.name}` : '';
            trackItem.textContent = `${track.title ?? 'Unknown'}${artistName}`;
            console.log(`Track ${index} item text:`, trackItem.textContent);
            trackItem.onclick = () => onTrackClick(track);
            tracksSection.appendChild(trackItem);
        });

        console.log("Appending tracks section to container, tracksSection children:", tracksSection.children.length);
        container.appendChild(tracksSection);
    }

    // Playlists section
    if (playlists.length > 0) {
        console.log("Creating playlists section");
        const playlistsSection = document.createElement("div");
        playlistsSection.className = "p-4 border-t border-gray-700";

        const playlistsTitle = document.createElement("h3");
        playlistsTitle.className = "text-sm font-semibold text-gray-400 mb-2";
        playlistsTitle.textContent = "PLAYLISTS";
        playlistsSection.appendChild(playlistsTitle);

        playlists.forEach((playlist, index) => {
            console.log(`Processing playlist ${index}:`, playlist);
            const playlistItem = document.createElement("div");
            playlistItem.className = "p-2 hover:bg-gray-700 rounded cursor-pointer";
            playlistItem.textContent = playlist.name ?? 'Unknown Playlist';
            playlistItem.onclick = () => onPlaylistClick(playlist);
            playlistsSection.appendChild(playlistItem);
        });

        container.appendChild(playlistsSection);
    }

    console.log("Returning container with children count:", container.children.length);
    return container;
}
