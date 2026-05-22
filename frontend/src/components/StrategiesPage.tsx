import React, { useEffect, useMemo, useState } from 'react';
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

const API_URL = '';

interface Strategy {
  id: string;
  name: string;
  symbol: string;
  timeframe: string;
  status: 'running' | 'paused' | 'backtested';
  pnl: number;
  win_rate: number;
  total_trades: number;
  equity_curve: Array<{ date: string; value: number }>;
}

export function StrategiesPage() {
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [selected, setSelected] = useState<Strategy | null>(null);
  const [showNewForm, setShowNewForm] = useState(false);
  const [creating, setCreating] = useState(false);
  const [newStrategy, setNewStrategy] = useState({
    name: '',
    symbol: 'INFY',
    timeframe: '4h',
    status: 'paused' as 'running' | 'paused' | 'backtested',
    entry_rule: '',
    exit_rule: '',
  });
  const [pineLoading, setPineLoading] = useState(false);
  const [pineScript, setPineScript] = useState('');
  const [pineError, setPineError] = useState<string | null>(null);

  useEffect(() => {
    fetchStrategies();
  }, []);

  const safeJson = async (res: Response) => {
    const text = await res.text();
    try {
      return text ? JSON.parse(text) : {};
    } catch {
      return { raw: text };
    }
  };

  const fetchStrategies = async () => {
    try {
      const res = await fetch(`${API_URL}/strategies`);
      const data = await safeJson(res);
      const list = Array.isArray(data) ? (data as Strategy[]) : [];
      setStrategies(list);
      setSelected(list[0] || null);
    } catch (error) {
      console.error('Error fetching strategies:', error);
      setStrategies([]);
      setSelected(null);
    }
  };

  const sortedStrategies = useMemo(() => {
    return [...strategies].sort((a, b) => (b.pnl || 0) - (a.pnl || 0));
  }, [strategies]);

  const handleDelete = async (id: string) => {
    // eslint-disable-next-line no-restricted-globals
    if (!confirm('Delete this strategy?')) return;
    try {
      await fetch(`${API_URL}/strategy/${encodeURIComponent(id)}`, { method: 'DELETE' });
      await fetchStrategies();
      setSelected(null);
    } catch (error) {
      console.error('Error deleting strategy:', error);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    const name = newStrategy.name.trim();
    const symbol = newStrategy.symbol.trim().toUpperCase();
    if (!name || !symbol) {
      alert('Name and symbol are required');
      return;
    }
    setCreating(true);
    try {
      const res = await fetch(`${API_URL}/strategy/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name,
          symbol,
          timeframe: newStrategy.timeframe,
          status: newStrategy.status,
          entry_rule: newStrategy.entry_rule,
          exit_rule: newStrategy.exit_rule,
        }),
      });
      const data = await safeJson(res);
      if (!res.ok) throw new Error(String(data?.detail || data?.raw || `HTTP ${res.status}`));
      setShowNewForm(false);
      setNewStrategy({ name: '', symbol: 'INFY', timeframe: '4h', status: 'paused', entry_rule: '', exit_rule: '' });
      await fetchStrategies();
    } catch (err: any) {
      alert(err?.message || 'Failed to create strategy');
    } finally {
      setCreating(false);
    }
  };

  const generatePineScript = async () => {
    if (!selected) return;
    setPineError(null);
    setPineLoading(true);
    setPineScript('');
    try {
      const res = await fetch(`${API_URL}/strategy/pinescript/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: `${selected.name} (${selected.symbol})` }),
      });
      const data = await safeJson(res);
      if (!res.ok) throw new Error(String(data?.detail || data?.raw || `HTTP ${res.status}`));
      setPineScript(String(data?.script || ''));
    } catch (e: any) {
      setPineError(e?.message || 'Failed to generate PineScript');
    } finally {
      setPineLoading(false);
    }
  };

  return (
    <div className="p-6 bg-black text-white">
      <div className="flex flex-col gap-3 sm:flex-row sm:justify-between sm:items-center mb-6">
        <h1 className="text-3xl font-bold">Trading Strategies</h1>
        <button
          onClick={() => setShowNewForm(!showNewForm)}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded font-semibold"
        >
          + New Strategy
        </button>
      </div>

      {showNewForm ? (
        <form onSubmit={handleCreate} className="mb-8 bg-gray-900 border border-gray-800 rounded-lg p-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-gray-300 mb-2">Name</label>
              <input
                value={newStrategy.name}
                onChange={(e) => setNewStrategy({ ...newStrategy, name: e.target.value })}
                className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white"
                placeholder="EMA Cross"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-300 mb-2">Symbol</label>
              <input
                value={newStrategy.symbol}
                onChange={(e) => setNewStrategy({ ...newStrategy, symbol: e.target.value })}
                className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white"
                placeholder="INFY"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-300 mb-2">Timeframe</label>
              <select
                value={newStrategy.timeframe}
                onChange={(e) => setNewStrategy({ ...newStrategy, timeframe: e.target.value })}
                className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white"
              >
                <option value="1h">1h</option>
                <option value="4h">4h</option>
                <option value="1d">1d</option>
              </select>
            </div>
            <div>
              <label className="block text-sm text-gray-300 mb-2">Status</label>
              <select
                value={newStrategy.status}
                onChange={(e) => setNewStrategy({ ...newStrategy, status: e.target.value as any })}
                className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white"
              >
                <option value="paused">paused</option>
                <option value="running">running</option>
                <option value="backtested">backtested</option>
              </select>
            </div>
            <div className="sm:col-span-2">
              <label className="block text-sm text-gray-300 mb-2">Entry Rule / Buy Conditions (text or JSON)</label>
              <textarea
                value={newStrategy.entry_rule}
                onChange={(e) => setNewStrategy({ ...newStrategy, entry_rule: e.target.value })}
                className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white min-h-[84px]"
                placeholder='Example: {"rsi":{"below":30},"trend":"bullish"}'
              />
            </div>
            <div className="sm:col-span-2">
              <label className="block text-sm text-gray-300 mb-2">Exit Rule / Sell Conditions (text or JSON)</label>
              <textarea
                value={newStrategy.exit_rule}
                onChange={(e) => setNewStrategy({ ...newStrategy, exit_rule: e.target.value })}
                className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white min-h-[84px]"
                placeholder='Example: {"rsi":{"above":70}}'
              />
            </div>
          </div>

          <div className="mt-4 flex items-center justify-end gap-2">
            <button
              type="button"
              onClick={() => setShowNewForm(false)}
              className="px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded font-semibold"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={creating}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 rounded font-semibold"
            >
              {creating ? 'Creating...' : 'Create Strategy'}
            </button>
          </div>
        </form>
      ) : null}

      <section className="mb-8">
        <div className="bg-gray-900 rounded-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-800">
                <tr>
                  <th className="px-4 py-3 text-left">Name</th>
                  <th className="px-4 py-3 text-left">Symbol</th>
                  <th className="px-4 py-3 text-left">Timeframe</th>
                  <th className="px-4 py-3 text-left">Status</th>
                  <th className="px-4 py-3 text-right">P&amp;L</th>
                  <th className="px-4 py-3 text-right">Win%</th>
                  <th className="px-4 py-3 text-center">Actions</th>
                </tr>
              </thead>
              <tbody>
                {sortedStrategies.map((strat) => (
                  <tr
                    key={strat.id}
                    className={`border-b border-gray-800 cursor-pointer hover:bg-gray-800/60 ${
                      selected?.id === strat.id ? 'bg-gray-800/60' : ''
                    }`}
                    onClick={() => setSelected(strat)}
                  >
                    <td className="px-4 py-3 font-semibold">{strat.name}</td>
                    <td className="px-4 py-3">{strat.symbol}</td>
                    <td className="px-4 py-3">{strat.timeframe}</td>
                    <td className="px-4 py-3">
                      <span
                        className={`px-2 py-1 rounded text-sm ${
                          strat.status === 'running'
                            ? 'bg-green-900 text-green-400'
                            : strat.status === 'paused'
                              ? 'bg-yellow-900 text-yellow-400'
                              : 'bg-gray-800 text-gray-300'
                        }`}
                      >
                        {strat.status}
                      </span>
                    </td>
                    <td className={`px-4 py-3 text-right font-semibold ${strat.pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {strat.pnl >= 0 ? '+' : ''}
                      {Number(strat.pnl).toFixed(0)}
                    </td>
                    <td className="px-4 py-3 text-right">{strat.win_rate}%</td>
                    <td className="px-4 py-3 text-center">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDelete(strat.id);
                        }}
                        className="px-2 py-1 bg-red-600 rounded text-sm hover:bg-red-700"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {selected ? (
        <section>
          <h2 className="text-xl font-bold mb-4">Strategy Details: {selected.name}</h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
            <div className="bg-gray-900 p-4 rounded">
              <p className="text-gray-400 text-sm">Total Trades</p>
              <p className="text-2xl font-bold">{selected.total_trades}</p>
            </div>
            <div className="bg-gray-900 p-4 rounded">
              <p className="text-gray-400 text-sm">Win Rate</p>
              <p className="text-2xl font-bold text-green-400">{selected.win_rate}%</p>
            </div>
          </div>

          <div className="bg-gray-900 p-4 rounded mb-6">
            <h3 className="text-lg font-semibold mb-4">Equity Curve</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={selected.equity_curve || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                <XAxis dataKey="date" stroke="#888" />
                <YAxis stroke="#888" />
                <Tooltip contentStyle={{ backgroundColor: '#1a1a1a', border: '1px solid #444' }} />
                <Line type="monotone" dataKey="value" stroke="#3b82f6" dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-gray-900 p-4 rounded">
            <div className="flex flex-col gap-3 sm:flex-row sm:justify-between sm:items-center mb-3">
              <h3 className="text-lg font-semibold">PineScript Generator</h3>
              <button
                onClick={generatePineScript}
                disabled={pineLoading}
                className="px-3 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 rounded text-sm font-semibold"
              >
                {pineLoading ? 'Generating...' : 'Generate PineScript'}
              </button>
            </div>
            {pineError ? <div className="text-red-400 text-sm mb-2">{pineError}</div> : null}
            {pineScript ? (
              <pre className="bg-black/40 border border-gray-800 rounded p-3 text-xs overflow-x-auto whitespace-pre">
                {pineScript}
              </pre>
            ) : (
              <div className="text-gray-400 text-sm">Click "Generate PineScript" to create a starter strategy.</div>
            )}
          </div>
        </section>
      ) : null}
    </div>
  );
}
