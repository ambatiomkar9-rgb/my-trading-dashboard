import React, { useEffect, useState } from 'react';
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis, BarChart, Bar } from 'recharts';
import { api } from '../api';

interface Trade {
  id: string;
  symbol: string;
  side: string;
  qty: number;
  price: number;
  pnl?: number;
  status: string;
  timestamp: string;
}

interface PerformanceMetrics {
  total_trades: number;
  win_rate: number;
  total_pnl: number;
  avg_pnl: number;
  max_win: number;
  max_loss: number;
  profit_factor: number;
  sharpe_ratio: number;
  win_streak: number;
  loss_streak: number;
}

export function PerformancePage() {
  const [trades, setTrades] = useState<Trade[]>([]);
  const [loading, setLoading] = useState(true);
  const [metrics, setMetrics] = useState<PerformanceMetrics | null>(null);
  const [pnlCurve, setPnlCurve] = useState<Array<{ date: string; pnl: number; cumulative: number }>>([]);

  useEffect(() => {
    fetchTrades();
  }, []);

  const fetchTrades = async () => {
    setLoading(true);
    try {
      const data = await api.get('/order-history');
      const tradeList = Array.isArray(data) ? data : [];
      setTrades(tradeList);
      computeMetrics(tradeList);
    } catch (error) {
      console.error('Error fetching trades:', error);
    } finally {
      setLoading(false);
    }
  };

  const computeMetrics = (tradeList: Trade[]) => {
    if (tradeList.length === 0) {
      setMetrics(null);
      setPnlCurve([]);
      return;
    }

    // Simulate P&L from trades (price * qty for buys, -price * qty for sells)
    let cumulative = 0;
    const pnlData: Array<{ date: string; pnl: number; cumulative: number }> = [];
    let wins = 0;
    let losses = 0;
    let totalPnl = 0;
    let maxWin = 0;
    let maxLoss = 0;
    let currentWinStreak = 0;
    let currentLossStreak = 0;
    let maxWinStreak = 0;
    let maxLossStreak = 0;

    // Sort by timestamp
    const sorted = [...tradeList].sort((a, b) => (a.timestamp || '').localeCompare(b.timestamp || ''));

    for (const trade of sorted) {
      const pnl = trade.pnl != null ? Number(trade.pnl) : 0;

      cumulative += pnl;
      totalPnl += pnl;

      if (pnl >= 0) {
        wins++;
        currentWinStreak++;
        currentLossStreak = 0;
        maxWin = Math.max(maxWin, pnl);
      } else {
        losses++;
        currentLossStreak++;
        currentWinStreak = 0;
        maxLoss = Math.min(maxLoss, pnl);
      }

      maxWinStreak = Math.max(maxWinStreak, currentWinStreak);
      maxLossStreak = Math.max(maxLossStreak, currentLossStreak);

      const dateStr = trade.timestamp ? trade.timestamp.slice(0, 10) : 'unknown';
      pnlData.push({
        date: dateStr,
        pnl: Math.round(pnl * 100) / 100,
        cumulative: Math.round(cumulative * 100) / 100,
      });
    }

    const totalTrades = wins + losses;
    setMetrics({
      total_trades: totalTrades,
      win_rate: totalTrades > 0 ? Math.round((wins / totalTrades) * 10000) / 100 : 0,
      total_pnl: Math.round(totalPnl * 100) / 100,
      avg_pnl: totalTrades > 0 ? Math.round((totalPnl / totalTrades) * 100) / 100 : 0,
      max_win: Math.round(maxWin * 100) / 100,
      max_loss: Math.round(maxLoss * 100) / 100,
      profit_factor: losses > 0 ? Math.round((wins / losses) * 100) / 100 : wins > 0 ? 999 : 0,
      sharpe_ratio: 0,
      win_streak: maxWinStreak,
      loss_streak: maxLossStreak,
    });

    setPnlCurve(pnlData);
  };

  const formatCurrency = (val: number) => {
    return `₹${val.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  };

  return (
    <div className="p-6 bg-black text-white">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold">Performance Analytics</h1>
        {loading ? <div className="text-gray-400 text-sm">Loading...</div> : null}
      </div>

      {metrics ? (
        <>
          {/* Key Metrics */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8">
            <div className="bg-gray-900 p-4 rounded-lg">
              <p className="text-gray-400 text-sm">Total Trades</p>
              <p className="text-2xl font-bold">{metrics.total_trades}</p>
            </div>
            <div className="bg-gray-900 p-4 rounded-lg">
              <p className="text-gray-400 text-sm">Win Rate</p>
              <p className={`text-2xl font-bold ${metrics.win_rate >= 50 ? 'text-green-400' : 'text-red-400'}`}>
                {metrics.win_rate}%
              </p>
            </div>
            <div className="bg-gray-900 p-4 rounded-lg">
              <p className="text-gray-400 text-sm">Total P&L</p>
              <p className={`text-2xl font-bold ${metrics.total_pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                {formatCurrency(metrics.total_pnl)}
              </p>
            </div>
            <div className="bg-gray-900 p-4 rounded-lg">
              <p className="text-gray-400 text-sm">Avg P&L</p>
              <p className={`text-2xl font-bold ${metrics.avg_pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                {formatCurrency(metrics.avg_pnl)}
              </p>
            </div>
          </div>

          {/* Extended Metrics */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8">
            <div className="bg-gray-900 p-4 rounded-lg">
              <p className="text-gray-400 text-sm">Max Win</p>
              <p className="text-xl font-bold text-green-400">{formatCurrency(metrics.max_win)}</p>
            </div>
            <div className="bg-gray-900 p-4 rounded-lg">
              <p className="text-gray-400 text-sm">Max Loss</p>
              <p className="text-xl font-bold text-red-400">{formatCurrency(metrics.max_loss)}</p>
            </div>
            <div className="bg-gray-900 p-4 rounded-lg">
              <p className="text-gray-400 text-sm">Profit Factor</p>
              <p className="text-xl font-bold">{metrics.profit_factor}</p>
            </div>
            <div className="bg-gray-900 p-4 rounded-lg">
              <p className="text-gray-400 text-sm">Streaks (W/L)</p>
              <p className="text-xl font-bold">
                <span className="text-green-400">{metrics.win_streak}</span>
                <span className="text-gray-500"> / </span>
                <span className="text-red-400">{metrics.loss_streak}</span>
              </p>
            </div>
          </div>

          {/* Cumulative P&L Chart */}
          {pnlCurve.length > 0 && (
            <div className="bg-gray-900 p-4 rounded-lg mb-8">
              <h3 className="text-lg font-semibold mb-4">Cumulative P&L</h3>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={pnlCurve}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                  <XAxis dataKey="date" stroke="#666" tick={{ fontSize: 11 }} />
                  <YAxis stroke="#666" tick={{ fontSize: 11 }} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#1a1a1a', border: '1px solid #444' }}
                    formatter={(value: number) => [`₹${value.toFixed(2)}`, 'Cumulative P&L']}
                  />
                  <Line type="monotone" dataKey="cumulative" stroke="#3b82f6" dot={false} strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Per-Trade P&L Bar Chart */}
          {pnlCurve.length > 0 && (
            <div className="bg-gray-900 p-4 rounded-lg mb-8">
              <h3 className="text-lg font-semibold mb-4">Per-Trade P&L</h3>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={pnlCurve.slice(-30)}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                  <XAxis dataKey="date" stroke="#666" tick={{ fontSize: 10 }} />
                  <YAxis stroke="#666" tick={{ fontSize: 10 }} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#1a1a1a', border: '1px solid #444' }}
                    formatter={(value: number) => [`₹${value.toFixed(2)}`, 'P&L']}
                  />
                  <Bar dataKey="pnl" fill="#3b82f6" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Trade History Table */}
          <div className="bg-gray-900 rounded-lg overflow-hidden">
            <div className="px-4 py-3 bg-gray-800">
              <h3 className="text-lg font-semibold">Trade History</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-800">
                  <tr>
                    <th className="px-4 py-3 text-left">Symbol</th>
                    <th className="px-4 py-3 text-left">Side</th>
                    <th className="px-4 py-3 text-right">Qty</th>
                    <th className="px-4 py-3 text-right">Price</th>
                    <th className="px-4 py-3 text-left">Status</th>
                    <th className="px-4 py-3 text-left">Time</th>
                  </tr>
                </thead>
                <tbody>
                  {trades.slice(0, 50).map((trade) => (
                    <tr key={trade.id} className="border-b border-gray-800 hover:bg-gray-800/60">
                      <td className="px-4 py-3 font-bold">{trade.symbol}</td>
                      <td className="px-4 py-3">
                        <span className={`px-2 py-1 rounded text-sm ${
                          trade.side === 'buy' ? 'bg-green-900 text-green-400' : 'bg-red-900 text-red-400'
                        }`}>
                          {trade.side.toUpperCase()}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-right">{trade.qty}</td>
                      <td className="px-4 py-3 text-right">{formatCurrency(trade.price)}</td>
                      <td className="px-4 py-3">
                        <span className={`px-2 py-1 rounded text-sm ${
                          trade.status === 'filled' ? 'bg-green-900 text-green-400' :
                          trade.status === 'submitted' ? 'bg-yellow-900 text-yellow-400' :
                          'bg-gray-800 text-gray-300'
                        }`}>
                          {trade.status}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-gray-400 text-sm">
                        {trade.timestamp ? new Date(trade.timestamp).toLocaleString() : '-'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {trades.length === 0 && !loading && (
              <div className="p-6 text-center text-gray-400">No trades yet</div>
            )}
          </div>
        </>
      ) : !loading ? (
        <div className="bg-gray-900 p-8 rounded-lg text-center">
          <p className="text-gray-400 text-lg">No trade data available</p>
          <p className="text-gray-500 text-sm mt-2">Start trading to see performance analytics</p>
        </div>
      ) : null}
    </div>
  );
}
