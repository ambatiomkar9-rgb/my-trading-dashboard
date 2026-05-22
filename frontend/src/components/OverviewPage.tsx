import React, { useEffect, useMemo, useState } from 'react';

const API_URL = '';

type Portfolio = {
  total_value: number;
  total_pnl: number;
  total_pnl_pct: number;
  open_positions: number;
};

type SystemHealth = {
  timestamp: string;
  ollama_status: string;
  broker_status: string;
  agents_online: number;
  alert_cooldown_seconds: number;
};

type WatchlistItem = {
  id: string;
  symbol: string;
  strategy_id: string;
  auto_trade: boolean;
  status: string;
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
};

export function OverviewPage() {
  const [watchlist, setWatchlist] = useState<WatchlistItem[]>([]);
  const [signals, setSignals] = useState<TradeSignal[]>([]);
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null);
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [loading, setLoading] = useState(true);

  const safeJson = async (res: Response) => {
    const text = await res.text();
    try {
      return text ? JSON.parse(text) : {};
    } catch {
      return { raw: text };
    }
  };

  const refresh = async () => {
    setLoading(true);
    try {
      const [wRes, sRes, pRes, hRes] = await Promise.all([
        fetch(`${API_URL}/api/watchlist`),
        fetch(`${API_URL}/api/signals/pending`),
        fetch(`${API_URL}/api/portfolio`),
        fetch(`${API_URL}/api/system/health`),
      ]);
      const [w, s, p, h] = await Promise.all([safeJson(wRes), safeJson(sRes), safeJson(pRes), safeJson(hRes)]);
      setWatchlist(Array.isArray(w) ? w : []);
      setSignals(Array.isArray(s) ? s : []);
      setPortfolio(p && typeof p === 'object' ? (p as Portfolio) : null);
      setHealth(h && typeof h === 'object' ? (h as SystemHealth) : null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refresh();
    const t = setInterval(refresh, 10000);
    return () => clearInterval(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const metrics = useMemo(() => {
    const pending = signals.length;
    return {
      watchCount: watchlist.filter((i) => i.status !== 'removed').length,
      pendingSignals: pending,
    };
  }, [signals, watchlist]);

  return (
    <div className="p-6 bg-black text-white">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold">Overview</h1>
        <button onClick={refresh} className="px-3 py-2 bg-gray-900 hover:bg-gray-800 rounded text-sm font-semibold">
          {loading ? 'Refreshing…' : 'Refresh'}
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 mb-8">
        <div className="bg-gray-900 p-4 rounded border border-gray-800">
          <div className="text-gray-400 text-sm">Active Watches</div>
          <div className="text-2xl font-bold">{metrics.watchCount}</div>
        </div>
        <div className="bg-gray-900 p-4 rounded border border-gray-800">
          <div className="text-gray-400 text-sm">Pending Signals</div>
          <div className="text-2xl font-bold text-yellow-300">{metrics.pendingSignals}</div>
        </div>
        <div className="bg-gray-900 p-4 rounded border border-gray-800">
          <div className="text-gray-400 text-sm">Portfolio Value</div>
          <div className="text-2xl font-bold">₹{(portfolio?.total_value || 0).toFixed(0)}</div>
        </div>
        <div className="bg-gray-900 p-4 rounded border border-gray-800">
          <div className="text-gray-400 text-sm">Total P&amp;L</div>
          <div className={`text-2xl font-bold ${(portfolio?.total_pnl || 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {(portfolio?.total_pnl || 0) >= 0 ? '+' : ''}
            {(portfolio?.total_pnl || 0).toFixed(0)} ({(portfolio?.total_pnl_pct || 0).toFixed(2)}%)
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-gray-900 rounded-lg border border-gray-800 overflow-hidden">
          <div className="px-4 py-3 bg-gray-800 font-semibold">Action Required</div>
          <div className="p-4">
            {signals.length === 0 ? (
              <div className="text-gray-400 text-sm">No pending signals right now.</div>
            ) : (
              <div className="space-y-3">
                {signals.slice(0, 5).map((s) => (
                  <div key={s.id} className="p-3 rounded bg-black/30 border border-gray-800">
                    <div className="flex items-center justify-between">
                      <div className="font-semibold">{s.symbol}</div>
                      <div className="text-xs text-gray-400">{s.approval_status}</div>
                    </div>
                    <div className="text-sm text-gray-300 mt-1">
                      Price: ₹{Number(s.signal_price || 0).toFixed(2)} | Score: {Number(s.overall_score || 0).toFixed(0)}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="bg-gray-900 rounded-lg border border-gray-800 overflow-hidden">
          <div className="px-4 py-3 bg-gray-800 font-semibold">System Health</div>
          <div className="p-4 space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-400">Agents Online</span>
              <span className="font-semibold">{health?.agents_online ?? 0}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Broker Status</span>
              <span className="font-semibold">{health?.broker_status ?? 'unknown'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Ollama Status</span>
              <span className="font-semibold">{health?.ollama_status ?? 'unknown'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Telegram Cooldown</span>
              <span className="font-semibold">{health?.alert_cooldown_seconds ?? 60}s</span>
            </div>
            <div className="text-xs text-gray-500 mt-3">Updated: {health?.timestamp || '—'}</div>
          </div>
        </div>
      </div>
    </div>
  );
}

