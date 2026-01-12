import { API_BASE_URL } from "@config/index";


export async function fetchSearch(query) {
  const token = localStorage.getItem('auth_token');
  const headers: any = {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(
    `${API_BASE_URL}/search/?q=${encodeURIComponent(query)}`,
    {
      headers
    }
  );
  if (!response.ok) {
    throw new Error("Failed to search");
  }
  return response.json();
}
