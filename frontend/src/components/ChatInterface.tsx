import React, { useState, useEffect, useRef } from 'react';
import { apiFetch } from '../api';

interface ChatMessage {
  role: string;
  content: string;
  timestamp?: string;
}

export function ChatInterface() {
  const [message, setMessage] = useState('');
  const [history, setHistory] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const historyEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadHistory();
  }, []);

  useEffect(() => {
    historyEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [history]);

  const loadHistory = async () => {
    try {
      const data = await apiFetch('/chat/history');
      if (Array.isArray(data)) {
        setHistory(data.map((m: any) => ({
          role: m.role,
          content: m.message || m.content,
          timestamp: m.timestamp,
        })));
      }
    } catch {
      // ignore — start with empty history
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
    setHistory((p) => [...p,
      { role: 'user', content: userMessage },
      { role: 'assistant', content: 'Thinking...' },
    ]);

    try {
      const data = await apiFetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage }),
      });
      if (!data.command_id) throw new Error(data?.detail || 'No command_id returned');
      const ans = await pollResponse(data.command_id);
      setHistory((p) => {
        const n = [...p];
        n[n.length - 1] = { role: 'assistant', content: ans };
        return n;
      });
    } catch (err: any) {
      setHistory((p) => {
        const n = [...p];
        n[n.length - 1] = { role: 'assistant', content: `Error: ${err?.message || 'Unknown error'}` };
        return n;
      });
    } finally {
      setLoading(false);
    }
  };

  const formatMessage = (content: string) => {
    // Simple markdown-like formatting
    return content
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/`(.+?)`/g, '<code style="background:#1e293b;padding:1px 4px;border-radius:3px">$1</code>')
      .replace(/\n/g, '<br/>');
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <h2 style={{ margin: '0 0 12px' }}>Chat</h2>
      <div style={{ flex: 1, overflowY: 'auto', padding: 8, background: '#111', borderRadius: 8 }}>
        {history.length === 0 && (
          <div style={{ color: '#666', textAlign: 'center', padding: 40 }}>
            <p style={{ fontSize: 16, marginBottom: 8 }}>Boss Agent</p>
            <p style={{ fontSize: 12 }}>Ask me to analyze stocks, manage your watchlist, check portfolio, generate strategies, and more.</p>
          </div>
        )}
        {history.map((m, i) => (
          <div key={i} style={{ marginBottom: 12, padding: '8px 12px', borderRadius: 8, background: m.role === 'user' ? '#1a1a2e' : '#0f172a', border: '1px solid #1e293b' }}>
            <div style={{ marginBottom: 4 }}>
              <strong style={{ color: m.role === 'user' ? '#60a5fa' : '#4ade80', fontSize: 12 }}>
                {m.role === 'user' ? 'You' : 'Boss Agent'}
              </strong>
              {m.timestamp && (
                <span style={{ color: '#555', fontSize: 10, marginLeft: 8 }}>
                  {new Date(m.timestamp).toLocaleTimeString()}
                </span>
              )}
            </div>
            <div
              style={{ color: '#e5e7eb', fontSize: 14, lineHeight: 1.5 }}
              dangerouslySetInnerHTML={{ __html: formatMessage(m.content) }}
            />
          </div>
        ))}
        <div ref={historyEndRef} />
      </div>
      <div style={{ display: 'flex', marginTop: 8, gap: 8 }}>
        <input
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && !loading && sendMessage()}
          placeholder="Analyze INFY, add TCS to watchlist, show portfolio..."
          style={{ flex: 1, padding: 10, borderRadius: 8, border: '1px solid #333', background: '#1a1a2e', color: '#fff' }}
          disabled={loading}
        />
        <button
          onClick={sendMessage}
          disabled={loading || !message.trim()}
          style={{ padding: '10px 20px', borderRadius: 8, background: '#2563eb', color: '#fff', border: 'none', cursor: 'pointer' }}
        >
          {loading ? '...' : 'Send'}
        </button>
      </div>
    </div>
  );
}
