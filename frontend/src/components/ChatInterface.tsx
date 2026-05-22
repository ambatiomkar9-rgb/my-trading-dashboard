import React, { useState } from 'react';

const API_URL = '';

export function ChatInterface() {
  const [message, setMessage] = useState('');
  const [history, setHistory] = useState<Array<{ role: string; content: string }>>([]);
  const [loading, setLoading] = useState(false);

  const pollResponse = async (commandId: string, attempts = 240): Promise<string> => {
    for (let i = 0; i < attempts; i += 1) {
      const res = await fetch(`${API_URL}/chat/response/${commandId}`);
      const data = await res.json();
      if (data.status === 'done' && data.response) return data.response;
      await new Promise((r) => setTimeout(r, 500));
    }
    return 'Agent timeout';
  };

  const sendMessage = async () => {
    if (!message.trim()) return;
    const userMessage = message;
    setMessage('');
    setLoading(true);
    setHistory((p) => [...p, { role: 'user', content: userMessage }, { role: 'assistant', content: 'Agent Processing...' }]);

    try {
      const res = await fetch(`${API_URL}/chat`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message: userMessage }),
      });
      const data = await res.json();
      const ans = await pollResponse(data.command_id);
      setHistory((p) => {
        const n = [...p];
        n[n.length - 1] = { role: 'assistant', content: ans };
        return n;
      });
    } catch {
      setHistory((p) => {
        const n = [...p];
        n[n.length - 1] = { role: 'assistant', content: 'Error sending message' };
        return n;
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: 16 }}>
      <h3>Chat Interface</h3>
      <div style={{ minHeight: 240, background: '#111', padding: 8, borderRadius: 8, marginBottom: 8 }}>
        {history.map((m, i) => <div key={i}><b>{m.role}:</b> {m.content}</div>)}
      </div>
      <input value={message} onChange={(e) => setMessage(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && !loading && sendMessage()} />
      <button onClick={sendMessage} disabled={loading}>{loading ? 'Sending...' : 'Send'}</button>
    </div>
  );
}
