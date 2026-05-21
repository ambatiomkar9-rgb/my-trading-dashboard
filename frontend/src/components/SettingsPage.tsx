import React, { useEffect, useState } from 'react';
const API_URL = '';
export function SettingsPage() {
  const [settings, setSettings] = useState<any>({});
  useEffect(() => { fetch(`${API_URL}/settings`).then((r) => r.json()).then(setSettings); }, []);
  const save = async () => { await fetch(`${API_URL}/settings`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(settings) }); alert('Saved'); };
  return <div style={{ padding: 16 }}><h2>Settings</h2><input value={settings.ollama_model || ''} onChange={(e) => setSettings({ ...settings, ollama_model: e.target.value })} /><button onClick={save}>Save</button></div>;
}
