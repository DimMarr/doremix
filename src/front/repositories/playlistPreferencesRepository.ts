import { API_BASE_URL } from "@config/index";
import { handleHttpError } from "@utils/errorHandling";

export type SortMode = "date_desc" | "name_asc" | "custom";

export interface PlaylistPreferences {
  sort_mode: SortMode;
  custom_order: number[] | null;
}

export class PlaylistPreferencesRepository {
  async get(): Promise<PlaylistPreferences> {
    const response = await fetch(`${API_BASE_URL}/playlists/preferences`, {
      credentials: "include",
    });
    if (!response.ok) {
      handleHttpError(response, "Get playlist preferences");
      throw new Error("Failed to fetch playlist preferences");
    }
    return response.json();
  }

  async save(prefs: PlaylistPreferences): Promise<PlaylistPreferences> {
    const response = await fetch(`${API_BASE_URL}/playlists/preferences`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify(prefs),
    });
    if (!response.ok) {
      handleHttpError(response, "Save playlist preferences");
      throw new Error("Failed to save playlist preferences");
    }
    return response.json();
  }
}
