import { API_BASE_URL } from '@config';

export async function fetchWithAuth(
  url: string,
  options: RequestInit = {}
): Promise<Response> {
  const token = localStorage.getItem('auth_token');

  const headers = {
    ...options.headers,
    ...(token && { 'Authorization': `Bearer ${token}` }),
  };

  const response = await fetch(url, { ...options, headers });

  // Handle 401 - redirect to login
  if (response.status === 401) {
    localStorage.removeItem('auth_token');
    window.location.href = '/login';
    throw new Error('Unauthorized');
  }

  return response;
}

// Helper functions
export async function get(endpoint: string) {
  return fetchWithAuth(`${API_BASE_URL}${endpoint}`);
}

export async function post(endpoint: string, data: any) {
  return fetchWithAuth(`${API_BASE_URL}${endpoint}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
}

export async function put(endpoint: string, data: any) {
  return fetchWithAuth(`${API_BASE_URL}${endpoint}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
}

export async function del(endpoint: string) {
  return fetchWithAuth(`${API_BASE_URL}${endpoint}`, {
    method: 'DELETE',
  });
}
