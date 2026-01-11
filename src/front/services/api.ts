const API_BASE_URL = "http://localhost:8000";

export async function fetchPlaylists() {
  const response = await fetch(`${API_BASE_URL}/playlists/`);
  if (!response.ok) {
    throw new Error("Failed to fetch playlists");
  }
  return response.json();
}

export async function fetchPlaylist(playlistId) {
  const response = await fetch(`${API_BASE_URL}/playlists/${playlistId}`);
  if (!response.ok) {
    throw new Error("Failed to fetch playlist");
  }
  return response.json();
}

export async function fetchPlaylistTracks(playlistId) {
  const response = await fetch(
    `${API_BASE_URL}/playlists/${playlistId}/tracks`,
  );
  if (!response.ok) {
    throw new Error("Failed to fetch tracks");
  }
  return response.json();
}

export async function getTrackByUrl(url: string) {
  const response = await fetch(`${API_BASE_URL}/tracks/by-url?url=${encodeURIComponent(url)}`);
  if (!response.ok) {
    throw new Error("Track not found");
  }
  return response.json();
}

export async function addTrackByUrl(playlistId: number, url: string, title: string) {
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

export async function removeTrackFromPlaylist(playlistId, trackId) {
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

export async function uploadPlaylistCover(playlistId, imageFile) {
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

export function getCoverImageUrl(coverPath) {
  if (!coverPath) return null;
  return `${API_BASE_URL}/playlists/${coverPath}`;
}
