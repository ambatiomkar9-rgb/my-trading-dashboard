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
    return content
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/`(.+?)`/g, '<code style="background:#1e293b;padding:1px 4px;border-radius:3px">$1</code>')
      .replace(/\n/g, '<br/>');
  };

  return (
    <div className="flex flex-col h-full p-4">
      <h2 className="text-lg font-bold mb-3" style={{color:'var(--accent)'}}>Boss Agent Chat</h2>
      <div className="flex-1 overflow-y-auto rounded-lg p-3 mb-3" style={{background:'var(--surface)', border:'1px solid var(--border)'}}>
        {history.length === 0 && (
          <div className="flex items-center justify-center h-full">
            <div className="text-center" style={{color:'var(--text-dim)'}}>
              <p className="text-lg font-semibold mb-2" style={{color:'var(--accent)'}}>Boss Agent</p>
              <p style={{fontSize:12}}>Ask me to analyze stocks, manage your watchlist, check portfolio, generate strategies, and more.</p>
            </div>
          </div>
        )}
        {history.map((m, i) => (
          <div
            key={i}
            className="mb-3 p-3 rounded-lg"
            style={{
              background: m.role === 'user' ? 'var(--panel-2)' : 'var(--panel)',
              border: '1px solid var(--border)',
            }}
          >
            <div className="mb-1">
              <strong style={{color: m.role === 'user' ? 'var(--accent)' : 'var(--green)', fontSize:12}}>
                {m.role === 'user' ? 'You' : 'Boss Agent'}
              </strong>
              {m.timestamp && (
                <span className="ml-2" style={{color:'var(--text-dim)', fontSize:10}}>
                  {new Date(m.timestamp).toLocaleTimeString()}
                </span>
              )}
            </div>
            <div
              style={{color:'var(--text)', fontSize:14, lineHeight:1.5}}
              dangerouslySetInnerHTML={{ __html: formatMessage(m.content) }}
            />
          </div>
        ))}
        <div ref={historyEndRef} />
      </div>
      <div className="flex gap-2">
        <input
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && !loading && sendMessage()}
          placeholder="Analyze INFY, add TCS to watchlist, show portfolio..."
          className="flex-1 input"
          style={{padding:10}}
          disabled={loading}
        />
        <button
          onClick={sendMessage}
          disabled={loading || !message.trim()}
          className="btn btn-accent"
          style={{padding:'10px 20px'}}
        >
          {loading ? '...' : 'Send'}
        </button>
      </div>
    </div>
  );
}
