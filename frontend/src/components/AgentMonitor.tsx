import React, { useEffect, useRef, useState } from 'react';

interface AgentState {
  agent_id: string;
  status: string;
  task: string;
  progress: number;
}

export function AgentMonitor() {
  const [agents, setAgents] = useState<Record<string, AgentState>>({});
  const [wsError, setWsError] = useState(false);
  const reconnectRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const maxReconnect = 10;

  useEffect(() => {
    let ws: WebSocket | null = null;
    let reconnectCount = 0;

    function connect() {
      try {
        const token = localStorage.getItem('access_token') || '';
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        ws = new WebSocket(`${protocol}//${window.location.host}/ws/agent-monitor?token=${encodeURIComponent(token)}`);
        ws.onopen = () => {
          setWsError(false);
          reconnectCount = 0;
        };
        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            if (data.agent_id) {
              setAgents((prev) => ({ ...prev, [data.agent_id]: data }));
            }
          } catch {
            // ignore non-JSON messages
          }
        };
        ws.onerror = () => setWsError(true);
        ws.onclose = (event) => {
          setWsError(true);
          if (event.code === 4001) {
            localStorage.removeItem('access_token');
            localStorage.removeItem('username');
            window.location.reload();
            return;
          }
          if (reconnectCount < maxReconnect) {
            reconnectCount++;
            reconnectRef.current = setTimeout(connect, Math.min(1000 * Math.pow(2, reconnectCount), 30000));
          }
        };
      } catch {
        setWsError(true);
        if (reconnectCount < maxReconnect) {
          reconnectCount++;
          reconnectRef.current = setTimeout(connect, Math.min(1000 * Math.pow(2, reconnectCount), 30000));
        }
      }
    }

    connect();
    return () => {
      if (ws) ws.close();
      if (reconnectRef.current) clearTimeout(reconnectRef.current);
    };
  }, []);

  return (
    <div className="space-y-2">
      <div className="text-xs uppercase tracking-wider text-gray-400 font-semibold">Agent Monitor</div>
      {wsError && <div className="text-gray-600 text-xs">WebSocket unavailable</div>}
      {Object.values(agents).length === 0 && !wsError ? <div className="text-gray-500 text-sm">No agents online</div> : null}
      {Object.values(agents).map((a) => (
        <div key={a.agent_id} className="bg-gray-900 border border-gray-800 rounded p-3">
          <div className="flex items-center justify-between gap-2">
            <div className="font-semibold text-sm">{a.agent_id}</div>
            <div className="text-xs text-gray-300">{a.status}</div>
          </div>
          <div className="text-xs text-gray-400 mt-1">{a.task}</div>
          <div className="mt-2 h-1 bg-gray-800 rounded overflow-hidden">
            <div className="h-full bg-blue-500" style={{ width: `${Math.max(0, Math.min(100, a.progress || 0))}%` }} />
          </div>
        </div>
      ))}
    </div>
  );
}
