import React, { useState } from 'react';

const API_URL = '';

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
        const res = await fetch(`${API_URL}/chat/response/${commandId}`);
        const data = await safeJson(res);
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
      const res = await fetch(`${API_URL}/chat`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message: userMessage }),
      });
      const data = await safeJson(res);
      if (!res.ok || !data.command_id) {
        const detail = data?.detail || data?.raw || `HTTP ${res.status}`;
        throw new Error(String(detail));
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
    <div className="p-6 bg-black text-white">
      <h1 className="text-3xl font-bold mb-6">Chat</h1>
      <div className="bg-gray-900 border border-gray-800 rounded-lg p-4 mb-4 min-h-[320px]">
        {history.length === 0 ? (
          <div className="text-gray-400 text-sm">Type a message to send it to the Boss Agent.</div>
        ) : null}
        <div className="space-y-3">
          {history.map((m, i) => (
            <div key={i} className="text-sm">
              <div className={`font-semibold ${m.role === 'user' ? 'text-blue-300' : 'text-green-300'}`}>
                {m.role === 'user' ? 'You' : 'Agent'}
              </div>
              <div className="text-gray-100 whitespace-pre-wrap">{m.content}</div>
            </div>
          ))}
        </div>
      </div>
      <div className="flex gap-2">
        <input
          className="flex-1 bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && !loading && sendMessage()}
          placeholder="Ask: analyze INFY, backtest BTC, generate PineScript strategy…"
        />
        <button
          onClick={sendMessage}
          disabled={loading}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 rounded font-semibold"
        >
          {loading ? 'Sending…' : 'Send'}
        </button>
      </div>
    </div>
  );
}
