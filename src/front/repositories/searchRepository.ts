import { Track } from "@models/track";
import Playlist from "@models/playlist";
import { PlaylistRepository } from "./playlistRepository";
import { API_BASE_URL } from "@config/index";
import { handleHttpError } from "@utils/errorHandling";
import { AlertManager } from "@utils/alertManager";

export interface SearchResults {
    tracks: Track[];
    playlists: Playlist[];
}

export class SearchRepository {
    private async _fetch(query: string) {
      try {
        const response = await fetch(
          `${API_BASE_URL}/search/?q=${encodeURIComponent(query)}`,
        );
        if (!response.ok) {
          handleHttpError(response, "Search");
          throw new Error("Failed to search");
        }
        return response.json();
      } catch (error) {
        if (error instanceof TypeError) {
          new AlertManager().error("Network error. Check your connection.");
        }
        console.error("Error searching:", error);
        throw error;
      }
    }

    async search(query: string): Promise<SearchResults> {
        if (!query) {
            return { tracks: [], playlists: [] };
        }

        try {
            const rawData = await this._fetch(query);

            const tracks = rawData.tracks.map((data: any) => new Track({
                ...data,
                artist: data.artists?.[0] // take first artist from array
            }));

            const playlists = rawData.playlists.map((data: any) => new Playlist({
                ...data,
                image: data.coverImage ? new PlaylistRepository().getCoverUrl(data.coverImage) : null,
                visibility: data.visibility ? data.visibility.toLowerCase() : 'public'
            }));

            return { tracks, playlists };
        } catch (error) {
            console.error("Error searching", error);
            return { tracks: [], playlists: [] };
        }
    }
}
