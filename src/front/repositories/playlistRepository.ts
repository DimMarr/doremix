import { API_BASE_URL } from "@config/index";
import Playlist, { Visibility } from "@models/playlist";
import { Track } from "@models/track";
import { Artist } from "@models/artist";
import { AlertManager } from "@utils/alertManager";
import { handleHttpError } from "@utils/errorHandling";
import { authService } from "@utils/authentication";

export interface VoteResponse {
    score: number;
    userVote: number | null;
}

export class PlaylistRepository {
    private async _fetchAll() {
        try {
            const response = await authService.fetchWithAuth(`${API_BASE_URL}/playlists/`, {
                credentials: 'include'
            });

            if (!response.ok) {
                handleHttpError(response, "Fetch playlists");
                throw new Error("Failed to fetch playlists");
            }
            return response.json();
        } catch (error) {
            throw error;
        }
    }

    private async _fetchPublic() {
        const response = await authService.fetchWithAuth(`${API_BASE_URL}/playlists/public`, {
            credentials: 'include'
        });

        if (!response.ok) {
            throw new Error("Failed to fetch public playlists");
        }
        return response.json();
    }

    private async _fetchById(playlistId: number) {
        try {
            const response = await authService.fetchWithAuth(`${API_BASE_URL}/playlists/${playlistId}`, {
                credentials: 'include'
            });

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

    private async _fetchTracks(playlistId: number) {
        try {
            const response = await authService.fetchWithAuth(
                `${API_BASE_URL}/playlists/${playlistId}/tracks`,
                {
                    credentials: 'include'
                }
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

    async create(name: string, idGenre?: number) {
        try {
            const body: Record<string, unknown> = { name };
            if (idGenre !== undefined) body.idGenre = idGenre;
            const response = await authService.fetchWithAuth(`${API_BASE_URL}/playlists/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(body),
                credentials: 'include'
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

    async uploadCover(playlistId: number, imageFile: File) {
        try {
            const formData = new FormData();
            formData.append("file", imageFile);

            const response = await authService.fetchWithAuth(
                `${API_BASE_URL}/playlists/${playlistId}/cover`,
                {
                    method: "POST",
                    body: formData,
                    credentials: 'include'
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

    getCoverUrl(coverPath: string) {
        if (!coverPath) return null;
        if (coverPath.startsWith("asset:")) {
            const assetName = coverPath.split(":")[1];
            if (assetName === "playlist1.jpg") return new URL("../assets/images/playlist1.jpg", import.meta.url).href;
            if (assetName === "playlist2.jpg") return new URL("../assets/images/playlist2.jpg", import.meta.url).href;
            if (assetName === "playlist3.jpg") return new URL("../assets/images/playlist3.jpg", import.meta.url).href;
        }
        if (coverPath.startsWith("http") || coverPath.startsWith("https")) return coverPath;
        return `${API_BASE_URL}/covers/${coverPath}`;
    }

    async getAll(): Promise<Playlist[]> {
        const img1 = new URL("../assets/images/playlist1.jpg", import.meta.url).href;
        try {
            const rawDataPlaylists = await this._fetchAll();
            // Lazy loading: do NOT fetch tracks here
            const playlists = rawDataPlaylists.map((item: any) => {
                // Ensure visibility is correctly mapped, handling case-insensitivity
                let visibility: Visibility = Visibility.public;
                if (item.visibility) {
                    const vizLower = item.visibility.toLowerCase();
                    if (Object.values(Visibility).includes(vizLower as Visibility)) {
                        visibility = vizLower as Visibility;
                    }
                }

                return new Playlist({
                    ...item,
                    genreLabel: item.genre?.label,
                    image: item.coverImage ? this.getCoverUrl(item.coverImage) : img1,
                    visibility: visibility,
                    userVote: item.userVote ?? null,
                    tracks: [], // Initialize with empty tracks
                });
            });
            return playlists;
        } catch (error) {
            console.error("Erreur lors de la récupération des playlists", error);
            return [];
        }
    }

    async getPublic(): Promise<Playlist[]> {
        const img1 = new URL("../assets/images/playlist1.jpg", import.meta.url).href;
        try {
            const rawDataPlaylists = await this._fetchPublic();
            // Lazy loading: do NOT fetch tracks here
            const playlists = rawDataPlaylists.map((item: any) => {
                // Ensure visibility is correctly mapped, handling case-insensitivity
                let visibility: Visibility = Visibility.public;
                if (item.visibility) {
                    const vizLower = item.visibility.toLowerCase();
                    if (Object.values(Visibility).includes(vizLower as Visibility)) {
                        visibility = vizLower as Visibility;
                    }
                }

                return new Playlist({
                    ...item,
                    genreLabel: item.genre?.label,
                    image: item.coverImage ? this.getCoverUrl(item.coverImage) : img1,
                    visibility: visibility,
                    userVote: item.userVote ?? null,
                    tracks: [], // Initialize with empty tracks
                });
            });
            return playlists;
        } catch (error) {
            console.error("Erreur lors de la récupération des playlists", error);
            return [];
        }
    }

    async getShared(): Promise<Playlist[]> {
        const img1 = new URL("../assets/images/playlist1.jpg", import.meta.url).href;
        try {
            const response = await authService.fetchWithAuth(`${API_BASE_URL}/playlists/shared`, {
                method: "GET",
                credentials: "include",
            });

            if (!response.ok) {
                throw new Error("Failed to get shared playlists");
            }

            const rawDataPlaylists = await response.json();
            return Promise.all(
                rawDataPlaylists.map(async (item: any) => {
                    const rawDatatracks = await this._fetchTracks(item.idPlaylist);
                    const tracks = rawDatatracks.map((data: any) => new Track(data));

                    let visibility: Visibility = Visibility.public;
                    if (item.visibility) {
                        const vizLower = item.visibility.toLowerCase();
                        if (Object.values(Visibility).includes(vizLower as Visibility)) {
                            visibility = vizLower as Visibility;
                        }
                    }

                    return new Playlist({
                    ...item,
                    image: item.coverImage ? this.getCoverUrl(item.coverImage) : img1,
                    visibility,
                    userVote: item.userVote ?? null,
                    tracks,
                    });
                })
            );
        } catch (error) {
            if (error instanceof TypeError) {
                new AlertManager().error("Network error. Check your connection.");
            }
            console.error("Error fetching shared playlists:", error);
            throw error;
        }
    }

    async getTracks(playlistId: number): Promise<Track[]> {
        const rawDatatracks = await this._fetchTracks(playlistId);
        const tracks: Track[] = [];
        for (const data of rawDatatracks) {
            tracks.push(new Track(data));
        }
        return tracks;
    }

    async castVote(playlistId: number, value: -1 | 0 | 1): Promise<VoteResponse> {
        try {
            const response = await authService.fetchWithAuth(`${API_BASE_URL}/playlists/${playlistId}/vote`, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                },
                credentials: "include",
                body: JSON.stringify({ value }),
            });

            if (!response.ok) {
                handleHttpError(response, "Vote");
                throw new Error("Failed to cast vote");
            }

            return response.json();
        } catch (error) {
            if (error instanceof TypeError) {
                new AlertManager().error("Network error. Check your connection.");
            }
            throw error;
        }
    }

    async getById(id: number): Promise<Playlist> {
        const rawData = await this._fetchById(id);
        const rawDataTracks = await this._fetchTracks(id);
        const tracks = rawDataTracks.map((data: any) => new Track(data));
        const artists = rawDataTracks.map((data: any) => new Artist(data.artist));

        const img1 = new URL("../assets/images/playlist1.jpg", import.meta.url).href;

        return new Playlist({
            ...rawData,
            genreLabel: rawData.genre?.label,
            image: rawData.coverImage ? this.getCoverUrl(rawData.coverImage) : img1,
            visibility: rawData.visibility ? rawData.visibility.toLowerCase() as Visibility : Visibility.public,
            userVote: rawData.userVote ?? null,
            tracks: tracks,
            artists: artists
        });
    }

    private sharedWithCache = new Map<number, Promise<any>>();
    private sharedGroupsCache = new Map<number, Promise<any>>();

    invalidateSharedWithCache(playlistId: number): void {
        this.sharedWithCache.delete(playlistId);
        this.sharedGroupsCache.delete(playlistId);
    }

    async shareWithGroup(playlistId: number, groupId: number): Promise<void> {
        try {
            const response = await authService.fetchWithAuth(
                `${API_BASE_URL}/playlists/${playlistId}/share/group`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({ group_id: groupId }),
                    credentials: "include",
                }
            );

            if (!response.ok) {
                if (response.status === 404) {
                    throw new Error("Group not found");
                }
                if (response.status === 409) {
                    throw new Error("Group already has access");
                }
                throw new Error("Failed to share playlist with group");
            }
            this.invalidateSharedWithCache(playlistId);
        } catch (error) {
            console.error("Error sharing playlist with group:", error);
            throw error;
        }
    }

    async sharedWith(playlist_id: Number) {
        const id = Number(playlist_id);
        if (this.sharedWithCache.has(id)) {
            return this.sharedWithCache.get(id);
        }

        const promise = (async () => {
            try {
                const response = await authService.fetchWithAuth(`${API_BASE_URL}/playlists/${id}/shared-with`, {
                    method: "GET",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    credentials: 'include',
                });

                if (response.status == 403){
                    return []
                }

                if (!response.ok) {
                    throw new Error("Failed to get shared users");
                }
                return response.json();
            } catch (error) {
                this.sharedWithCache.delete(id);
                if (error instanceof TypeError) {
                    new AlertManager().error("Network error. Check your connection.");
                }
                console.error("Error getting shared users for a playlist:", error);
                throw error;
            }
        })();

        this.sharedWithCache.set(id, promise);
        return promise;
    }

    async sharedGroups(playlist_id: Number) {
        const id = Number(playlist_id);
        if (this.sharedGroupsCache.has(id)) {
            return this.sharedGroupsCache.get(id);
        }

        const promise = (async () => {
            try {
                const response = await authService.fetchWithAuth(`${API_BASE_URL}/playlists/${id}/shared-groups`, {
                    method: "GET",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    credentials: 'include',
                });

                if (response.status == 403){
                    return []
                }

                if (!response.ok) {
                    throw new Error("Failed to get shared groups");
                }
                return response.json();
            } catch (error) {
                this.sharedGroupsCache.delete(id);
                if (error instanceof TypeError) {
                    new AlertManager().error("Network error. Check your connection.");
                }
                console.error("Error getting shared groups for a playlist:", error);
                throw error;
            }
        })();

        this.sharedGroupsCache.set(id, promise);
        return promise;
    }

    async removeSharedUser(playlistId: number, targetUserId: number): Promise<void> {
        try {
            const response = await authService.fetchWithAuth(
                `${API_BASE_URL}/playlists/${playlistId}/share/user/${targetUserId}`,
                {
                    method: "DELETE",
                    credentials: 'include',
                }
            );

            if (!response.ok) {
                handleHttpError(response, "Remove shared user");
                throw new Error("Failed to remove shared user");
            }
            this.invalidateSharedWithCache(playlistId);
        } catch (error) {
            if (error instanceof TypeError) {
                new AlertManager().error("Network error. Check your connection.");
            }
            console.error("Error removing shared user from playlist:", error);
            throw error;
        }
    }

    async removeSharedGroup(playlistId: number, targetGroupId: number): Promise<void> {
        try {
            const response = await authService.fetchWithAuth(
                `${API_BASE_URL}/playlists/${playlistId}/share/group/${targetGroupId}`,
                {
                    method: "DELETE",
                    credentials: 'include',
                }
            );

            if (!response.ok) {
                if (response.status === 404) {
                    throw new Error("Group is not associated with this playlist");
                }
                handleHttpError(response, "Remove shared group");
                throw new Error("Failed to remove shared group");
            }
            this.invalidateSharedWithCache(playlistId);
        } catch (error) {
            if (error instanceof TypeError) {
                new AlertManager().error("Network error. Check your connection.");
            }
            console.error("Error removing shared group from playlist:", error);
            throw error;
        }
    }

    async update(id: number, data: Partial<Playlist>) {
        try {
            const response = await authService.fetchWithAuth(`${API_BASE_URL}/playlists/${id}`, {
                method: "PATCH",
                headers: {
                    "Content-Type": "application/json",
                },
                credentials: 'include',
                body: JSON.stringify(data),
            });

            if (!response.ok) {
                handleHttpError(response, "Update playlist");
                throw new Error("Failed to update playlist");
            }
            return response.json();
        } catch (error) {
            if (error instanceof TypeError) {
                new AlertManager().error("Network error. Check your connection.");
            }
            console.error("Error updating playlist:", error);
            throw error;
        }
    }

    async delete(id: number): Promise<void> {
        try {
            const response = await authService.fetchWithAuth(`${API_BASE_URL}/playlists/${id}`, {
                method: "DELETE",
                credentials: 'include',
            });

            if (!response.ok) {
                handleHttpError(response, "Delete playlist");
                throw new Error("Failed to delete playlist");
            }
        } catch (error) {
            if (error instanceof TypeError) {
                new AlertManager().error("Network error. Check your connection.");
            }
            console.error("Error deleting playlist:", error);
            throw error;
        }
    }

    async adminGetAll(): Promise<Playlist[]> {
        const img1 = new URL("../assets/images/playlist1.jpg", import.meta.url).href;
        try {
            const response = await authService.fetchWithAuth(`${API_BASE_URL}/admin/playlists/`, {
                credentials: 'include',
            });
            if (!response.ok) {
                handleHttpError(response, "Admin fetch playlists");
                throw new Error("Failed to fetch all playlists");
            }
            const rawData = await response.json();
            return rawData.map((item: any) => {
                let visibility: Visibility = Visibility.public;
                if (item.visibility) {
                    const vizLower = item.visibility.toLowerCase();
                    if (Object.values(Visibility).includes(vizLower as Visibility)) {
                        visibility = vizLower as Visibility;
                    }
                }
                return new Playlist({
                    ...item,
                    genreLabel: item.genre?.label,
                    image: item.coverImage ? this.getCoverUrl(item.coverImage) : img1,
                    visibility,
                    tracks: [],
                });
            });
        } catch (error) {
            if (error instanceof TypeError) {
                new AlertManager().error("Network error. Check your connection.");
            }
            throw error;
        }
    }

    async adminUpdate(id: number, data: Partial<Playlist>): Promise<any> {
        const response = await authService.fetchWithAuth(`${API_BASE_URL}/admin/playlists/${id}`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            credentials: 'include',
            body: JSON.stringify(data),
        });
        if (!response.ok) {
            handleHttpError(response, "Admin update playlist");
            throw new Error("Failed to update playlist");
        }
        return response.json();
    }

    async adminDelete(id: number): Promise<void> {
        const response = await authService.fetchWithAuth(`${API_BASE_URL}/admin/playlists/${id}`, {
            method: "DELETE",
            credentials: 'include',
        });
        if (!response.ok) {
            handleHttpError(response, "Admin delete playlist");
            throw new Error("Failed to delete playlist");
        }
    }

    async adminGetTracks(playlistId: number): Promise<Track[]> {
        const response = await authService.fetchWithAuth(
            `${API_BASE_URL}/admin/playlists/${playlistId}/tracks`,
            { credentials: 'include' }
        );
        if (!response.ok) {
            handleHttpError(response, "Admin get tracks");
            throw new Error("Failed to fetch tracks");
        }
        const rawData = await response.json();
        return rawData.map((data: any) => new Track(data));
    }

    async adminAddTrack(playlistId: number, url: string, title: string): Promise<Track> {
        const response = await authService.fetchWithAuth(
            `${API_BASE_URL}/admin/playlists/${playlistId}/tracks/by-url`,
            {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                credentials: 'include',
                body: JSON.stringify({ url, title }),
            }
        );
        if (!response.ok) {
            handleHttpError(response, "Admin add track");
            throw new Error("Failed to add track");
        }
        return response.json();
    }

    async adminRemoveTrack(playlistId: number, trackId: number): Promise<any> {
        const response = await authService.fetchWithAuth(
            `${API_BASE_URL}/admin/playlists/${playlistId}/track/${trackId}`,
            {
                method: "DELETE",
                credentials: 'include',
            }
        );
        if (!response.ok) {
            handleHttpError(response, "Admin remove track");
            throw new Error("Failed to remove track");
        }
        return response.json();
    }

    async transfer_ownership(id: number, new_owner_email: string) {
        try {
            const response = await authService.fetchWithAuth(`${API_BASE_URL}/playlists/${id}/transfer`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                credentials: "include",
                body: JSON.stringify({ new_owner_email: new_owner_email }),
            });
            return response.status;
        } catch (error) {
            if (error instanceof TypeError) {
                new AlertManager().error("Network error. Check your connection.");
            }
            console.error("Error transferring ownership of the playlist:", error);
            throw error;
        }
    }
}
