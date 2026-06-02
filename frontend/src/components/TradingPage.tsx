import React, { useEffect, useState } from 'react';
import { api } from '../api';

const API_URL = '';

interface Position {
  symbol: string;
  qty: number;
  entry_price: number;
  current_price: number;
  pnl: number;
  pnl_pct: number;
}

interface Order {
  id: string;
  symbol: string;
  side: 'buy' | 'sell';
  qty: number;
  price: number;
  status: 'pending' | 'filled' | 'partial' | 'cancelled';
  timestamp: string;
}

export function TradingPage() {
  const [mode, setMode] = useState<'paper' | 'live'>('paper');
  const [positions, setPositions] = useState<Position[]>([]);
  const [orders, setOrders] = useState<Order[]>([]);
  const [formData, setFormData] = useState({
    symbol: '',
    side: 'buy' as 'buy' | 'sell',
    qty: '',
    price: '',
    stopLoss: '',
    takeProfit: '',
  });

  useEffect(() => {
    fetchPositions();
    fetchOrders();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mode]);

  const safeJson = async (res: Response) => {
    const text = await res.text();
    try {
      return text ? JSON.parse(text) : {};
    } catch {
      return { raw: text };
    }
  };

  const fetchPositions = async () => {
    try {
      const res = await fetch(`${API_URL}/positions`);
      const data = await safeJson(res);
      setPositions(Array.isArray(data) ? data : []);
    } catch {
      setPositions([]);
    }
  };

  const fetchOrders = async () => {
    try {
      const res = await fetch(`${API_URL}/order-history`);
      const data = await safeJson(res);
      setOrders(Array.isArray(data) ? data : []);
    } catch {
      setOrders([]);
    }
  };

  const handlePlaceOrder = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.symbol || !formData.qty || !formData.price) {
      alert('Please fill all required fields');
      return;
    }

    try {
      const data = await api.post('/trade', {
        symbol: formData.symbol,
        side: formData.side,
        quantity: parseFloat(formData.qty),
        price: parseFloat(formData.price),
        stop_loss: formData.stopLoss ? parseFloat(formData.stopLoss) : null,
        take_profit: formData.takeProfit ? parseFloat(formData.takeProfit) : null,
        mode,
      });
      setFormData({ symbol: '', side: 'buy', qty: '', price: '', stopLoss: '', takeProfit: '' });
      await Promise.all([fetchPositions(), fetchOrders()]);
    } catch (error: any) {
      console.error('Error placing order:', error);
      alert(error?.message || 'Error placing order');
    }
  };

  const handleClosePosition = async (symbol: string) => {
    try {
      await api.delete(`/positions/${encodeURIComponent(symbol)}`);
      await fetchPositions();
    } catch (error) {
      console.error('Error closing position:', error);
    }
  };

  return (
    <div className="p-6 bg-black text-white">
      <div className="flex flex-col gap-3 sm:flex-row sm:justify-between sm:items-center mb-6">
        <h1 className="text-3xl font-bold">Trading Dashboard</h1>
        <div className="flex items-center gap-3">
          <span className="text-sm text-gray-300">Mode:</span>
          <button
            onClick={() => setMode(mode === 'paper' ? 'live' : 'paper')}
            className={`px-4 py-2 rounded font-semibold ${
              mode === 'paper' ? 'bg-blue-600 hover:bg-blue-700' : 'bg-red-600 hover:bg-red-700'
            }`}
          >
            {mode === 'paper' ? 'Paper' : 'LIVE'}
          </button>
        </div>
      </div>

      <section className="mb-8">
        <h2 className="text-xl font-bold mb-4">Active Positions</h2>
        <div className="bg-gray-900 rounded-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-800 border-b border-gray-700">
                <tr>
                  <th className="px-4 py-3 text-left">Symbol</th>
                  <th className="px-4 py-3 text-right">Qty</th>
                  <th className="px-4 py-3 text-right">Entry Price</th>
                  <th className="px-4 py-3 text-right">Current Price</th>
                  <th className="px-4 py-3 text-right">P&L</th>
                  <th className="px-4 py-3 text-right">%</th>
                  <th className="px-4 py-3 text-center">Action</th>
                </tr>
              </thead>
              <tbody>
                {positions.map((pos) => (
                  <tr key={pos.symbol} className="border-b border-gray-800 hover:bg-gray-800/60">
                    <td className="px-4 py-3 font-semibold">{pos.symbol}</td>
                    <td className="px-4 py-3 text-right">{pos.qty}</td>
                    <td className="px-4 py-3 text-right">₹{Number(pos.entry_price).toFixed(2)}</td>
                    <td className="px-4 py-3 text-right">₹{Number(pos.current_price).toFixed(2)}</td>
                    <td
                      className={`px-4 py-3 text-right font-semibold ${
                        pos.pnl >= 0 ? 'text-green-400' : 'text-red-400'
                      }`}
                    >
                      {pos.pnl >= 0 ? '+' : ''}
                      {Number(pos.pnl).toFixed(2)}
                    </td>
                    <td className={`px-4 py-3 text-right ${pos.pnl_pct >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {pos.pnl_pct >= 0 ? '+' : ''}
                      {Number(pos.pnl_pct).toFixed(2)}%
                    </td>
                    <td className="px-4 py-3 text-center">
                      <button
                        onClick={() => handleClosePosition(pos.symbol)}
                        className="px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700"
                      >
                        Close
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {positions.length === 0 && <div className="p-6 text-center text-gray-400">No active positions</div>}
        </div>
      </section>

      <section className="mb-8">
        <h2 className="text-xl font-bold mb-4">Place New Order</h2>
        <form onSubmit={handlePlaceOrder} className="bg-gray-900 p-6 rounded-lg">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium mb-2">Symbol</label>
              <input
                type="text"
                placeholder="INFY"
                value={formData.symbol}
                onChange={(e) => setFormData({ ...formData, symbol: e.target.value.toUpperCase() })}
                className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Side</label>
              <select
                value={formData.side}
                onChange={(e) => setFormData({ ...formData, side: e.target.value as 'buy' | 'sell' })}
                className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white"
              >
                <option value="buy">Buy</option>
                <option value="sell">Sell</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium mb-2">Quantity</label>
              <input
                type="number"
                placeholder="100"
                value={formData.qty}
                onChange={(e) => setFormData({ ...formData, qty: e.target.value })}
                className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Price</label>
              <input
                type="number"
                step="0.01"
                placeholder="1955.50"
                value={formData.price}
                onChange={(e) => setFormData({ ...formData, price: e.target.value })}
                className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
            <div>
              <label className="block text-sm font-medium mb-2">Stop Loss</label>
              <input
                type="number"
                step="0.01"
                placeholder="1920"
                value={formData.stopLoss}
                onChange={(e) => setFormData({ ...formData, stopLoss: e.target.value })}
                className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Take Profit</label>
              <input
                type="number"
                step="0.01"
                placeholder="1985"
                value={formData.takeProfit}
                onChange={(e) => setFormData({ ...formData, takeProfit: e.target.value })}
                className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white"
              />
            </div>
          </div>

          <button type="submit" className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 rounded">
            Place Order
          </button>
        </form>
      </section>

      <section>
        <h2 className="text-xl font-bold mb-4">Order History</h2>
        <div className="bg-gray-900 rounded-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-800 border-b border-gray-700">
                <tr>
                  <th className="px-4 py-3 text-left">Date</th>
                  <th className="px-4 py-3 text-left">Symbol</th>
                  <th className="px-4 py-3 text-left">Side</th>
                  <th className="px-4 py-3 text-right">Qty</th>
                  <th className="px-4 py-3 text-right">Price</th>
                  <th className="px-4 py-3 text-left">Status</th>
                </tr>
              </thead>
              <tbody>
                {orders.slice(0, 10).map((order) => (
                  <tr key={order.id} className="border-b border-gray-800 hover:bg-gray-800/60">
                    <td className="px-4 py-3 text-sm">
                      {order.timestamp ? new Date(order.timestamp).toLocaleDateString() : ''}
                    </td>
                    <td className="px-4 py-3 font-semibold">{order.symbol}</td>
                    <td className={`px-4 py-3 ${order.side === 'buy' ? 'text-green-400' : 'text-red-400'}`}>
                      {order.side === 'buy' ? 'Buy' : 'Sell'}
                    </td>
                    <td className="px-4 py-3 text-right">{order.qty}</td>
                    <td className="px-4 py-3 text-right">₹{Number(order.price).toFixed(2)}</td>
                    <td
                      className={`px-4 py-3 text-sm ${
                        order.status === 'filled'
                          ? 'text-green-400'
                          : order.status === 'partial'
                            ? 'text-yellow-400'
                            : 'text-gray-400'
                      }`}
                    >
                      {String(order.status || '').toUpperCase()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {orders.length === 0 && <div className="p-6 text-center text-gray-400">No orders yet</div>}
        </div>
      </section>
    </div>
  );
}

