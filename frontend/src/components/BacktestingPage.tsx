import React, { useState } from 'react';
const API_URL = '';
export function BacktestingPage() {
  const [result, setResult] = useState<any | null>(null);
  const run = async () => { const r = await fetch(`${API_URL}/backtest`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({}) }); setResult(await r.json()); };
  return <div style={{ padding: 16 }}><h2>Backtesting</h2><button onClick={run}>Run Backtest</button>{result && <pre>{JSON.stringify(result, null, 2)}</pre>}</div>;
}
