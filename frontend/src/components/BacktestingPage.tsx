import React, { useState } from 'react';
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { apiFetch } from '../api';

interface BacktestResult {
  total_trades: number;
  win_rate: number;
  profit_factor: number;
  sharpe: number;
  max_dd: number;
  net_pnl: number;
  equity_curve: Array<{ date: string; value: number }>;
  trades: Array<{ entry_date: string; exit_date: string; entry_price: number; profit: number }>;
}

export function BacktestingPage() {
  const [config, setConfig] = useState({
    strategy: 'ema_cross',
    symbol: 'INFY',
    timeframe: '4h',
    from_date: '2026-01-01',
    to_date: '2026-05-21',
    capital: '100000',
  });

  const [result, setResult] = useState<BacktestResult | null>(null);
  const [loading, setLoading] = useState(false);

  const handleRunBacktest = async () => {
    setLoading(true);
    try {
      const data = await apiFetch('/backtest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config),
      });
      setResult(data as BacktestResult);
    } catch (error) {
      console.error('Backtest error:', error);
      alert('Backtest failed');
    } finally {
      setLoading(false);
    }
  };

  const handleExport = () => {
    if (!result) return;
    const csv = [
      ['Entry Date', 'Exit Date', 'Entry Price', 'Profit'],
      ...(result.trades || []).map((t) => [t.entry_date, t.exit_date, String(t.entry_price), String(t.profit)]),
    ]
      .map((row) => row.join(','))
      .join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `backtest_${config.symbol}.csv`;
    a.click();
  };

  return (
    <div className="p-6 bg-black text-white">
      <h1 className="text-3xl font-bold mb-6">Backtesting Engine</h1>

      <section className="mb-8 bg-gray-900 p-6 rounded-lg">
        <h2 className="text-xl font-bold mb-4">Configuration</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm mb-2">Strategy</label>
            <select value={config.strategy} onChange={(e) => setConfig({ ...config, strategy: e.target.value })} className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2">
              <option value="ema_cross">EMA Crossover</option>
              <option value="rsi_oversold">RSI Oversold</option>
              <option value="macd_momentum">MACD Momentum</option>
            </select>
          </div>
          <div>
            <label className="block text-sm mb-2">Symbol</label>
            <input type="text" value={config.symbol} onChange={(e) => setConfig({ ...config, symbol: e.target.value })} className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2" />
          </div>
          <div>
            <label className="block text-sm mb-2">From Date</label>
            <input type="date" value={config.from_date} onChange={(e) => setConfig({ ...config, from_date: e.target.value })} className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2" />
          </div>
          <div>
            <label className="block text-sm mb-2">To Date</label>
            <input type="date" value={config.to_date} onChange={(e) => setConfig({ ...config, to_date: e.target.value })} className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2" />
          </div>
        </div>
        <button onClick={handleRunBacktest} disabled={loading} className="mt-6 w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white font-bold py-2 rounded">
          {loading ? 'Running...' : 'Run Backtest'}
        </button>
      </section>

      {result ? (
        <section>
          <h2 className="text-xl font-bold mb-4">Results</h2>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
            <div className="bg-gray-900 p-4 rounded">
              <p className="text-gray-400 text-sm">Total Trades</p>
              <p className="text-2xl font-bold">{result.total_trades}</p>
            </div>
            <div className="bg-gray-900 p-4 rounded">
              <p className="text-gray-400 text-sm">Win Rate</p>
              <p className="text-2xl font-bold text-green-400">{result.win_rate}%</p>
            </div>
            <div className="bg-gray-900 p-4 rounded">
              <p className="text-gray-400 text-sm">Net P&amp;L</p>
              <p className={`text-2xl font-bold ${result.net_pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                {result.net_pnl >= 0 ? '+' : ''}{Number(result.net_pnl).toFixed(0)}
              </p>
            </div>
          </div>

          <div className="bg-gray-900 p-4 rounded mb-6">
            <h3 className="text-lg font-semibold mb-4">Equity Curve</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={result.equity_curve || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                <XAxis dataKey="date" stroke="#888" />
                <YAxis stroke="#888" />
                <Tooltip contentStyle={{ backgroundColor: '#1a1a1a' }} />
                <Line type="monotone" dataKey="value" stroke="#3b82f6" dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-gray-900 p-4 rounded">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Trade List</h3>
              <button onClick={handleExport} className="px-3 py-1 bg-green-600 hover:bg-green-700 rounded text-sm">Export CSV</button>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="border-b border-gray-700">
                  <tr>
                    <th className="px-2 py-2 text-left">Entry Date</th>
                    <th className="px-2 py-2 text-left">Exit Date</th>
                    <th className="px-2 py-2 text-right">Entry Price</th>
                    <th className="px-2 py-2 text-right">Profit</th>
                  </tr>
                </thead>
                <tbody>
                  {(result.trades || []).slice(0, 10).map((trade, idx) => (
                    <tr key={idx} className="border-b border-gray-800">
                      <td className="px-2 py-2">{trade.entry_date}</td>
                      <td className="px-2 py-2">{trade.exit_date}</td>
                      <td className="px-2 py-2 text-right">₹{trade.entry_price}</td>
                      <td className={`px-2 py-2 text-right ${trade.profit >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                        {trade.profit >= 0 ? '+' : ''}{trade.profit}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </section>
      ) : null}
    </div>
  );
}
