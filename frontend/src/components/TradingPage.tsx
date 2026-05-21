import React, { useEffect, useState } from 'react';
const API_URL = '';
export function TradingPage() {
  const [positions, setPositions] = useState<any[]>([]);
  const [orders, setOrders] = useState<any[]>([]);
  const [mode, setMode] = useState<'paper' | 'live'>('paper');
  const [form, setForm] = useState({ symbol: '', side: 'buy', qty: '', price: '', stopLoss: '', takeProfit: '' });
  const load = async () => {
    setPositions(await (await fetch(`${API_URL}/positions`)).json());
    setOrders(await (await fetch(`${API_URL}/order-history`)).json());
  };
  useEffect(() => { load(); }, []);
  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    await fetch(`${API_URL}/trade`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ symbol: form.symbol, side: form.side, quantity: Number(form.qty), price: Number(form.price), stop_loss: form.stopLoss ? Number(form.stopLoss) : null, take_profit: form.takeProfit ? Number(form.takeProfit) : null, mode }) });
    setForm({ symbol: '', side: 'buy', qty: '', price: '', stopLoss: '', takeProfit: '' });
    load();
  };
  return <div style={{ padding: 16 }}><h2>Trading</h2><button onClick={() => setMode(mode === 'paper' ? 'live' : 'paper')}>{mode}</button><table><thead><tr><th>Symbol</th><th>Qty</th><th>P&L</th></tr></thead><tbody>{positions.map((p) => <tr key={p.symbol}><td>{p.symbol}</td><td>{p.qty}</td><td>{p.pnl}</td></tr>)}</tbody></table><form onSubmit={submit}><input placeholder='Symbol' value={form.symbol} onChange={(e) => setForm({ ...form, symbol: e.target.value.toUpperCase() })} /><input placeholder='Qty' value={form.qty} onChange={(e) => setForm({ ...form, qty: e.target.value })} /><input placeholder='Price' value={form.price} onChange={(e) => setForm({ ...form, price: e.target.value })} /><button>Place Order</button></form><h3>Order History</h3><ul>{orders.map((o) => <li key={o.id}>{o.symbol} {o.side} {o.qty} @ {o.price}</li>)}</ul></div>;
}
