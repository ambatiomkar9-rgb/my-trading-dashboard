import React, { useEffect, useState } from 'react';
import { apiFetch } from '../api';

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

export function WatchlistPage() {
  const [items, setItems] = useState<WatchlistItem[]>([]);
  const [symbol, setSymbol] = useState('');
  const [strategyId, setStrategyId] = useState('default');
  const [autoTrade, setAutoTrade] = useState(false);
  const [quantity, setQuantity] = useState(1);
  const [loading, setLoading] = useState(true);

  const refresh = async () => {
    setLoading(true);
    try {
      const data = await apiFetch('/api/watchlist');
      setItems(Array.isArray(data) ? data : []);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refresh();
  }, []);

  const add = async () => {
    const s = symbol.trim().toUpperCase();
    if (!s) return;
    try {
      const data = await apiFetch('/api/watchlist/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ symbol: s, strategy_id: strategyId, auto_trade: autoTrade, quantity_to_buy: quantity }),
      });
      if (data?.detail || data?.raw) {
        alert(data.detail || data.raw);
        return;
      }
      setSymbol('');
      await refresh();
    } catch (err: any) {
      alert(err?.message || 'Failed to add');
    }
  };

  const remove = async (sym: string) => {
    try {
      await apiFetch('/api/watchlist/remove', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ symbol: sym }),
      });
      await refresh();
    } catch (err: any) {
      alert(err?.message || 'Failed to remove');
    }
  };

  return (
    <div className="p-6 bg-black text-white">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold">Watchlist</h1>
        <button onClick={refresh} className="px-3 py-2 bg-gray-900 hover:bg-gray-800 rounded text-sm font-semibold">
          {loading ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-lg p-4 mb-6">
        <div className="grid grid-cols-1 sm:grid-cols-5 gap-3">
          <div className="sm:col-span-2">
            <label className="block text-sm text-gray-400 mb-1">Symbol</label>
            <input value={symbol} onChange={(e) => setSymbol(e.target.value)} className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white" placeholder="INFY / BTC-USD / RELIANCE" />
          </div>
          <div>
            <label className="block text-sm text-gray-400 mb-1">Strategy</label>
            <input value={strategyId} onChange={(e) => setStrategyId(e.target.value)} className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white" placeholder="default" />
          </div>
          <div>
            <label className="block text-sm text-gray-400 mb-1">Qty</label>
            <input type="number" value={quantity} min={1} onChange={(e) => setQuantity(parseInt(e.target.value || '1', 10))} className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white" />
          </div>
          <div className="flex items-end gap-2">
            <label className="flex items-center gap-2 text-sm text-gray-300">
              <input type="checkbox" checked={autoTrade} onChange={(e) => setAutoTrade(e.target.checked)} />
              Auto trade
            </label>
            <button onClick={add} className="ml-auto px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded font-semibold">Add</button>
          </div>
        </div>
        <div className="text-xs text-gray-500 mt-3">
          Watchlist is stored in the dashboard database.
        </div>
      </div>

      <div className="bg-gray-900 rounded-lg overflow-hidden border border-gray-800">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-800 border-b border-gray-700">
              <tr>
                <th className="px-4 py-3 text-left">Symbol</th>
                <th className="px-4 py-3 text-left">Strategy</th>
                <th className="px-4 py-3 text-left">Auto</th>
                <th className="px-4 py-3 text-right">Qty</th>
                <th className="px-4 py-3 text-left">Last Signal</th>
                <th className="px-4 py-3 text-center">Action</th>
              </tr>
            </thead>
            <tbody>
              {items.filter((i) => i.status !== 'removed').map((i) => (
                <tr key={i.id} className="border-b border-gray-800 hover:bg-gray-800/60">
                  <td className="px-4 py-3 font-semibold">{i.symbol}</td>
                  <td className="px-4 py-3">{i.strategy_id}</td>
                  <td className="px-4 py-3">{i.auto_trade ? 'Yes' : 'No'}</td>
                  <td className="px-4 py-3 text-right">{i.quantity_to_buy ?? 1}</td>
                  <td className="px-4 py-3 text-gray-300">
                    {i.last_signal ? `${i.last_signal} @ ₹${Number(i.last_signal_price || 0).toFixed(2)}` : '—'}
                  </td>
                  <td className="px-4 py-3 text-center">
                    <button onClick={() => remove(i.symbol)} className="px-3 py-1 bg-red-600 hover:bg-red-700 rounded text-sm">Remove</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {items.filter((i) => i.status !== 'removed').length === 0 && !loading ? (
          <div className="p-6 text-center text-gray-400">No watchlist items</div>
        ) : null}
      </div>
    </div>
  );
}
