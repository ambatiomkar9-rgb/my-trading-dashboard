import React, { useEffect, useState } from 'react';
const API_URL = '';
export function StrategiesPage() {
  const [strategies, setStrategies] = useState<any[]>([]);
  const [selected, setSelected] = useState<any | null>(null);
  const [script, setScript] = useState('');
  const load = async () => { const data = await (await fetch(`${API_URL}/strategies`)).json(); setStrategies(data); setSelected(data[0] || null); };
  useEffect(() => { load(); }, []);
  const genScript = async () => {
    const r = await fetch(`${API_URL}/strategy/pinescript/generate`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name: selected?.name || 'Generated Strategy' }) });
    const data = await r.json();
    setScript(data.script || '');
  };
  return <div style={{ padding: 16 }}><h2>Strategies</h2><table><thead><tr><th>Name</th><th>Status</th><th>PnL</th></tr></thead><tbody>{strategies.map((s) => <tr key={s.id} onClick={() => setSelected(s)}><td>{s.name}</td><td>{s.status}</td><td>{s.pnl}</td></tr>)}</tbody></table>{selected && <div><h3>{selected.name}</h3><button onClick={genScript}>Generate PineScript</button><pre style={{ whiteSpace: 'pre-wrap' }}>{script}</pre></div>}</div>;
}
