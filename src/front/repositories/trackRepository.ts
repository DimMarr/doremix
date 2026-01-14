import { API_BASE_URL } from "@config/index";

export class TrackRepository {
  static async getTrackByUrl(url: string) {
    const response = await fetch(`${API_BASE_URL}/tracks/by-url?url=${encodeURIComponent(url)}`);
    if (!response.ok) {
      throw new Error("Track not found");
    }
    return response.json();
  }

  static async addTrackByUrl(playlistId: number, url: string, title: string) {
    const response = await fetch(`${API_BASE_URL}/playlists/${playlistId}/tracks/by-url`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url, title }),
    });
    if (!response.ok) {
      throw new Error("Failed to add track by URL");
    }
    return response.json();
  }

  static async removeTrackFromPlaylist(playlistId: number, trackId: number) {
    const response = await fetch(
      `${API_BASE_URL}/playlists/${playlistId}/track/${trackId}`,
      {
        method: "DELETE",
      },
    );
    if (!response.ok) {
      throw new Error("Failed to remove track from playlist");
    }
    return response.json();
  }
}
