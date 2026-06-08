import React, { useEffect, useMemo, useState } from 'react';
import { apiFetch } from '../api';

interface ScreenerResult {
  rank: number;
  symbol: string;
  price: number;
  change_pct: number;
  pnl_pct: number;
  signal: 'buy' | 'sell' | 'hold';
  timeframe: string;
}

export function StockScreenerPage() {
  const [results, setResults] = useState<ScreenerResult[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchScreenerResults();
    const interval = setInterval(fetchScreenerResults, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchScreenerResults = async () => {
    try {
      const data = await apiFetch('/screener');
      setResults(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Error fetching screener:', error);
    } finally {
      setLoading(false);
    }
  };

  const signalColor = (signal: string) => {
    switch (signal) {
      case 'buy': return 'text-green-400 bg-green-900';
      case 'sell': return 'text-red-400 bg-red-900';
      default: return 'text-gray-300 bg-gray-800';
    }
  };

  const summary = useMemo(() => {
    const buy = results.filter((r) => r.signal === 'buy').length;
    const sell = results.filter((r) => r.signal === 'sell').length;
    const hold = results.filter((r) => r.signal === 'hold').length;
    return { buy, sell, hold };
  }, [results]);

  return (
    <div className="p-6 bg-black text-white">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold">Stock Screener</h1>
        {loading ? <div className="text-gray-400 text-sm">Loading...</div> : null}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
        <div className="bg-green-900 p-4 rounded">
          <p className="text-green-200 text-sm">Buy Signals</p>
          <p className="text-2xl font-bold">{summary.buy}</p>
        </div>
        <div className="bg-red-900 p-4 rounded">
          <p className="text-red-200 text-sm">Sell Signals</p>
          <p className="text-2xl font-bold">{summary.sell}</p>
        </div>
        <div className="bg-gray-900 p-4 rounded">
          <p className="text-gray-300 text-sm">Hold</p>
          <p className="text-2xl font-bold">{summary.hold}</p>
        </div>
      </div>

      <div className="bg-gray-900 rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-800 border-b border-gray-700">
              <tr>
                <th className="px-4 py-3 text-left">#</th>
                <th className="px-4 py-3 text-left">Symbol</th>
                <th className="px-4 py-3 text-right">Price</th>
                <th className="px-4 py-3 text-right">Change%</th>
                <th className="px-4 py-3 text-right">P&amp;L%</th>
                <th className="px-4 py-3 text-left">Signal</th>
                <th className="px-4 py-3 text-left">TF</th>
                <th className="px-4 py-3 text-center">Action</th>
              </tr>
            </thead>
            <tbody>
              {results.map((result) => (
                <tr key={result.symbol} className="border-b border-gray-800 hover:bg-gray-800/60">
                  <td className="px-4 py-3 font-semibold">{result.rank}</td>
                  <td className="px-4 py-3 font-bold">{result.symbol}</td>
                  <td className="px-4 py-3 text-right">₹{Number(result.price).toFixed(2)}</td>
                  <td className={`px-4 py-3 text-right ${result.change_pct >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {result.change_pct >= 0 ? '+' : ''}{Number(result.change_pct).toFixed(2)}%
                  </td>
                  <td className={`px-4 py-3 text-right ${result.pnl_pct >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {result.pnl_pct >= 0 ? '+' : ''}{Number(result.pnl_pct).toFixed(2)}%
                  </td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-1 rounded text-sm font-semibold ${signalColor(result.signal)}`}>
                      {result.signal.toUpperCase()}
                    </span>
                  </td>
                  <td className="px-4 py-3">{result.timeframe}</td>
                  <td className="px-4 py-3 text-center">
                    <button className="px-2 py-1 bg-blue-600 rounded text-sm hover:bg-blue-700">Analyze</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {results.length === 0 && !loading ? (
          <div className="p-6 text-center text-gray-400">No screener results</div>
        ) : null}
      </div>
    </div>
  );
}

export const StockScreener = StockScreenerPage;
