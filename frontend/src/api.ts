/** Shared API client with JWT token management, auto-attach, and 401 handling. */

const API_BASE = import.meta.env.VITE_API_BASE || '';

interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  username: string | null;
}

let _state: AuthState = {
  accessToken: null,
  refreshToken: null,
  isAuthenticated: false,
  username: null,
};

let _onUnauthorized: (() => void) | null = null;

export function setOnUnauthorized(fn: (() => void) | null) {
  _onUnauthorized = fn;
}

export function getAuthState(): AuthState {
  return { ..._state };
}

export function setTokens(tokens: TokenPair | null) {
  if (tokens) {
    _state.accessToken = tokens.access_token;
    _state.refreshToken = tokens.refresh_token;
    _state.isAuthenticated = true;
    localStorage.setItem('access_token', tokens.access_token);
    localStorage.setItem('refresh_token', tokens.refresh_token);
  } else {
    _state.accessToken = null;
    _state.refreshToken = null;
    _state.isAuthenticated = false;
    _state.username = null;
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }
}

export function setUsername(name: string) {
  _state.username = name;
  localStorage.setItem('username', name);
}

export function getUsername(): string | null {
  return _state.username || localStorage.getItem('username');
}

export function loadStoredAuth() {
  const access = localStorage.getItem('access_token');
  const refresh = localStorage.getItem('refresh_token');
  const username = localStorage.getItem('username');
  if (access) {
    _state.accessToken = access;
    _state.refreshToken = refresh;
    _state.isAuthenticated = true;
    _state.username = username;
  }
}

async function refreshAccessToken(): Promise<boolean> {
  if (!_state.refreshToken) return false;
  try {
    const res = await fetch(`${API_BASE}/api/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: _state.refreshToken }),
    });
    if (!res.ok) return false;
    const data: TokenPair = await res.json();
    setTokens(data);
    return true;
  } catch {
    return false;
  }
}

export async function apiFetch<T = any>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const headers = new Headers(options.headers);

  if (_state.accessToken) {
    headers.set('Authorization', `Bearer ${_state.accessToken}`);
  }

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });

  if (res.status === 401) {
    // Try refresh once
    const refreshed = await refreshAccessToken();
    if (refreshed && _state.accessToken) {
      headers.set('Authorization', `Bearer ${_state.accessToken}`);
      const retry = await fetch(`${API_BASE}${path}`, { ...options, headers });
      if (retry.status === 401) {
        setTokens(null);
        _onUnauthorized?.();
        throw new Error('Unauthorized');
      }
      if (!retry.ok) throw new Error(`API error ${retry.status}`);
      return retry.json();
    }
    setTokens(null);
    _onUnauthorized?.();
    throw new Error('Unauthorized');
  }

  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`API error ${res.status}: ${text}`);
  }

  return res.json();
}

// Convenience methods
export const api = {
  get: <T = any>(path: string) => apiFetch<T>(path),
  post: <T = any>(path: string, body?: any) =>
    apiFetch<T>(path, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: body ? JSON.stringify(body) : undefined,
    }),
  put: <T = any>(path: string, body?: any) =>
    apiFetch<T>(path, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: body ? JSON.stringify(body) : undefined,
    }),
  delete: <T = any>(path: string) => apiFetch<T>(path, { method: 'DELETE' }),
};
