import React, { useState } from 'react';
import { AuthProvider, useAuth } from './auth/AuthContext';
import { OverviewPage } from './components/OverviewPage';
import { TradingPage } from './components/TradingPage';
import { StrategiesPage } from './components/StrategiesPage';
import { BacktestingPage } from './components/BacktestingPage';
import { StockScreener } from './components/StockScreener';
import { SettingsPage } from './components/SettingsPage';
import { AgentAnimation } from './components/AgentAnimation';
import { ChatInterface } from './components/ChatInterface';
import { AgentMonitor } from './components/AgentMonitor';
import { WatchlistPage } from './components/WatchlistPage';
import { SignalsPage } from './components/SignalsPage';
import { PortfolioPage } from './components/PortfolioPage';
import { LiveStatusPanel } from './components/LiveStatusPanel';
import { BrokerReconciliation } from './components/BrokerReconciliation';

type Page =
  | 'overview'
  | 'chat'
  | 'watchlist'
  | 'signals'
  | 'portfolio'
  | 'trading'
  | 'strategies'
  | 'backtesting'
  | 'screener'
  | 'settings'
  | 'animation'
  | 'live-status'
  | 'broker-recon';

function DashboardContent() {
  const [page, setPage] = useState<Page>('overview');
  const { isAuthenticated, loading, username, logout } = useAuth();

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
    return <LoginPage />;
  }

  const renderPage = () => {
    switch (page) {
      case 'overview': return <OverviewPage />;
      case 'trading': return <TradingPage />;
      case 'strategies': return <StrategiesPage />;
      case 'backtesting': return <BacktestingPage />;
      case 'screener': return <StockScreener />;
      case 'settings': return <SettingsPage />;
      case 'animation': return <AgentAnimation />;
      case 'watchlist': return <WatchlistPage />;
      case 'signals': return <SignalsPage />;
      case 'portfolio': return <PortfolioPage />;
      case 'live-status': return <LiveStatusPanel />;
      case 'broker-recon': return <BrokerReconciliation />;
      default:
        return <ChatInterface />;
    }
  };

  return (
    <div className="min-h-screen bg-black text-white grid grid-cols-1 lg:grid-cols-[280px_1fr]">
      <aside className="border-r border-gray-900 p-4">
        <div className="flex items-center justify-between mb-3">
          <span className="text-lg font-bold">Trading Dashboard</span>
          <div className="flex items-center gap-2">
            <span className="text-xs text-gray-500">{username}</span>
            <button onClick={logout} className="text-xs text-red-400 hover:text-red-300">Logout</button>
          </div>
        </div>
        <AgentMonitor />
        <div className="h-px bg-gray-800 my-4" />
        <div className="space-y-2">
          {(
            [
              'overview',
              'chat',
              'watchlist',
              'signals',
              'portfolio',
              'trading',
              'strategies',
              'backtesting',
              'screener',
              'live-status',
              'broker-recon',
              'settings',
              'animation',
            ] as Page[]
          ).map((p) => (
            <button
              key={p}
              onClick={() => setPage(p)}
              className={`w-full text-left px-3 py-2 rounded font-semibold ${
                page === p ? 'bg-blue-600 hover:bg-blue-700' : 'bg-gray-900 hover:bg-gray-800'
              }`}
            >
              {p}
            </button>
          ))}
        </div>
        <div className="h-px bg-gray-800 my-4" />
        <div className="space-y-2">
          {(['live-status', 'broker-recon'] as Page[]).map((p) => (
            <button
              key={p}
              onClick={() => setPage(p)}
              className={`w-full text-left px-3 py-2 rounded font-semibold text-xs uppercase tracking-wide ${
                page === p ? 'bg-blue-600 hover:bg-blue-700' : 'bg-gray-900 hover:bg-gray-800'
              }`}
            >
              {p === 'live-status' ? 'Live Status' : 'Broker Recon'}
            </button>
          ))}
        </div>
      </aside>
      <main className="min-w-0">{renderPage()}</main>
    </div>
  );
}

function LoginPage() {
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
      if (!result.success) {
        setError(result.error || 'Login failed');
      }
    } catch (err: any) {
      setError(err.message || 'Network error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center h-screen bg-black text-white">
      <div className="bg-gray-950 border border-gray-800 rounded-lg p-8 w-full max-w-sm">
        <h1 className="text-xl font-bold mb-6 text-center">Trading Dashboard Login</h1>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm text-gray-400 mb-1">Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full bg-gray-900 border border-gray-700 rounded px-3 py-2 text-white focus:outline-none focus:border-blue-500"
              required
              autoFocus
            />
          </div>
          <div>
            <label className="block text-sm text-gray-400 mb-1">Password</label>
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
        <p className="text-xs text-gray-600 mt-4 text-center">Default: admin / change-me-now</p>
      </div>
    </div>
  );
}

function AppWrapper() {
  return (
    <AuthProvider>
      <DashboardContent />
    </AuthProvider>
  );
}

export default AppWrapper;
