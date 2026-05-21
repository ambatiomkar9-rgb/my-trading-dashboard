import React, { useEffect, useState } from 'react';

interface AgentState {
  agent_id: string;
  status: string;
  task: string;
  progress: number;
}

export function AgentMonitor() {
  const [agents, setAgents] = useState<Record<string, AgentState>>({});

  useEffect(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const ws = new WebSocket(`${protocol}//${window.location.host}/ws/agent-monitor`);
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.agent_id) {
        setAgents((prev) => ({ ...prev, [data.agent_id]: data }));
      }
    };
    return () => ws.close();
  }, []);

  return (
    <div style={{ padding: 16 }}>
      <h3>Agent Monitor</h3>
      {Object.values(agents).length === 0 ? <p>No agents online</p> : null}
      {Object.values(agents).map((a) => (
        <div key={a.agent_id} style={{ background: '#111', marginBottom: 8, padding: 8, borderRadius: 6 }}>
          <div><b>{a.agent_id}</b> - {a.status}</div>
          <div>{a.task}</div>
          <div>Progress: {a.progress}%</div>
        </div>
      ))}
    </div>
  );
}
