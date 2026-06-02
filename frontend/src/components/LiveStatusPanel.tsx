import React, { useState, useEffect, useCallback } from 'react';
import { api } from '../api';

interface SystemStatus {
  market_engine: string;
  position_manager: string;
  trade_execution: string;
  news_sentiment: string;
  telegram_poller: string;
  kill_switch: string;
  last_tick: string;
  open_executions: number;
  filled_today: number;
}

interface PriceUpdate {
  symbol: string;
  ltp: number;
  change: number;
  change_pct: number;
  timestamp: number;
}

interface OrderEvent {
  order_id: string;
  symbol: string;
  side: string;
  status: string;
  price?: number;
  quantity?: number;
  timestamp: number;
}

interface PnLUpdate {
  realized: number;
  unrealized: number;
  total: number;
  timestamp: number;
}

export function LiveStatusPanel() {
  const [system, setSystem] = useState<SystemStatus | null>(null);
  const [prices, setPrices] = useState<Map<string, PriceUpdate>>(new Map());
  const [orders, setOrders] = useState<OrderEvent[]>([]);
  const [pnl, setPnl] = useState<PnLUpdate | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchStatus = useCallback(async () => {
    try {
      const [sysRes, portRes, ordersRes] = await Promise.allSettled([
        api.get('/api/system/status'),
        api.get('/api/portfolio'),
        api.get('/api/executions?limit=10'),
      ]);

      if (sysRes.status === 'fulfilled') {
        setSystem(sysRes.value);
      }

      if (portRes.status === 'fulfilled') {
        const data = portRes.value;
        const positions = data.positions || [];
        const priceMap = new Map<string, PriceUpdate>();
        for (const pos of positions) {
          if (pos.quantity !== 0) {
            priceMap.set(pos.symbol, {
              symbol: pos.symbol,
              ltp: pos.current_price || pos.avg_entry_price || 0,
              change: pos.unrealized_pnl || 0,
              change_pct: pos.avg_entry_price ? ((pos.current_price - pos.avg_entry_price) / pos.avg_entry_price * 100) : 0,
              timestamp: Date.now(),
            });
          }
        }
        setPrices(priceMap);
        setPnl({
          realized: data.realized_pnl || 0,
          unrealized: data.unrealized_pnl || 0,
          total: (data.realized_pnl || 0) + (data.unrealized_pnl || 0),
          timestamp: Date.now(),
        });
      }

      if (ordersRes.status === 'fulfilled') {
        const execs = Array.isArray(ordersRes.value) ? ordersRes.value : (ordersRes.value.executions || []);
        setOrders(execs.map((e: any) => ({
          id: e.client_order_id || e.id,
          symbol: e.symbol,
          side: e.side,
          quantity: e.quantity,
          price: e.entry_price || 0,
          status: e.status,
          timestamp: e.created_at,
        })));
      }
    } catch (err) {
      console.error('Failed to fetch status:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 5000);
    return () => clearInterval(interval);
  }, [fetchStatus]);

  if (loading) {
    return (
      <div className="bg-gray-950 border border-gray-800 rounded-lg p-4">
        <div className="text-gray-400 text-sm">Loading system status...</div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* System Health */}
      <div className="bg-gray-950 border border-gray-800 rounded-lg p-4">
        <h3 className="text-sm font-semibold text-gray-300 mb-3">System Health</h3>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
          <StatusIndicator label="Market Engine" status={system?.market_engine || 'unknown'} />
          <StatusIndicator label="Position Mgr" status={system?.position_manager || 'unknown'} />
          <StatusIndicator label="Trade Exec" status={system?.trade_execution || 'unknown'} />
          <StatusIndicator label="News Agent" status={system?.news_sentiment || 'unknown'} />
          <StatusIndicator label="Telegram" status={system?.telegram_poller || 'unknown'} />
          <StatusIndicator label="Kill Switch" status={system?.kill_switch || 'unknown'} />
        </div>
        {system?.last_tick && (
          <div className="mt-3 text-xs text-gray-500">
            Last tick: {new Date(system.last_tick).toLocaleTimeString()}
            {system.open_executions > 0 && (
              <span className="ml-2 text-yellow-400">
                {system.open_executions} open execution(s)
              </span>
            )}
          </div>
        )}
      </div>

      {/* Live Prices */}
      <div className="bg-gray-950 border border-gray-800 rounded-lg p-4">
        <h3 className="text-sm font-semibold text-gray-300 mb-3">Live Prices</h3>
        {prices.size === 0 ? (
          <div className="text-gray-500 text-xs">Waiting for price updates...</div>
        ) : (
          <div className="space-y-1">
            {Array.from(prices.values()).map((p) => (
              <PriceRow key={p.symbol} update={p} />
            ))}
          </div>
        )}
      </div>

      {/* PnL Summary */}
      {pnl && (
        <div className="bg-gray-950 border border-gray-800 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-gray-300 mb-3">PnL Summary</h3>
          <div className="grid grid-cols-3 gap-2 text-sm">
            <div>
              <div className="text-gray-500 text-xs">Realized</div>
              <div className={pnl.realized >= 0 ? 'text-green-400' : 'text-red-400'}>
                {pnl.realized >= 0 ? '+' : ''}{pnl.realized.toFixed(2)}
              </div>
            </div>
            <div>
              <div className="text-gray-500 text-xs">Unrealized</div>
              <div className={pnl.unrealized >= 0 ? 'text-green-400' : 'text-red-400'}>
                {pnl.unrealized >= 0 ? '+' : ''}{pnl.unrealized.toFixed(2)}
              </div>
            </div>
            <div>
              <div className="text-gray-500 text-xs">Total</div>
              <div className={pnl.total >= 0 ? 'text-green-400 font-bold' : 'text-red-400 font-bold'}>
                {pnl.total >= 0 ? '+' : ''}{pnl.total.toFixed(2)}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Recent Orders */}
      <div className="bg-gray-950 border border-gray-800 rounded-lg p-4">
        <h3 className="text-sm font-semibold text-gray-300 mb-3">Recent Orders</h3>
        {orders.length === 0 ? (
          <div className="text-gray-500 text-xs">No recent orders</div>
        ) : (
          <div className="space-y-1 max-h-40 overflow-y-auto">
            {orders.slice(-10).reverse().map((o, i) => (
              <div key={i} className="flex items-center justify-between text-xs py-1 border-b border-gray-800 last:border-0">
                <span className={o.side === 'buy' ? 'text-green-400' : 'text-red-400'}>
                  {o.side.toUpperCase()} {o.symbol}
                </span>
                <span className="text-gray-400">
                  {o.quantity} @ {o.price?.toFixed(2) || '-'}
                </span>
                <OrderStatusBadge status={o.status} />
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function StatusIndicator({ label, status }: { label: string; status: string }) {
  const colorMap: Record<string, string> = {
    running: 'bg-green-500',
    healthy: 'bg-green-500',
    active: 'bg-green-500',
    enabled: 'bg-green-500',
    stopped: 'bg-gray-500',
    disabled: 'bg-gray-500',
    error: 'bg-red-500',
    failed: 'bg-red-500',
    warning: 'bg-yellow-500',
  };
  const dotColor = colorMap[status.toLowerCase()] || 'bg-yellow-500';

  return (
    <div className="flex items-center gap-2 text-xs">
      <div className={`w-2 h-2 rounded-full ${dotColor}`} />
      <span className="text-gray-400">{label}</span>
      <span className="text-gray-500 ml-auto">{status}</span>
    </div>
  );
}

function PriceRow({ update }: { update: PriceUpdate }) {
  const isUp = update.change >= 0;
  return (
    <div className="flex items-center justify-between text-xs py-1">
      <span className="font-medium text-white w-20">{update.symbol}</span>
      <span className="text-gray-300">{update.ltp.toFixed(2)}</span>
      <span className={isUp ? 'text-green-400' : 'text-red-400'}>
        {isUp ? '+' : ''}{update.change_pct.toFixed(2)}%
      </span>
    </div>
  );
}

function OrderStatusBadge({ status }: { status: string }) {
  const colorMap: Record<string, string> = {
    filled: 'bg-green-900 text-green-300',
    submitted: 'bg-blue-900 text-blue-300',
    pending: 'bg-yellow-900 text-yellow-300',
    rejected: 'bg-red-900 text-red-300',
    cancelled: 'bg-gray-800 text-gray-400',
  };
  const colors = colorMap[status.toLowerCase()] || 'bg-gray-800 text-gray-400';

  return (
    <span className={`px-1.5 py-0.5 rounded text-[10px] ${colors}`}>
      {status}
    </span>
  );
}
