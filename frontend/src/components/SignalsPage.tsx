import React, { useEffect, useMemo, useState } from 'react';
import { api } from '../api';

const API_URL = '';

type TradeSignal = {
  id: string;
  symbol: string;
  approval_status: 'pending' | 'approved' | 'rejected' | string;
  signal_price?: number;
  signal_time?: string;
  technical_score?: number;
  news_score?: number;
  fundamental_score?: number;
  risk_score?: number;
  overall_score?: number;
};

export function SignalsPage() {
  const [signals, setSignals] = useState<TradeSignal[]>([]);
  const [loading, setLoading] = useState(true);
  const [approving, setApproving] = useState<string | null>(null);
  const [skipping, setSkipping] = useState<string | null>(null);

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
      const res = await fetch(`${API_URL}/api/signals/pending`);
      const data = await safeJson(res);
      setSignals(Array.isArray(data) ? data : []);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refresh();
    const t = setInterval(refresh, 10000);
    return () => clearInterval(t);
  }, []);

  const approve = async (id: string) => {
    setApproving(id);
    try {
      await api.post('/api/signal/approve', { signal_id: id });
      await refresh();
    } catch (error: any) {
      alert(error?.message || 'Failed to approve signal');
    } finally {
      setApproving(null);
    }
  };

  const skip = async (id: string) => {
    setSkipping(id);
    try {
      await api.post('/api/signal/skip', { signal_id: id, reason: 'Skipped from dashboard' });
      await refresh();
    } catch (error: any) {
      alert(error?.message || 'Failed to skip signal');
    } finally {
      setSkipping(null);
    }
  };
      }
      await refresh();
    } finally {
      setSkipping(null);
    }
  };

  const summary = useMemo(() => {
    const pending = signals.length;
    const avg = pending ? signals.reduce((a, s) => a + Number(s.overall_score || 0), 0) / pending : 0;
    return { pending, avg };
  }, [signals]);

  return (
    <div className="p-6 bg-black text-white">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold">Signals</h1>
        <button onClick={refresh} className="px-3 py-2 bg-gray-900 hover:bg-gray-800 rounded text-sm font-semibold">
          {loading ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
        <div className="bg-gray-900 border border-gray-800 rounded p-4">
          <div className="text-gray-400 text-sm">Pending</div>
          <div className="text-2xl font-bold text-yellow-300">{summary.pending}</div>
        </div>
        <div className="bg-gray-900 border border-gray-800 rounded p-4">
          <div className="text-gray-400 text-sm">Avg Score</div>
          <div className="text-2xl font-bold">{summary.avg.toFixed(0)}%</div>
        </div>
        <div className="bg-gray-900 border border-gray-800 rounded p-4">
          <div className="text-gray-400 text-sm">Auto-trading</div>
          <div className="text-sm text-gray-300 mt-1">
            Approval updates status now. Execution wiring can be added next (paper broker).
          </div>
        </div>
      </div>

      <div className="bg-gray-900 rounded-lg overflow-hidden border border-gray-800">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-800 border-b border-gray-700">
              <tr>
                <th className="px-4 py-3 text-left">Symbol</th>
                <th className="px-4 py-3 text-left">Status</th>
                <th className="px-4 py-3 text-right">Price</th>
                <th className="px-4 py-3 text-right">Tech</th>
                <th className="px-4 py-3 text-right">News</th>
                <th className="px-4 py-3 text-right">Fund</th>
                <th className="px-4 py-3 text-right">Risk</th>
                <th className="px-4 py-3 text-right">Overall</th>
                <th className="px-4 py-3 text-center">Action</th>
              </tr>
            </thead>
            <tbody>
              {signals.map((s) => (
                <tr key={s.id} className="border-b border-gray-800 hover:bg-gray-800/60">
                  <td className="px-4 py-3 font-semibold">{s.symbol}</td>
                  <td className="px-4 py-3 text-yellow-200">{s.approval_status}</td>
                  <td className="px-4 py-3 text-right">₹{Number(s.signal_price || 0).toFixed(2)}</td>
                  <td className="px-4 py-3 text-right">{Number(s.technical_score || 0).toFixed(0)}</td>
                  <td className="px-4 py-3 text-right">{Number(s.news_score || 0).toFixed(0)}</td>
                  <td className="px-4 py-3 text-right">{Number(s.fundamental_score || 0).toFixed(0)}</td>
                  <td className="px-4 py-3 text-right">{Number(s.risk_score || 0).toFixed(0)}</td>
                  <td className="px-4 py-3 text-right font-semibold">{Number(s.overall_score || 0).toFixed(0)}</td>
                  <td className="px-4 py-3 text-center">
                    <div className="flex items-center justify-center gap-2">
                      <button
                        disabled={approving === s.id}
                        onClick={() => approve(s.id)}
                        className="px-3 py-1 bg-green-600 hover:bg-green-700 disabled:bg-gray-700 rounded text-sm font-semibold"
                      >
                        {approving === s.id ? 'Approving...' : 'Approve'}
                      </button>
                      <button
                        disabled={skipping === s.id}
                        onClick={() => skip(s.id)}
                        className="px-3 py-1 bg-gray-800 hover:bg-gray-700 disabled:bg-gray-700 rounded text-sm font-semibold"
                      >
                        {skipping === s.id ? 'Skipping...' : 'Skip'}
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {signals.length === 0 && !loading ? <div className="p-6 text-center text-gray-400">No pending signals</div> : null}
      </div>
    </div>
  );
}
