import React, { useEffect, useState } from 'react';
import { TradingPage } from './components/TradingPage';
import { StrategiesPage } from './components/StrategiesPage';
import { BacktestingPage } from './components/BacktestingPage';
import { StockScreener } from './components/StockScreener';
import { SettingsPage } from './components/SettingsPage';
import { AgentAnimation } from './components/AgentAnimation';

const API_URL = '';

type Page = 'chat' | 'trading' | 'strategies' | 'backtesting' | 'screener' | 'settings' | 'animation';

interface AgentState {
  agent_id: string;
  status: string;
  task: string;
  progress: number;
}

function App() {
  const [page, setPage] = useState<Page>('chat');
  const [agents, setAgents] = useState<Record<string, AgentState>>({});
  const [message, setMessage] = useState('');
  const [chatHistory, setChatHistory] = useState<Array<{ role: string; content: string }>>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/agent-monitor`;
    const ws = new WebSocket(wsUrl);
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.agent_id) {
        setAgents((prev) => ({ ...prev, [data.agent_id]: data }));
      }
    };
    return () => ws.close();
  }, []);

  const pollResponse = async (commandId: string, attempts = 20): Promise<string> => {
    for (let i = 0; i < attempts; i += 1) {
      const res = await fetch(`${API_URL}/chat/response/${commandId}`);
      const data = await res.json();
      if (data.status === 'done' && data.response) return data.response;
      await new Promise((r) => setTimeout(r, 500));
    }
    return 'Agent timed out. Please retry.';
  };

  const handleSendMessage = async () => {
    if (!message.trim()) return;
    const userMessage = message;
    setMessage('');
    setLoading(true);
    setChatHistory((p) => [...p, { role: 'user', content: userMessage }, { role: 'assistant', content: 'Agent Processing...' }]);

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage }),
      });
      const data = await response.json();
      const finalResponse = await pollResponse(data.command_id);
      setChatHistory((p) => {
        const next = [...p];
        next[next.length - 1] = { role: 'assistant', content: finalResponse };
        return next;
      });
    } catch {
      setChatHistory((p) => {
        const next = [...p];
        next[next.length - 1] = { role: 'assistant', content: 'Error sending command.' };
        return next;
      });
    } finally {
      setLoading(false);
    }
  };

  const renderPage = () => {
    switch (page) {
      case 'trading': return <TradingPage />;
      case 'strategies': return <StrategiesPage />;
      case 'backtesting': return <BacktestingPage />;
      case 'screener': return <StockScreener />;
      case 'settings': return <SettingsPage />;
      case 'animation': return <AgentAnimation />;
      default:
        return (
          <div style={{ padding: 16 }}>
            <h2>Chat</h2>
            <div style={{ minHeight: 320, background: '#121212', padding: 12, borderRadius: 8, marginBottom: 12 }}>
              {chatHistory.map((m, i) => <div key={i}><b>{m.role}:</b> {m.content}</div>)}
            </div>
            <div style={{ display: 'flex', gap: 8 }}>
              <input style={{ flex: 1 }} value={message} onChange={(e) => setMessage(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && !loading && handleSendMessage()} />
              <button onClick={handleSendMessage} disabled={loading}>{loading ? 'Sending...' : 'Send'}</button>
            </div>
          </div>
        );
    }
  };

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '240px 1fr', minHeight: '100vh', background: '#000', color: '#fff' }}>
      <aside style={{ borderRight: '1px solid #222', padding: 12 }}>
        <h3>Agent Monitor</h3>
        {Object.values(agents).map((a) => <div key={a.agent_id} style={{ marginBottom: 8, padding: 8, background: '#111', borderRadius: 6 }}>{a.agent_id}: {a.status}</div>)}
        <hr style={{ borderColor: '#333' }} />
        {(['chat', 'trading', 'strategies', 'backtesting', 'screener', 'settings', 'animation'] as Page[]).map((p) => (
          <button key={p} onClick={() => setPage(p)} style={{ width: '100%', marginBottom: 8, padding: 8, background: page === p ? '#2563eb' : '#111', color: '#fff', border: 'none', borderRadius: 6 }}>
            {p}
          </button>
        ))}
      </aside>
      <main>{renderPage()}</main>
    </div>
  );
}

export default App;
