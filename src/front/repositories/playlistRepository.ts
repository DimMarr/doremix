import { API_BASE_URL } from "@config/index";
import Playlist, { Visibility } from "@models/playlist";
import { Track } from "@models/track";
import { Artist } from "@models/artist";
import { AlertManager } from "@utils/alertManager";
import { handleHttpError } from "@utils/errorHandling";

export default class PlaylistRepository {
    private static async _fetchAll() {
        try {
            const response = await fetch(`${API_BASE_URL}/playlists/`);
            if (!response.ok) {
                handleHttpError(response, "Fetch playlists");
                throw new Error("Failed to fetch playlists");
            }
            return response.json();
        } catch (error) {
            throw error;
        }
    }

    private static async _fetchPublic() {
        const response = await fetch(`${API_BASE_URL}/playlists/public`);
        if (!response.ok) {
            throw new Error("Failed to fetch public playlists");
        }
        return response.json();
    }

    private static async _fetchById(playlistId: number) {
        try {
            const response = await fetch(`${API_BASE_URL}/playlists/${playlistId}`);
            if (!response.ok) {
                handleHttpError(response, "Playlist");
                throw new Error("Failed to fetch playlist");
            }
            return response.json();
        } catch (error) {
            if (error instanceof TypeError) {
                new AlertManager().error("Network error. Check your connection.");
            }
            console.error("Error fetching playlist:", error);
            throw error;
        }
    }

    private static async _fetchTracks(playlistId: number) {
        try {
            const response = await fetch(
                `${API_BASE_URL}/playlists/${playlistId}/tracks`,
            );
            if (!response.ok) {
                handleHttpError(response, "Tracks");
                throw new Error("Failed to fetch tracks");
            }
            return response.json();
        } catch (error) {
            if (error instanceof TypeError) {
                new AlertManager().error("Network error. Check your connection.");
            }
            console.error("Error fetching tracks:", error);
            throw error;
        }
    }

    static async create(name: string) {
        try {
            const response = await fetch(`${API_BASE_URL}/playlists/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ name }),
            });

            if (!response.ok) {
                handleHttpError(response, "Create playlist");
                throw new Error("Failed to create playlist");
            }
            return response.json();
        } catch (error) {
            if (error instanceof TypeError) {
                new AlertManager().error("Network error. Check your connection.");
            }
            console.error("Error creating playlist:", error);
            throw error;
        }
    }

    static async uploadCover(playlistId: number, imageFile: File) {
        try {
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
                handleHttpError(response, "Upload cover");
                throw new Error("Failed to upload cover");
            }
            return response.json();
        } catch (error) {
            if (error instanceof TypeError) {
                new AlertManager().error("Network error. Check your connection.");
            }
            console.error("Error uploading cover:", error);
            throw error;
        }
    }

    static getCoverUrl(coverPath: string) {
        if (!coverPath) return null;
        return `${API_BASE_URL}/covers/${coverPath}`;
    }

    static async getAll(): Promise<Playlist[]> {
        const img1 = new URL("../assets/images/playlist1.jpg", import.meta.url).href;
        try {
            const rawDataPlaylists = await PlaylistRepository._fetchAll();
            const playlistPromises = rawDataPlaylists.map(async (item: any) => {
                const rawDatatracks = await PlaylistRepository._fetchTracks(item.idPlaylist);
                const tracks = [];
                for (const data of rawDatatracks) {
                    tracks.push(new Track(data));
                }
                return new Playlist({
                    ...item,
                    image: item.coverImage ? PlaylistRepository.getCoverUrl(item.coverImage) : img1,
                    visibility: item.visibility ? item.visibility.toLowerCase() as Visibility : Visibility.public,
                    tracks: tracks,
                });
            });
            const playlists = await Promise.all(playlistPromises);
            return playlists;
        } catch (error) {
            console.error("Erreur lors de la récupération des playlists", error);
            return [];
        }
    }

    static async getPublic(): Promise<Playlist[]> {
        const img1 = new URL("../assets/images/playlist1.jpg", import.meta.url).href;
        try {
            const rawDataPlaylists = await PlaylistRepository._fetchPublic();
            const playlistPromises = rawDataPlaylists.map(async (item: any) => {
                const rawDatatracks = await PlaylistRepository._fetchTracks(item.idPlaylist);
                const tracks = [];
                for (const data of rawDatatracks) {
                    tracks.push(new Track(data));
                }
                return new Playlist({
                    ...item,
                    image: item.coverImage ? PlaylistRepository.getCoverUrl(item.coverImage) : img1,
                    visibility: item.visibility ? item.visibility.toLowerCase() as Visibility : Visibility.public,
                    tracks: tracks,
                });
            });
            const playlists = await Promise.all(playlistPromises);
            return playlists;
        } catch (error) {
            console.error("Erreur lors de la récupération des playlists", error);
            return [];
        }
    }

    static async getById(id: number): Promise<Playlist> {
        const rawData = await PlaylistRepository._fetchById(id);
        const rawDataTracks = await PlaylistRepository._fetchTracks(id);
        const tracks = rawDataTracks.map((data: any) => new Track(data));
        const artists = rawDataTracks.map((data: any) => new Artist(data.artist));

        const img1 = new URL("../assets/images/playlist1.jpg", import.meta.url).href;

        return new Playlist({
            ...rawData,
            image: rawData.coverImage ? PlaylistRepository.getCoverUrl(rawData.coverImage) : img1,
            visibility: rawData.visibility ? rawData.visibility.toLowerCase() as Visibility : Visibility.public,
            tracks: tracks,
            artists: artists
        });
    }
}
