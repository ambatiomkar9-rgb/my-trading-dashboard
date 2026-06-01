import React, { useState } from 'react';
import { useAuth } from './AuthContext';

interface LoginFormProps {
  onLoginSuccess?: () => void;
}

export function LoginForm({ onLoginSuccess }: LoginFormProps) {
  const { login } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const result = await login(username, password);
      if (result.success) {
        onLoginSuccess?.();
      } else {
        setError(result.error || 'Login failed');
      }
    } catch (err: any) {
      setError(err.message || 'Network error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 max-w-sm">
      <div>
        <label className="block text-sm font-medium text-gray-300 mb-1">Username</label>
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          className="w-full bg-gray-900 border border-gray-700 rounded px-3 py-2 text-white focus:outline-none focus:border-blue-500"
          required
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-300 mb-1">Password</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full bg-gray-900 border border-gray-700 rounded px-3 py-2 text-white focus:outline-none focus:border-blue-500"
          required
        />
      </div>
      {error && <p className="text-red-400 text-sm">{error}</p>}
      <button
        type="submit"
        disabled={loading}
        className="w-full px-4 py-2 bg-blue-600 rounded hover:bg-blue-700 disabled:opacity-50 font-medium"
      >
        {loading ? 'Logging in...' : 'Login'}
      </button>
    </form>
  );
}

export function LogoutButton() {
  const { isAuthenticated, username, logout } = useAuth();

  if (!isAuthenticated) return null;

  return (
    <div className="flex items-center gap-3">
      <span className="text-sm text-gray-400">Logged in as <strong className="text-white">{username}</strong></span>
      <button
        onClick={logout}
        className="px-3 py-1 bg-gray-800 rounded hover:bg-gray-700 text-sm"
      >
        Logout
      </button>
    </div>
  );
}
