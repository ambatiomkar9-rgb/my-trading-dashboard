import React, { useState } from 'react';
import { apiFetch } from '../api';

export function ChatInterface() {
  const [message, setMessage] = useState('');
  const [history, setHistory] = useState<Array<{ role: string; content: string }>>([]);
  const [loading, setLoading] = useState(false);

  const safeJson = async (res: Response): Promise<any> => {
    const text = await res.text();
    try {
      return text ? JSON.parse(text) : {};
    } catch {
      return { raw: text };
    }
  };

  const pollResponse = async (commandId: string, attempts = 240): Promise<string> => {
    for (let i = 0; i < attempts; i += 1) {
      try {
        const data = await apiFetch(`/chat/response/${commandId}`);
        if (data.status === 'done' && data.response) return data.response;
      } catch {
        // transient poll failure
      }
      await new Promise((r) => setTimeout(r, 500));
    }
    return 'Agent timed out. Please retry.';
  };

  const sendMessage = async () => {
    if (!message.trim()) return;
    const userMessage = message;
    setMessage('');
    setLoading(true);
    setHistory((p) => [...p, { role: 'user', content: userMessage }, { role: 'assistant', content: 'Agent Processing...' }]);

    try {
      const data = await apiFetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage }),
      });
      if (!data.command_id) {
        throw new Error(data?.detail || 'No command_id returned');
      }
      const ans = await pollResponse(data.command_id);
      setHistory((p) => {
        const n = [...p];
        n[n.length - 1] = { role: 'assistant', content: ans };
        return n;
      });
    } catch (err: any) {
      setHistory((p) => {
        const n = [...p];
        n[n.length - 1] = { role: 'assistant', content: `Error sending message: ${err?.message || 'Unknown error'}` };
        return n;
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <h2 style={{ margin: '0 0 12px' }}>Chat</h2>
      <div style={{ flex: 1, overflowY: 'auto', padding: 8, background: '#111', borderRadius: 8 }}>
        {history.map((m, i) => (
          <div key={i} style={{ marginBottom: 8 }}>
            <strong style={{ color: m.role === 'user' ? '#60a5fa' : '#4ade80' }}>
              {m.role === 'user' ? 'You' : 'Agent'}
            </strong>
            <div style={{ color: '#e5e7eb', whiteSpace: 'pre-wrap' }}>{m.content}</div>
          </div>
        ))}
      </div>
      <div style={{ display: 'flex', marginTop: 8, gap: 8 }}>
        <input
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && !loading && sendMessage()}
          placeholder="Ask: analyze INFY, backtest BTC, generate PineScript strategy..."
          style={{ flex: 1, padding: 10, borderRadius: 8, border: '1px solid #333', background: '#1a1a2e', color: '#fff' }}
          disabled={loading}
        />
        <button
          onClick={sendMessage}
          disabled={loading || !message.trim()}
          style={{ padding: '10px 20px', borderRadius: 8, background: '#2563eb', color: '#fff', border: 'none', cursor: 'pointer' }}
        >
          Send
        </button>
      </div>
    </div>
  );
}
