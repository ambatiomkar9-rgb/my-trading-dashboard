import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { AuthProvider, useAuth } from './auth/AuthContext';
import { apiFetch } from './api';
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
import { ToastContainer } from './components/ToastContainer';

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

interface RuntimeStatus {
  running?: boolean;
  app_name?: string;
  env?: string;
  watchlist_count?: number;
  strategy_count?: number;
  strategy_counts?: {
    generated?: number;
    pending_approval?: number;
    approved?: number;
    rejected?: number;
  };
  research_running?: boolean;
  validation_running?: boolean;
  registry_running?: boolean;
  auto_approve_strategies?: boolean;
  event_bus?: {
    worker_count?: number;
    queue_size?: number;
    running?: boolean;
  };
  hermes?: {
    online?: boolean;
    info?: string;
    backend?: string;
    model?: string;
  };
}

interface AgentCard {
  agent_id: string;
  status: string;
  task: string;
  progress: number;
  detail?: string;
}

interface ShellMetricProps {
  label: string;
  value: string;
  detail: string;
  tone?: 'accent' | 'success' | 'warning' | 'danger';
}

const NAV_ITEMS: { page: Page; label: string; badge: string }[] = [
  { page: 'overview', label: 'Overview', badge: 'OV' },
  { page: 'chat', label: 'Chat', badge: 'CH' },
  { page: 'watchlist', label: 'Watchlist', badge: 'WL' },
  { page: 'signals', label: 'Signals', badge: 'SG' },
  { page: 'portfolio', label: 'Portfolio', badge: 'PF' },
  { page: 'trading', label: 'Trading', badge: 'TR' },
  { page: 'strategies', label: 'Strategies', badge: 'ST' },
  { page: 'backtesting', label: 'Backtest', badge: 'BT' },
  { page: 'screener', label: 'Screener', badge: 'SC' },
  { page: 'performance', label: 'Performance', badge: 'PR' },
  { page: 'settings', label: 'Settings', badge: 'SE' },
];

const QUICK_JUMPS: { page: Page; label: string; badge: string }[] = [
  { page: 'overview', label: 'Overview', badge: 'OV' },
  { page: 'chat', label: 'Chat', badge: 'CH' },
  { page: 'signals', label: 'Signals', badge: 'SG' },
  { page: 'strategies', label: 'Strategies', badge: 'ST' },
  { page: 'watchlist', label: 'Watchlist', badge: 'WL' },
  { page: 'trading', label: 'Trading', badge: 'TR' },
];

function ShellMetric({ label, value, detail, tone = 'accent' }: ShellMetricProps) {
  return (
    <div className={`shell-metric shell-metric-${tone}`}>
      <div className="shell-metric-label">{label}</div>
      <div className="shell-metric-value">{value}</div>
      <div className="shell-metric-detail">{detail}</div>
    </div>
  );
}

function LiveTicker() {
  const [prices, setPrices] = useState<Record<string, number>>({});

  useEffect(() => {
    const fetchPrices = async () => {
      try {
        const data = await apiFetch('/api/watchlist');
        if (Array.isArray(data)) {
          const next: Record<string, number> = {};
          for (const item of data) {
            if (item.symbol && item.last_signal_price) {
              next[item.symbol] = item.last_signal_price;
            }
          }
          setPrices(next);
        }
      } catch {
        // keep the previous ticker values if the request fails
      }
    };

    fetchPrices();
    const timer = setInterval(fetchPrices, 15000);
    return () => clearInterval(timer);
  }, []);

  const entries = Object.entries(prices);
  if (entries.length === 0) return null;

  return (
    <div className="ticker-bar">
      <div className="ticker-scroll">
        {[...entries, ...entries].map(([symbol, price], index) => (
          <span key={`${symbol}-${index}`} className="ticker-item">
            <span className="ticker-symbol">{symbol}</span>
            <span className="ticker-price">INR {price.toFixed(2)}</span>
          </span>
        ))}
      </div>
    </div>
  );
}

function DashboardShell() {
  const [page, setPage] = useState<Page>('overview');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [runtime, setRuntime] = useState<RuntimeStatus | null>(null);
  const [agentCards, setAgentCards] = useState<AgentCard[]>([]);
  const [summaryLoading, setSummaryLoading] = useState(true);
  const [summaryError, setSummaryError] = useState<string | null>(null);
  const [lastRefreshed, setLastRefreshed] = useState<string>('');
  const { username, logout } = useAuth();

  const refreshSummary = useCallback(async () => {
    try {
      const [runtimeData, agentData] = await Promise.all([
        apiFetch<RuntimeStatus>('/api/runtime/status'),
        apiFetch<AgentCard[]>('/agent-status'),
      ]);
      setRuntime(runtimeData || null);
      setAgentCards(Array.isArray(agentData) ? agentData : []);
      setSummaryError(null);
      setLastRefreshed(new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }));
    } catch (error: any) {
      setSummaryError(error?.message || 'Unable to load runtime status');
    } finally {
      setSummaryLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshSummary();
    const timer = setInterval(refreshSummary, 15000);
    return () => clearInterval(timer);
  }, [refreshSummary]);

  const currentPage = NAV_ITEMS.find((item) => item.page === page) || NAV_ITEMS[0];
  const agentOnlineCount = useMemo(
    () => agentCards.filter((agent) => ['online', 'running', 'healthy'].includes(String(agent.status).toLowerCase())).length,
    [agentCards],
  );

  const pendingStrategies = runtime?.strategy_counts?.pending_approval ?? 0;
  const strategyCount = runtime?.strategy_count ?? 0;
  const watchlistCount = runtime?.watchlist_count ?? 0;
  const systemOnline = Boolean(runtime?.running);
  const hermesOnline = Boolean(runtime?.hermes?.online);
  const eventBusWorkers = runtime?.event_bus?.worker_count ?? 0;
  const eventBusQueue = runtime?.event_bus?.queue_size ?? 0;

  const navigateTo = (nextPage: Page) => {
    setPage(nextPage);
    setSidebarOpen(false);
  };

  const renderPage = () => {
    switch (page) {
      case 'overview':
        return <OverviewPage />;
      case 'trading':
        return <TradingPage />;
      case 'strategies':
        return <StrategiesPage />;
      case 'backtesting':
        return <BacktestingPage />;
      case 'screener':
        return <StockScreener />;
      case 'performance':
        return <PerformancePage />;
      case 'settings':
        return <SettingsPage />;
      case 'animation':
        return <AgentAnimation />;
      case 'watchlist':
        return <WatchlistPage />;
      case 'signals':
        return <SignalsPage />;
      case 'portfolio':
        return <PortfolioPage />;
      case 'live-status':
        return <LiveStatusPanel />;
      case 'broker-recon':
        return <BrokerReconciliation />;
      default:
        return <ChatInterface />;
    }
  };

  const shellStatusTone = systemOnline ? 'success' : 'danger';
  const hermesTone = hermesOnline ? 'success' : 'warning';

  return (
    <div className="dashboard-root">
      <div className="scanline-overlay" />
      <ToastContainer />

      <header className="mobile-header lg:hidden">
        <button onClick={() => setSidebarOpen(!sidebarOpen)} className="btn btn-ghost" style={{ padding: '4px 8px' }}>
          MENU
        </button>
        <div>
          <div className="mobile-header-title">Trading Dashboard</div>
          <div className="mobile-header-subtitle">{currentPage.label}</div>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-muted" style={{ fontSize: 10 }}>{username}</span>
          <button onClick={logout} className="btn btn-ghost" style={{ padding: '2px 6px', fontSize: 10 }}>Exit</button>
        </div>
      </header>

      {sidebarOpen && <div className="sidebar-overlay lg:hidden" onClick={() => setSidebarOpen(false)} />}

      <aside className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <div>
            <div className="sidebar-logo">Trading Dashboard</div>
            <div className="sidebar-subtitle">{username}</div>
          </div>
          <button onClick={logout} className="btn btn-ghost" style={{ fontSize: 10, padding: '2px 6px' }}>Exit</button>
        </div>

        <div className="sidebar-nav">
          {NAV_ITEMS.map((item) => (
            <button
              key={item.page}
              onClick={() => navigateTo(item.page)}
              className={`nav-item ${page === item.page ? 'active' : ''}`}
            >
              <span className="nav-badge">{item.badge}</span>
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
            onClick={() => navigateTo('live-status')}
            className={`nav-item text-xs ${page === 'live-status' ? 'active' : ''}`}
          >
            <span className="nav-badge">LS</span>
            <span>Live Status</span>
          </button>
          <button
            onClick={() => navigateTo('broker-recon')}
            className={`nav-item text-xs ${page === 'broker-recon' ? 'active' : ''}`}
          >
            <span className="nav-badge">RC</span>
            <span>Broker Recon</span>
          </button>
        </div>
      </aside>

      <main className="main-content">
        <div className="workspace-bar">
          <div className="workspace-copy">
            <div className="workspace-kicker">Operator Console</div>
            <div className="workspace-title">{currentPage.label}</div>
            <div className="workspace-subtitle">
              {summaryLoading
                ? 'Syncing live runtime state...'
                : summaryError
                  ? summaryError
                  : `${runtime?.app_name || 'Trading runtime'} | ${runtime?.env || 'unknown env'} | refreshed ${lastRefreshed || 'just now'}`}
            </div>
          </div>

          <div className="workspace-actions">
            <button onClick={refreshSummary} className="btn btn-ghost" disabled={summaryLoading}>
              {summaryLoading ? 'SYNCING' : 'REFRESH'}
            </button>
            <button onClick={() => navigateTo('chat')} className="btn btn-accent">
              OPEN CHAT
            </button>
          </div>
        </div>

        <div className="workspace-summary-grid">
          <ShellMetric
            label="System"
            value={systemOnline ? 'ONLINE' : 'OFFLINE'}
            detail={`${runtime?.env || 'unknown'} mode`}
            tone={shellStatusTone}
          />
          <ShellMetric
            label="Watchlist"
            value={String(watchlistCount)}
            detail="active symbols"
            tone="accent"
          />
          <ShellMetric
            label="Strategies"
            value={`${strategyCount}`}
            detail={`${pendingStrategies} pending approval`}
            tone="warning"
          />
          <ShellMetric
            label="Agents"
            value={`${agentOnlineCount}/${Math.max(agentCards.length, 1)}`}
            detail="online services"
            tone={agentOnlineCount > 0 ? 'success' : 'warning'}
          />
          <ShellMetric
            label="Hermes"
            value={hermesOnline ? 'CONNECTED' : 'OFFLINE'}
            detail={`${runtime?.hermes?.backend || 'backend'} | ${runtime?.hermes?.model || 'model'}`}
            tone={hermesTone}
          />
        </div>

        <div className="workspace-quick-links">
          {QUICK_JUMPS.map((item) => (
            <button
              key={item.page}
              onClick={() => navigateTo(item.page)}
              className={`quick-link ${page === item.page ? 'active' : ''}`}
            >
              <span className="nav-badge">{item.badge}</span>
              <span>{item.label}</span>
            </button>
          ))}
        </div>

        <div className="workspace-status-row">
          <div className="status-chip status-chip-accent">
            <span className="status-chip-label">Event Bus</span>
            <span className="status-chip-value">{eventBusWorkers} workers</span>
            <span className="status-chip-note">queue {eventBusQueue}</span>
          </div>
          <div className="status-chip status-chip-neutral">
            <span className="status-chip-label">Research</span>
            <span className="status-chip-value">{runtime?.research_running ? 'ON' : 'OFF'}</span>
            <span className="status-chip-note">generation loop</span>
          </div>
          <div className="status-chip status-chip-neutral">
            <span className="status-chip-label">Validation</span>
            <span className="status-chip-value">{runtime?.validation_running ? 'ON' : 'OFF'}</span>
            <span className="status-chip-note">safety checks</span>
          </div>
          <div className="status-chip status-chip-neutral">
            <span className="status-chip-label">Registry</span>
            <span className="status-chip-value">{runtime?.registry_running ? 'ON' : 'OFF'}</span>
            <span className="status-chip-note">strategy storage</span>
          </div>
          <div className="status-chip status-chip-success">
            <span className="status-chip-label">Auto Approve</span>
            <span className="status-chip-value">{runtime?.auto_approve_strategies ? 'ENABLED' : 'MANUAL'}</span>
            <span className="status-chip-note">approval flow</span>
          </div>
        </div>

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
    <div className="flex items-center justify-center h-screen" style={{ background: 'var(--bg)' }}>
      <div className="modal-box p-8 w-full max-w-sm">
        <h1 className="text-xl font-bold mb-6 text-center" style={{ color: 'var(--accent)' }}>
          Trading Dashboard
        </h1>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm mb-1" style={{ color: 'var(--text-muted)' }}>Username</label>
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
            <label className="block text-sm mb-1" style={{ color: 'var(--text-muted)' }}>Password</label>
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
            style={{ padding: '8px 16px' }}
          >
            {loading ? '...' : 'Login'}
          </button>
        </form>
        <p className="text-muted mt-4 text-center" style={{ fontSize: 10 }}>Contact admin for credentials</p>
      </div>
    </div>
  );
}

function DashboardContent() {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen" style={{ background: 'var(--bg)' }}>
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-accent mx-auto mb-4" style={{ borderColor: 'var(--accent)' }} />
          <p className="text-muted">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <LoginPage />;
  }

  return <DashboardShell />;
}

function AppWrapper() {
  return (
    <AuthProvider>
      <DashboardContent />
    </AuthProvider>
  );
}

export default AppWrapper;
