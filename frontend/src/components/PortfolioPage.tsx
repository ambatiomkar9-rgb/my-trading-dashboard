import React, { useEffect, useState } from 'react';

const API_URL = '';

type Portfolio = {
  total_value: number;
  total_pnl: number;
  total_pnl_pct: number;
  open_positions: number;
};

export function PortfolioPage() {
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null);
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
      const res = await fetch(`${API_URL}/api/portfolio`);
      const data = await safeJson(res);
      setPortfolio(data && typeof data === 'object' ? (data as Portfolio) : null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refresh();
    const t = setInterval(refresh, 10000);
    return () => clearInterval(t);
  }, []);

  return (
    <div className="p-6 bg-black text-white">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold">Portfolio</h1>
        <button onClick={refresh} className="px-3 py-2 bg-gray-900 hover:bg-gray-800 rounded text-sm font-semibold">
          {loading ? 'Refreshing…' : 'Refresh'}
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <div className="bg-gray-900 border border-gray-800 rounded p-4">
          <div className="text-gray-400 text-sm">Total Value</div>
          <div className="text-2xl font-bold">₹{Number(portfolio?.total_value || 0).toFixed(0)}</div>
        </div>
        <div className="bg-gray-900 border border-gray-800 rounded p-4">
          <div className="text-gray-400 text-sm">Open Positions</div>
          <div className="text-2xl font-bold">{portfolio?.open_positions ?? 0}</div>
        </div>
        <div className="bg-gray-900 border border-gray-800 rounded p-4">
          <div className="text-gray-400 text-sm">PnL</div>
          <div className={`text-2xl font-bold ${(portfolio?.total_pnl || 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {(portfolio?.total_pnl || 0) >= 0 ? '+' : ''}
            {Number(portfolio?.total_pnl || 0).toFixed(0)}
          </div>
        </div>
        <div className="bg-gray-900 border border-gray-800 rounded p-4">
          <div className="text-gray-400 text-sm">PnL %</div>
          <div className={`text-2xl font-bold ${(portfolio?.total_pnl_pct || 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {(portfolio?.total_pnl_pct || 0) >= 0 ? '+' : ''}
            {Number(portfolio?.total_pnl_pct || 0).toFixed(2)}%
          </div>
        </div>
      </div>

      <div className="mt-6 text-gray-400 text-sm">
        This page uses `GET /api/portfolio` which is derived from active positions. If you want true broker balances and
        holdings, we can wire the broker SDK next.
      </div>
    </div>
  );
}

