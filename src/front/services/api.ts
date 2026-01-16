import { AlertManager } from "@utils/AlertManager";

const API_BASE_URL = "http://localhost:8000";

function handleHttpError(response: Response, context: string) {
  switch (response.status) {
    case 429:
      new AlertManager().warning("Too many requests. Please slow down.");
      break;
    case 404:
      new AlertManager().error(`${context} not found.`);
      break;
    case 500:
    case 502:
    case 503:
      new AlertManager().error("Server error. Please try again later.");
      break;
    default:
      new AlertManager().error(`Failed to ${context.toLowerCase()}.`);
  }
}

export async function fetchPlaylist(playlistId) {
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

export async function fetchPlaylistTracks(playlistId) {
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

export async function removeTrackFromPlaylist(playlistId, trackId) {
  try {
    const response = await fetch(
      `${API_BASE_URL}/playlists/${playlistId}/track/${trackId}`,
      {
        method: "DELETE",
      },
    );
    if (!response.ok) {
      handleHttpError(response, "Remove track");
      throw new Error("Failed to remove track from playlist");
    }
    return response.json();
  } catch (error) {
    if (error instanceof TypeError) {
      new AlertManager().error("Network error. Check your connection.");
    }
    console.error("Error removing track:", error);
    throw error;
  }
}

export async function uploadPlaylistCover(playlistId, imageFile) {
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

export function getCoverImageUrl(coverPath) {
  if (!coverPath) return null;
  return `${API_BASE_URL}/playlists/${coverPath}`;
}

export async function fetchSearch(query) {
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
