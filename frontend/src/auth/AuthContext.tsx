import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import {
  loadStoredAuth,
  setTokens,
  setUsername,
  getUsername,
  getAuthState,
  setOnUnauthorized,
  api,
} from '../api';

interface AuthContextType {
  isAuthenticated: boolean;
  username: string | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<{ success: boolean; error?: string }>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType>({
  isAuthenticated: false,
  username: null,
  loading: true,
  login: async () => ({ success: false }),
  logout: () => {},
});

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [authState, setAuthState] = useState<AuthContextType>({
    isAuthenticated: false,
    username: null,
    loading: true,
    login: async () => ({ success: false }),
    logout: () => {},
  });

  useEffect(() => {
    loadStoredAuth();
    const state = getAuthState();

    if (state.isAuthenticated && state.accessToken) {
      fetch('/api/kill-switch', {
        headers: { Authorization: `Bearer ${state.accessToken}` },
      })
        .then((r) => {
          if (r.status === 401) {
            setTokens(null);
            state.isAuthenticated = false;
            state.username = null;
          }
        })
        .catch(() => {
          // Network error — keep local state, will fail on next API call
        })
        .finally(() => {
          setAuthState((prev) => ({
            ...prev,
            isAuthenticated: state.isAuthenticated,
            username: state.username,
            loading: false,
          }));
        });
    } else {
      setAuthState((prev) => ({
        ...prev,
        isAuthenticated: state.isAuthenticated,
        username: state.username,
        loading: false,
      }));
    }

    setOnUnauthorized(() => {
      setAuthState((prev) => ({
        ...prev,
        isAuthenticated: false,
        username: null,
      }));
    });

    return () => setOnUnauthorized(null);
  }, []);

  const login = useCallback(async (username: string, password: string) => {
    try {
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);

      const res = await fetch('/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData.toString(),
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        return { success: false, error: data.detail || 'Login failed' };
      }

      const data = await res.json();
      setTokens(data);
      setUsername(username);
      setAuthState((prev) => ({
        ...prev,
        isAuthenticated: true,
        username,
      }));
      return { success: true };
    } catch (err: any) {
      return { success: false, error: err.message || 'Network error' };
    }
  }, []);

  const logout = useCallback(() => {
    setTokens(null);
    setUsername('');
    setAuthState((prev) => ({
      ...prev,
      isAuthenticated: false,
      username: null,
    }));
  }, []);

  return (
    <AuthContext.Provider value={{ ...authState, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-black text-white">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-4" />
          <p className="text-gray-400">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="flex items-center justify-center h-screen bg-black text-white">
        <div className="text-center">
          <h2 className="text-xl font-bold mb-2">Authentication Required</h2>
          <p className="text-gray-400 mb-4">Please log in to access the dashboard.</p>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-blue-600 rounded hover:bg-blue-700"
          >
            Go to Login
          </button>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}
