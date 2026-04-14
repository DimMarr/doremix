import { API_BASE_URL } from "@config/index";
import { Artist } from "@models/artist";
import { Track } from "@models/track";
import { authService } from "@utils/authentication";

export class ArtistRepository {
  async getAll(): Promise<Artist[]> {
    const response = await authService.fetchWithAuth(`${API_BASE_URL}/artists`, { credentials: 'include' });
    if (!response.ok) throw new Error("Failed to fetch artists");
    const data = await response.json();
    return data.map((a: any) => new Artist(a));
  }

  async getById(id: number): Promise<Artist> {
    const response = await authService.fetchWithAuth(`${API_BASE_URL}/artists/${id}`, { credentials: 'include' });
    if (!response.ok) throw new Error("Failed to fetch artist");
    const data = await response.json();
    return new Artist(data);
  }

  async getTracks(id: number): Promise<Track[]> {
    const response = await authService.fetchWithAuth(`${API_BASE_URL}/artists/${id}/tracks`, { credentials: 'include' });
    if (!response.ok) throw new Error("Failed to fetch artist tracks");
    const data = await response.json();
    return data.map((t: any) => new Track({ ...t, artist: t.artists?.[0] }));
  }
}
