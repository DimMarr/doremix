import { API_BASE_URL } from "@config/index";
import { AlertManager } from "@utils/alertManager";

export class TrackRepository {
  async getByUrl(url: string) {
    const response = await fetch(`${API_BASE_URL}/tracks/by-url?url=${encodeURIComponent(url)}`, {
      credentials: 'include'
    });

    if (!response.ok) {
      throw new Error("Track not found");
    }
    return response.json();
  }

  async create(playlistId: number, url: string, title: string) {
    try {
      const response = await fetch(`${API_BASE_URL}/playlists/${playlistId}/tracks/by-url`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url, title }),
        credentials: 'include'
      });


      if (!response.ok) {
        throw new Error("Failed to add track by URL");
      }
      return response.json();
    } catch (err) {
      new AlertManager().error("Failed to add track");
    }
  }

  async delete(playlistId: number, trackId: number) {
    try {
      const response = await fetch(
        `${API_BASE_URL}/playlists/${playlistId}/track/${trackId}`,
        {
          method: "DELETE",
          credentials: 'include'
        },

      );

      if (!response.ok) {
        console.log("error from playlist removal")
        throw new Error("Failed to remove track from playlist");
      }
      return response.json();
    } catch (err) {
      throw err
    }
  }

  async share(playlistId: number, email: string, editor: boolean) {
    try {
      const response = await fetch(`${API_BASE_URL}/playlists/${playlistId}/share/user`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ "target_email": email, "is_editor": editor }),
        credentials: 'include'
      });


      if (!response.ok) {
        throw new Error("Failed to share");
      }
      return response.status;
    } catch (err) {
      new AlertManager().error("Failed to share playlist");
    }
    return response.status;
  }
  
  async shareGroup(playlistId: number, groupName: string) {
    const response = await fetch(`${API_BASE_URL}/playlists/${playlistId}/share/group`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ "group_name": groupName }),
      credentials: 'include'
    });
    if (!response.ok) {
      throw new Error("Failed to share with group");
    }
    return response.json();
  }
  
  async move(playlistId: number, trackId: number, prev_track_id: number | null) {
    try {
      const response = await fetch(`${API_BASE_URL}/playlists/${playlistId}/tracks/${trackId}/move`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prev_track_id }),
        credentials: 'include'
      });

      if (!response.ok) {
        throw new Error("Failed to move track");
      }
      return response.json();
    } catch (err) {
      throw err;
    }
  }
}
