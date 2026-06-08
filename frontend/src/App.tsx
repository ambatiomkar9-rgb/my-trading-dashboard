import React, { Component, useState, useEffect } from 'react';
import { AuthProvider, useAuth } from './auth/AuthContext';
import { apiFetch } from './api';

class ErrorBoundary extends Component<{children: React.ReactNode}, {hasError: boolean; error: string}> {
  constructor(props: {children: React.ReactNode}) {
    super(props);
    this.state = { hasError: false, error: '' };
  }
  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error: error.message };
  }
  render() {
    if (this.state.hasError) {
      return (
        <div className="flex items-center justify-center h-screen" style={{background:'var(--bg)'}}>
          <div className="text-center p-8 modal-box max-w-md">
            <h2 className="text-xl font-bold text-red mb-2">Something went wrong</h2>
            <p className="text-muted text-sm mb-4">{this.state.error}</p>
            <button onClick={() => window.location.reload()} className="btn btn-accent">Reload Page</button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}
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
import { PerformancePage } from './components/PerformancePage';

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
  | 'performance'
  | 'settings'
  | 'animation'
  | 'live-status'
  | 'broker-recon';

const NAV_ITEMS: { page: Page; label: string; icon: string }[] = [
  { page: 'overview', label: 'Overview', icon: '◈' },
  { page: 'chat', label: 'Chat', icon: '◆' },
  { page: 'watchlist', label: 'Watchlist', icon: '◉' },
  { page: 'signals', label: 'Signals', icon: '◎' },
  { page: 'portfolio', label: 'Portfolio', icon: '◇' },
  { page: 'trading', label: 'Trading', icon: '⬡' },
  { page: 'strategies', label: 'Strategies', icon: '⬢' },
  { page: 'backtesting', label: 'Backtest', icon: 'triangle' },
  { page: 'screener', label: 'Screener', icon: '▣' },
  { page: 'performance', label: 'Performance', icon: '▤' },
  { page: 'settings', label: 'Settings', icon: '⚙' },
];

function LiveTicker() {
  const [prices, setPrices] = useState<Record<string, number>>({});

  useEffect(() => {
    const fetchPrices = async () => {
      try {
        const data = await apiFetch('/api/watchlist');
        if (Array.isArray(data)) {
          const p: Record<string, number> = {};
          for (const item of data) {
            if (item.symbol && item.last_signal_price) {
              p[item.symbol] = item.last_signal_price;
            }
          }
          setPrices(p);
        }
      } catch { /* ignore */ }
    };
    fetchPrices();
    const t = setInterval(fetchPrices, 15000);
    return () => clearInterval(t);
  }, []);

  const entries = Object.entries(prices);
  if (entries.length === 0) return null;

  return (
    <div className="ticker-bar">
      <div className="ticker-scroll">
        {[...entries, ...entries].map(([sym, price], i) => (
          <span key={i} className="ticker-item">
            <span className="ticker-symbol">{sym}</span>
            <span className="ticker-price">₹{price.toFixed(2)}</span>
          </span>
        ))}
      </div>
    </div>
  );
}

function DashboardContent() {
  const [page, setPage] = useState<Page>('overview');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { isAuthenticated, loading, username, logout } = useAuth();

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen" style={{background:'var(--bg)'}}>
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-accent mx-auto mb-4" style={{borderColor:'var(--accent)'}} />
          <p className="text-muted">Loading...</p>
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
      case 'performance': return <PerformancePage />;
      case 'settings': return <SettingsPage />;
      case 'animation': return <AgentAnimation />;
      case 'watchlist': return <WatchlistPage />;
      case 'signals': return <SignalsPage />;
      case 'portfolio': return <PortfolioPage />;
      case 'live-status': return <LiveStatusPanel />;
      case 'broker-recon': return <BrokerReconciliation />;
      default: return <ChatInterface />;
    }
  };

  return (
    <div className="app-layout">
      <div className="scanline-overlay" />

      {/* Mobile header */}
      <header className="mobile-header lg:hidden">
        <button onClick={() => setSidebarOpen(!sidebarOpen)} className="btn btn-ghost" style={{padding:'4px 8px'}}>
          ☰
        </button>
        <span className="font-bold" style={{color:'var(--accent)'}}>Trading Dashboard</span>
        <div className="flex items-center gap-2">
          <span className="text-muted" style={{fontSize:10}}>{username}</span>
          <button onClick={logout} className="btn btn-ghost" style={{padding:'2px 6px',fontSize:10}}>Exit</button>
        </div>
      </header>

      {/* Sidebar overlay on mobile */}
      {sidebarOpen && (
        <div className="sidebar-overlay lg:hidden" onClick={() => setSidebarOpen(false)} />
      )}

      {/* Sidebar */}
      <aside className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <div>
            <div className="sidebar-logo">◈ Trading Dashboard</div>
            <div className="sidebar-subtitle">{username}</div>
          </div>
          <button onClick={logout} className="btn btn-ghost" style={{fontSize:10,padding:'2px 6px'}}>Exit</button>
        </div>

        <div className="sidebar-nav">
          {NAV_ITEMS.map((item) => (
            <button
              key={item.page}
              onClick={() => { setPage(item.page); setSidebarOpen(false); }}
              className={`nav-item ${page === item.page ? 'active' : ''}`}
            >
              <span className="nav-icon">{item.icon}</span>
              <span>{item.label}</span>
            </button>
          ))}
        </div>

        <div className="sidebar-section">
          <div className="panel-header">Agents</div>
          <div className="sidebar-agents">
            <AgentMonitor />
          </div>
        </div>

        <div className="sidebar-footer">
          <button
            onClick={() => { setPage('live-status' as Page); setSidebarOpen(false); }}
            className={`nav-item text-xs ${page === 'live-status' ? 'active' : ''}`}
          >
            <span className="nav-icon">▪</span> Live Status
          </button>
          <button
            onClick={() => { setPage('broker-recon' as Page); setSidebarOpen(false); }}
            className={`nav-item text-xs ${page === 'broker-recon' ? 'active' : ''}`}
          >
            <span className="nav-icon">▫</span> Broker Recon
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="main-content">
        <LiveTicker />
        <div className="page-content">
          {renderPage()}
        </div>
      </main>
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
    <div className="flex items-center justify-center h-screen" style={{background:'var(--bg)'}}>
      <div className="modal-box p-8 w-full max-w-sm">
        <h1 className="text-xl font-bold mb-6 text-center" style={{color:'var(--accent)'}}>
          ◈ Trading Dashboard
        </h1>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm mb-1" style={{color:'var(--text-muted)'}}>Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="input"
              required
              autoFocus
            />
          </div>
          <div>
            <label className="block text-sm mb-1" style={{color:'var(--text-muted)'}}>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="input"
              required
            />
          </div>
          {error && <p className="text-red text-sm">{error}</p>}
          <button
            type="submit"
            disabled={loading}
            className="btn btn-accent w-full"
            style={{padding:'8px 16px'}}
          >
            {loading ? '...' : 'Login'}
          </button>
        </form>
        <p className="text-muted mt-4 text-center" style={{fontSize:10}}>Contact admin for credentials</p>
      </div>
    </div>
  );
}

function AppWrapper() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <DashboardContent />
      </AuthProvider>
    </ErrorBoundary>
  );
}

export default AppWrapper;
