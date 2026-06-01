import React, { useEffect, useState } from 'react';

interface AgentState {
  agent_id: string;
  status: string;
  task: string;
  progress: number;
}

export function AgentMonitor() {
  const [agents, setAgents] = useState<Record<string, AgentState>>({});
  const [wsError, setWsError] = useState(false);

  useEffect(() => {
    let ws: WebSocket | null = null;
    try {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      ws = new WebSocket(`${protocol}//${window.location.host}/ws/agent-monitor`);
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
      ws.onclose = () => setWsError(true);
    } catch {
      setWsError(true);
    }
    return () => { if (ws) ws.close(); };
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
