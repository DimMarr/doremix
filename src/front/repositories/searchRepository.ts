import { Track } from "../models/track";
import Playlist from "../models/playlist";
import { fetchSearch } from "../services/api";

export interface SearchResults {
    tracks: Track[];
    playlists: Playlist[];
}

export default class SearchRepository {
    async search(query: string): Promise<SearchResults> {
        if (!query) {
            return { tracks: [], playlists: [] };
        }

        try {
            const rawData = await fetchSearch(query);

            const tracks = rawData.tracks.map((data: any) => new Track({
                ...data,
                artist: data.artists?.[0] // take first artist from array
            }));

            const playlists = rawData.playlists.map((data: any) => new Playlist({
                ...data,
                image: data.coverImage ?? null,
                visibility: data.visibility ? data.visibility.toLowerCase() : 'public'
            }));

            return { tracks, playlists };
        } catch (error) {
            console.error("Error searching", error);
            return { tracks: [], playlists: [] };
        }
    }
}
