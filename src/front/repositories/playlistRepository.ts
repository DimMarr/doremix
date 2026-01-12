import { API_BASE_URL } from "@config/index";
import Playlist, { Visibility } from "../models/playlist";
import { Track } from "../models/track";
import { Artist } from "../models/artist";

export default class PlaylistRepository {
    static async fetchPlaylists() {
        const response = await fetch(`${API_BASE_URL}/playlists/`);
        if (!response.ok) {
            throw new Error("Failed to fetch playlists");
        }
        return response.json();
    }

    static async fetchPlaylist(playlistId: number) {
        const response = await fetch(`${API_BASE_URL}/playlists/${playlistId}`);
        if (!response.ok) {
            throw new Error("Failed to fetch playlist");
        }
        return response.json();
    }

    static async fetchPlaylistTracks(playlistId: number) {
        const response = await fetch(
            `${API_BASE_URL}/playlists/${playlistId}/tracks`,
        );
        if (!response.ok) {
            throw new Error("Failed to fetch tracks");
        }
        return response.json();
    }

    static async uploadPlaylistCover(playlistId: number, imageFile: File) {
        const formData = new FormData();
        formData.append("file", imageFile);

        const response = await fetch(
            `${API_BASE_URL}/playlists/${playlistId}/cover`,
            {
                method: "POST",
                body: formData,
            },
        );

        if (!response.ok) {
            throw new Error("Failed to upload cover");
        }
        return response.json();
    }

    static getCoverImageUrl(coverPath: string) {
        if (!coverPath) return null;
        return `${API_BASE_URL}/playlists/${coverPath}`;
    }

    async getPlaylists(): Promise<Playlist[]> {
      const img1 = new URL("../assets/images/playlist1.jpg", import.meta.url).href;
      try {
        const rawDataPlaylists = await PlaylistRepository.fetchPlaylists();
        const playlistPromises = rawDataPlaylists.map(async (item: any) => {
            const rawDatatracks = await PlaylistRepository.fetchPlaylistTracks(item.idPlaylist);
            const tracks = [];
            for (const data of rawDatatracks) {
                tracks.push(new Track(data));
            }
            return new Playlist({
                ...item,
                image: item.coverImage ?? img1,
                visibility: item.visibility ? item.visibility.toLowerCase() as Visibility : Visibility.public,
                tracks: tracks
            });
        });
        const playlists = await Promise.all(playlistPromises);
        return playlists;
      } catch (error) {
          console.error("Erreur lors de la récupération des playlists", error);
          return [];
      }
    }

    async getPlaylistById(id: number): Promise<Playlist> {
        const rawData = await PlaylistRepository.fetchPlaylist(id);
        const rawDataTracks = await PlaylistRepository.fetchPlaylistTracks(id);
        const tracks = rawDataTracks.map((data: any) => new Track(data));
        const artists = rawDataTracks.map((data: any) => new Artist(data.artist));

        const img1 = new URL("../assets/images/playlist1.jpg", import.meta.url).href;

        return new Playlist({
            ...rawData,
            image: rawData.coverImage ?? img1,
            visibility: rawData.visibility ? rawData.visibility.toLowerCase() as Visibility : Visibility.public,
            tracks: tracks,
            artists: artists
        });
    }
}
