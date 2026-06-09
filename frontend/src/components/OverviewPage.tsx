import React, { useEffect, useMemo, useState } from 'react';
import { apiFetch } from '../api';

type Portfolio = {
  total_value: number;
  total_pnl: number;
  total_pnl_pct: number;
  open_positions: number;
};

type RuntimeStatus = {
  running?: boolean;
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
};

type AgentCard = {
  agent_id: string;
  status: string;
  task: string;
  progress: number;
  detail?: string;
};

type WatchlistItem = {
  id: string;
  symbol: string;
  strategy_id: string;
  auto_trade: boolean;
  status: string;
  added_date?: string;
  last_checked?: string | null;
  last_signal?: string | null;
  last_signal_price?: number | null;
  quantity_to_buy?: number;
};

type TradeSignal = {
  id: string;
  symbol: string;
  approval_status: string;
  signal_price?: number;
  signal_time?: string;
  overall_score?: number;
  technical_score?: number;
  news_score?: number;
  fundamental_score?: number;
  risk_score?: number;
  approval_reason?: string;
};

function valueOrZero(value: unknown): number {
  const num = Number(value ?? 0);
  return Number.isFinite(num) ? num : 0;
}

function formatInr(value: number): string {
  return `INR ${value.toLocaleString('en-IN', { minimumFractionDigits: 0, maximumFractionDigits: 2 })}`;
}

export function OverviewPage() {
  const [watchlist, setWatchlist] = useState<WatchlistItem[]>([]);
  const [signals, setSignals] = useState<TradeSignal[]>([]);
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null);
  const [runtime, setRuntime] = useState<RuntimeStatus | null>(null);
  const [agents, setAgents] = useState<AgentCard[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshedAt, setRefreshedAt] = useState('');

  const refresh = async () => {
    setLoading(true);
    try {
      const safeFetch = async (url: string) => {
        try {
          return await apiFetch(url);
        } catch {
          return null;
        }
      };

      const [w, s, p, r, a] = await Promise.all([
        safeFetch('/api/watchlist'),
        safeFetch('/api/signals/pending'),
        safeFetch('/api/portfolio'),
        safeFetch('/api/runtime/status'),
        safeFetch('/api/agent-status'),
      ]);

      setWatchlist(Array.isArray(w) ? w : []);
      setSignals(Array.isArray(s) ? s : []);
      setPortfolio(p && typeof p === 'object' ? (p as Portfolio) : null);
      setRuntime(r && typeof r === 'object' ? (r as RuntimeStatus) : null);
      setAgents(Array.isArray(a) ? a : []);
      setRefreshedAt(new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }));
    } catch {
      // keep the existing screen on error
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refresh();
    const timer = setInterval(refresh, 10000);
    return () => clearInterval(timer);
  }, []);

  const activeWatchlist = useMemo(
    () => watchlist.filter((item) => item.status !== 'removed').length,
    [watchlist],
  );

  const pendingSignals = useMemo(
    () => signals.filter((signal) => signal.approval_status === 'pending').length,
    [signals],
  );

  const approvedSignals = useMemo(
    () => signals.filter((signal) => signal.approval_status === 'approved').length,
    [signals],
  );

  const avgScore = useMemo(() => {
    if (signals.length === 0) return 0;
    return signals.reduce((sum, signal) => sum + valueOrZero(signal.overall_score), 0) / signals.length;
  }, [signals]);

  const onlineAgents = useMemo(
    () => agents.filter((agent) => ['online', 'running', 'healthy'].includes(String(agent.status).toLowerCase())).length,
    [agents],
  );

  const strategyCounts = runtime?.strategy_counts ?? {};
  const topSignals = useMemo(
    () => [...signals].sort((a, b) => valueOrZero(b.overall_score) - valueOrZero(a.overall_score)).slice(0, 6),
    [signals],
  );

  const systemTone = runtime?.running ? 'text-green-400' : 'text-red-400';
  const hermesTone = runtime?.hermes?.online ? 'text-green-400' : 'text-yellow-300';

  return (
    <div className="p-6 bg-black text-white">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between mb-6">
        <div>
          <div className="text-xs uppercase tracking-[0.22em] text-gray-500 font-semibold">Overview</div>
          <h1 className="text-3xl font-bold mt-1">Command Center</h1>
          <p className="text-sm text-gray-400 mt-2 max-w-2xl">
            Live watchlist, strategy approvals, agent health, and portfolio state in one place.
          </p>
        </div>
        <button
          onClick={refresh}
          className="px-4 py-2 bg-gray-900 hover:bg-gray-800 rounded-lg text-sm font-semibold border border-gray-800"
        >
          {loading ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-5 gap-4 mb-6">
        <StatCard label="System" value={runtime?.running ? 'ONLINE' : 'OFFLINE'} detail={`${runtime?.env || 'unknown'} environment`} tone={systemTone} />
        <StatCard label="Watchlist" value={String(activeWatchlist)} detail="active symbols" tone="text-cyan-300" />
        <StatCard label="Signals" value={String(pendingSignals)} detail={`${approvedSignals} approved in queue`} tone="text-yellow-300" />
        <StatCard label="Agents" value={`${onlineAgents}/${Math.max(agents.length, 1)}`} detail="online services" tone="text-green-400" />
        <StatCard label="Hermes" value={runtime?.hermes?.online ? 'CONNECTED' : 'OFFLINE'} detail={`${runtime?.hermes?.backend || 'backend'} | ${runtime?.hermes?.model || 'model'}`} tone={hermesTone} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-6">
        <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
          <div className="text-xs uppercase tracking-[0.18em] text-gray-500 font-semibold">Strategy Pipeline</div>
          <div className="grid grid-cols-2 gap-3 mt-4 text-sm">
            <MiniMetric label="Generated" value={String(strategyCounts.generated ?? 0)} />
            <MiniMetric label="Pending" value={String(strategyCounts.pending_approval ?? 0)} />
            <MiniMetric label="Approved" value={String(strategyCounts.approved ?? 0)} />
            <MiniMetric label="Rejected" value={String(strategyCounts.rejected ?? 0)} />
          </div>
        </div>

        <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
          <div className="text-xs uppercase tracking-[0.18em] text-gray-500 font-semibold">Runtime</div>
          <div className="space-y-3 mt-4 text-sm">
            <HealthRow label="Research loop" value={runtime?.research_running ? 'ON' : 'OFF'} />
            <HealthRow label="Validation loop" value={runtime?.validation_running ? 'ON' : 'OFF'} />
            <HealthRow label="Registry loop" value={runtime?.registry_running ? 'ON' : 'OFF'} />
            <HealthRow label="Auto approve" value={runtime?.auto_approve_strategies ? 'ENABLED' : 'MANUAL'} />
          </div>
        </div>

        <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
          <div className="text-xs uppercase tracking-[0.18em] text-gray-500 font-semibold">Event Bus</div>
          <div className="mt-4 space-y-3 text-sm">
            <HealthRow label="Workers" value={String(runtime?.event_bus?.worker_count ?? 0)} />
            <HealthRow label="Queue" value={String(runtime?.event_bus?.queue_size ?? 0)} />
            <HealthRow label="Running" value={runtime?.event_bus?.running ? 'YES' : 'NO'} />
            <div className="text-xs text-gray-500">Last refresh: {refreshedAt || 'pending'}</div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <div className="xl:col-span-2 bg-gray-900 border border-gray-800 rounded-lg overflow-hidden">
          <div className="px-4 py-3 bg-gray-800/80 border-b border-gray-800 flex items-center justify-between gap-3">
            <div>
              <h2 className="text-lg font-semibold">Pending Actions</h2>
              <p className="text-xs text-gray-500">Signals waiting for human approval or auto-trading.</p>
            </div>
            <div className="text-xs text-gray-400">Avg score: {avgScore.toFixed(0)}%</div>
          </div>
          <div className="p-4 space-y-3">
            {topSignals.length === 0 ? (
              <div className="text-gray-400 text-sm">No pending signals right now.</div>
            ) : (
              topSignals.map((signal) => (
                <div key={signal.id} className="rounded-lg border border-gray-800 bg-black/20 p-4">
                  <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
                    <div>
                      <div className="flex items-center gap-3">
                        <div className="text-lg font-bold">{signal.symbol}</div>
                        <span className="px-2 py-1 rounded-full text-[10px] uppercase tracking-[0.18em] border border-gray-700 text-gray-300">
                          {signal.approval_status}
                        </span>
                      </div>
                      <div className="text-xs text-gray-500 mt-1">
                        {signal.approval_reason || 'Technical signal'}
                      </div>
                    </div>
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                      <SignalStat label="Price" value={`INR ${valueOrZero(signal.signal_price).toFixed(2)}`} />
                      <SignalStat label="Score" value={`${valueOrZero(signal.overall_score).toFixed(0)}%`} />
                      <SignalStat label="Tech" value={`${valueOrZero(signal.technical_score).toFixed(0)}`} />
                      <SignalStat label="Risk" value={`${valueOrZero(signal.risk_score).toFixed(0)}`} />
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="space-y-6">
          <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
            <div className="text-xs uppercase tracking-[0.18em] text-gray-500 font-semibold">System Health</div>
            <div className="mt-4 space-y-3 text-sm">
              <HealthRow label="Mode" value={runtime?.env || 'unknown'} />
              <HealthRow label="Watchlist size" value={String(runtime?.watchlist_count ?? activeWatchlist)} />
              <HealthRow label="Strategies" value={String(runtime?.strategy_count ?? 0)} />
              <HealthRow label="Hermes" value={runtime?.hermes?.online ? 'ONLINE' : 'OFFLINE'} valueClass={hermesTone} />
              <HealthRow label="Agents live" value={`${onlineAgents}/${Math.max(agents.length, 1)}`} />
            </div>
          </div>

          <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
            <div className="text-xs uppercase tracking-[0.18em] text-gray-500 font-semibold">Agent Health</div>
            <div className="mt-4 space-y-3">
              {agents.length === 0 ? (
                <div className="text-sm text-gray-400">No agent cards available yet.</div>
              ) : (
                agents.map((agent) => (
                  <div key={agent.agent_id} className="rounded-lg border border-gray-800 bg-black/20 p-3">
                    <div className="flex items-center justify-between gap-3">
                      <div className="text-sm font-semibold">{agent.agent_id}</div>
                      <span className={`text-xs uppercase tracking-[0.18em] ${statusTone(agent.status)}`}>{agent.status}</span>
                    </div>
                    <div className="text-xs text-gray-500 mt-1">{agent.task}</div>
                    <div className="mt-2 h-1.5 bg-gray-800 rounded-full overflow-hidden">
                      <div className="h-full bg-cyan-400" style={{ width: `${Math.max(0, Math.min(100, valueOrZero(agent.progress)))}%` }} />
                    </div>
                    {agent.detail ? <div className="text-[11px] text-gray-500 mt-2">{agent.detail}</div> : null}
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
        <div className="bg-gray-900 border border-gray-800 rounded-lg overflow-hidden">
          <div className="px-4 py-3 bg-gray-800/80 border-b border-gray-800">
            <h2 className="text-lg font-semibold">Watchlist Snapshot</h2>
          </div>
          <div className="p-4">
            {watchlist.filter((item) => item.status !== 'removed').length === 0 ? (
              <div className="text-sm text-gray-400">No watchlist items available.</div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr>
                      <th>Symbol</th>
                      <th>Strategy</th>
                      <th>Status</th>
                      <th className="text-right">Qty</th>
                    </tr>
                  </thead>
                  <tbody>
                    {watchlist.filter((item) => item.status !== 'removed').slice(0, 8).map((item) => (
                      <tr key={item.id}>
                        <td className="font-semibold">{item.symbol}</td>
                        <td>{item.strategy_id}</td>
                        <td>{item.auto_trade ? 'Auto' : 'Manual'}</td>
                        <td className="text-right">{item.quantity_to_buy ?? 1}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>

        <div className="bg-gray-900 border border-gray-800 rounded-lg overflow-hidden">
          <div className="px-4 py-3 bg-gray-800/80 border-b border-gray-800">
            <h2 className="text-lg font-semibold">Portfolio Snapshot</h2>
          </div>
          <div className="p-4">
            {portfolio ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="rounded-lg border border-gray-800 bg-black/20 p-4">
                  <div className="text-xs text-gray-500 uppercase tracking-[0.18em]">Total Value</div>
                  <div className="mt-2 text-2xl font-bold">{formatInr(valueOrZero(portfolio.total_value))}</div>
                </div>
                <div className="rounded-lg border border-gray-800 bg-black/20 p-4">
                  <div className="text-xs text-gray-500 uppercase tracking-[0.18em]">Open Positions</div>
                  <div className="mt-2 text-2xl font-bold">{valueOrZero(portfolio.open_positions)}</div>
                </div>
                <div className="rounded-lg border border-gray-800 bg-black/20 p-4">
                  <div className="text-xs text-gray-500 uppercase tracking-[0.18em]">PnL</div>
                  <div className={`mt-2 text-2xl font-bold ${valueOrZero(portfolio.total_pnl) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {formatInr(valueOrZero(portfolio.total_pnl))}
                  </div>
                </div>
                <div className="rounded-lg border border-gray-800 bg-black/20 p-4">
                  <div className="text-xs text-gray-500 uppercase tracking-[0.18em]">PnL %</div>
                  <div className={`mt-2 text-2xl font-bold ${valueOrZero(portfolio.total_pnl_pct) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {valueOrZero(portfolio.total_pnl_pct) >= 0 ? '+' : ''}{valueOrZero(portfolio.total_pnl_pct).toFixed(2)}%
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-sm text-gray-400">Portfolio data is not available yet.</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ label, value, detail, tone }: { label: string; value: string; detail: string; tone: string }) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
      <div className="text-xs uppercase tracking-[0.18em] text-gray-500 font-semibold">{label}</div>
      <div className={`text-2xl font-bold mt-2 ${tone}`}>{value}</div>
      <div className="text-xs text-gray-400 mt-1">{detail}</div>
    </div>
  );
}

function MiniMetric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-gray-800 bg-black/20 p-3">
      <div className="text-xs uppercase tracking-[0.18em] text-gray-500">{label}</div>
      <div className="mt-1 text-xl font-bold">{value}</div>
    </div>
  );
}

function HealthRow({ label, value, valueClass = 'text-white' }: { label: string; value: string; valueClass?: string }) {
  return (
    <div className="flex items-center justify-between gap-4">
      <span className="text-gray-400">{label}</span>
      <span className={`font-semibold ${valueClass}`}>{value}</span>
    </div>
  );
}

function SignalStat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-gray-800 bg-black/20 px-3 py-2">
      <div className="text-[10px] uppercase tracking-[0.18em] text-gray-500">{label}</div>
      <div className="mt-1 text-sm font-semibold">{value}</div>
    </div>
  );
}

function statusTone(status: string): string {
  const value = String(status || '').toLowerCase();
  if (['online', 'running', 'healthy'].includes(value)) return 'text-green-400';
  if (['processing', 'starting'].includes(value)) return 'text-cyan-300';
  if (['warning', 'paused', 'idle'].includes(value)) return 'text-yellow-300';
  return 'text-red-300';
}
