import React, { useState, useEffect, useCallback } from 'react';
import { api } from '../api';

interface BrokerAccount {
  broker: string;
  mode: string;
  connected: boolean;
  account_id?: string;
  balance?: number;
  available_margin?: number;
  last_sync?: string;
}

interface Position {
  symbol: string;
  quantity: number;
  avg_price: number;
  ltp: number;
  pnl: number;
  pnl_pct: number;
}

interface Mismatch {
  symbol: string;
  local_qty: number;
  broker_qty: number;
  local_avg: number;
  broker_avg: number;
  difference: number;
}

interface ReconciliationResult {
  status: string;
  matches: number;
  mismatches: Mismatch[];
  timestamp: string;
}

export function BrokerReconciliation() {
  const [account, setAccount] = useState<BrokerAccount | null>(null);
  const [positions, setPositions] = useState<Position[]>([]);
  const [mismatches, setMismatches] = useState<Mismatch[]>([]);
  const [reconResult, setReconResult] = useState<ReconciliationResult | null>(null);
  const [syncing, setSyncing] = useState(false);
  const [loading, setLoading] = useState(true);

  const fetchAccount = useCallback(async () => {
    try {
      const [acctRes, posRes] = await Promise.allSettled([
        api.get('/api/broker/account'),
        api.get('/api/portfolio/positions'),
      ]);

      if (acctRes.status === 'fulfilled') {
        setAccount(acctRes.value);
      }

      if (posRes.status === 'fulfilled') {
        const data = posRes.value;
        setPositions(data.positions || data || []);
      }
    } catch (err) {
      console.error('Failed to fetch broker data:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAccount();
  }, [fetchAccount]);

  const handleSyncNow = async () => {
    setSyncing(true);
    try {
      const result = await api.post('/api/broker/reconcile');
      setReconResult(result);
      if (result.mismatches) {
        setMismatches(result.mismatches);
      }
    } catch (err) {
      console.error('Reconciliation failed:', err);
    } finally {
      setSyncing(false);
    }
  };

  const handleForceSync = async (symbol: string) => {
    try {
      await api.post(`/api/broker/sync/${symbol}`);
      // Refresh after sync
      await fetchAccount();
    } catch (err) {
      console.error('Force sync failed:', err);
    }
  };

  if (loading) {
    return (
      <div className="bg-gray-950 border border-gray-800 rounded-lg p-6">
        <div className="text-gray-400">Loading broker data...</div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Account Status */}
      <div className="bg-gray-950 border border-gray-800 rounded-lg p-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">Broker Account</h3>
          <button
            onClick={handleSyncNow}
            disabled={syncing}
            className="px-4 py-2 bg-blue-600 rounded hover:bg-blue-700 disabled:opacity-50 text-sm"
          >
            {syncing ? 'Syncing...' : 'Sync Now'}
          </button>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm">
          <div>
            <div className="text-gray-500 text-xs">Broker</div>
            <div className="text-white font-medium">{account?.broker || 'Not configured'}</div>
          </div>
          <div>
            <div className="text-gray-500 text-xs">Mode</div>
            <div className={`font-medium ${account?.mode === 'live' ? 'text-red-400' : 'text-green-400'}`}>
              {account?.mode || 'paper'}
            </div>
          </div>
          <div>
            <div className="text-gray-500 text-xs">Connection</div>
            <div className={`font-medium ${account?.connected ? 'text-green-400' : 'text-red-400'}`}>
              {account?.connected ? 'Connected' : 'Disconnected'}
            </div>
          </div>
          <div>
            <div className="text-gray-500 text-xs">Balance</div>
            <div className="text-white font-medium">
              {account?.balance != null ? `₹${account.balance.toLocaleString()}` : '-'}
            </div>
          </div>
        </div>

        {account?.last_sync && (
          <div className="mt-3 text-xs text-gray-500">
            Last synced: {new Date(account.last_sync).toLocaleString()}
          </div>
        )}
      </div>

      {/* Reconciliation Results */}
      {reconResult && (
        <div className={`border rounded-lg p-4 ${
          reconResult.mismatches.length === 0
            ? 'bg-green-950 border-green-800'
            : 'bg-red-950 border-red-800'
        }`}>
          <h4 className="text-sm font-semibold mb-2">Reconciliation Result</h4>
          <div className="text-sm">
            {reconResult.mismatches.length === 0 ? (
              <span className="text-green-400">All positions match ({reconResult.matches} matched)</span>
            ) : (
              <div>
                <span className="text-red-400">
                  {reconResult.mismatches.length} mismatch(es) found
                </span>
                <div className="mt-2 space-y-1">
                  {reconResult.mismatches.map((m, i) => (
                    <div key={i} className="flex items-center gap-4 text-xs">
                      <span className="font-medium text-white w-20">{m.symbol}</span>
                      <span className="text-gray-400">
                        Local: {m.local_qty} @ ₹{m.local_avg.toFixed(2)}
                      </span>
                      <span className="text-gray-400">
                        Broker: {m.broker_qty} @ ₹{m.broker_avg.toFixed(2)}
                      </span>
                      <button
                        onClick={() => handleForceSync(m.symbol)}
                        className="px-2 py-0.5 bg-blue-600 rounded text-[10px] hover:bg-blue-700"
                      >
                        Force Sync
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Positions */}
      <div className="bg-gray-950 border border-gray-800 rounded-lg p-4">
        <h3 className="text-sm font-semibold text-gray-300 mb-3">Current Positions</h3>
        {positions.length === 0 ? (
          <div className="text-gray-500 text-sm">No open positions</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-gray-500 text-xs border-b border-gray-800">
                  <th className="text-left py-2">Symbol</th>
                  <th className="text-right py-2">Qty</th>
                  <th className="text-right py-2">Avg Price</th>
                  <th className="text-right py-2">LTP</th>
                  <th className="text-right py-2">P&L</th>
                  <th className="text-right py-2">P&L %</th>
                </tr>
              </thead>
              <tbody>
                {positions.map((pos) => (
                  <tr key={pos.symbol} className="border-b border-gray-800/50 hover:bg-gray-900/50">
                    <td className="py-2 font-medium text-white">{pos.symbol}</td>
                    <td className="py-2 text-right text-gray-300">{pos.quantity}</td>
                    <td className="py-2 text-right text-gray-300">₹{pos.avg_price.toFixed(2)}</td>
                    <td className="py-2 text-right text-gray-300">₹{pos.ltp.toFixed(2)}</td>
                    <td className={`py-2 text-right ${pos.pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {pos.pnl >= 0 ? '+' : ''}₹{pos.pnl.toFixed(2)}
                    </td>
                    <td className={`py-2 text-right ${pos.pnl_pct >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {pos.pnl_pct >= 0 ? '+' : ''}{pos.pnl_pct.toFixed(2)}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
