import React, { useEffect, useState } from 'react';
const API_URL = '';
export function StockScreener() {
  const [rows, setRows] = useState<any[]>([]);
  useEffect(() => { fetch(`${API_URL}/screener`).then((r) => r.json()).then(setRows); }, []);
  return <div style={{ padding: 16 }}><h2>Screener</h2><ul>{rows.map((r) => <li key={r.symbol}>{r.rank}. {r.symbol} {r.signal} {r.pnl_pct}%</li>)}</ul></div>;
}
