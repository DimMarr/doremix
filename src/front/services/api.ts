import { API_BASE_URL } from "@config/index";


export async function fetchSearch(query) {
  const response = await fetch(
    `${API_BASE_URL}/search/?q=${encodeURIComponent(query)}`,
  );
  if (!response.ok) {
    throw new Error("Failed to search");
  }
  return response.json();
}
