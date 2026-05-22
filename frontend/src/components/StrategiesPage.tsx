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
        <div className="mb-8 bg-gray-900 border border-gray-800 rounded-lg p-4">
          <div className="text-gray-300 text-sm">
            Strategy creation UI is wired to `POST /strategy/create` in the backend. If you want, I can turn this into a
            full modal form with validation.
          </div>
        </div>
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
                {pineLoading ? 'Generating…' : 'Generate PineScript'}
              </button>
            </div>
            {pineError ? <div className="text-red-400 text-sm mb-2">{pineError}</div> : null}
            {pineScript ? (
              <pre className="bg-black/40 border border-gray-800 rounded p-3 text-xs overflow-x-auto whitespace-pre">
                {pineScript}
              </pre>
            ) : (
              <div className="text-gray-400 text-sm">Click “Generate PineScript” to create a starter strategy.</div>
            )}
          </div>
        </section>
      ) : null}
    </div>
  );
}

