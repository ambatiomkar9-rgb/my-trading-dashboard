import React, { useEffect, useMemo, useState } from 'react';

interface AgentMetrics {
  response_time: number;
  agent_processing: number;
  llm_generation: number;
  network_latency: number;
}

interface AgentCard {
  agent_id: string;
  status: string;
  task: string;
  progress: number;
}

export function AgentAnimationView() {
  const [metrics, setMetrics] = useState<AgentMetrics | null>(null);
  const [agents, setAgents] = useState<Record<string, AgentCard>>({});

  useEffect(() => {
    const token = localStorage.getItem('access_token') || '';
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const ws = new WebSocket(`${protocol}//${window.location.host}/ws/agent-monitor?token=${encodeURIComponent(token)}`);
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data) as Partial<AgentCard>;
        if (data?.agent_id) {
          setAgents((prev) => ({
            ...prev,
            [data.agent_id as string]: {
              agent_id: data.agent_id as string,
              status: String(data.status || 'offline'),
              task: String(data.task || ''),
              progress: Number(data.progress || 0),
            },
          }));
        }
      } catch {
        // Ignore malformed updates.
      }
      setMetrics({
        response_time: Math.random() * 3,
        agent_processing: Math.random() * 2,
        llm_generation: Math.random() * 1.5,
        network_latency: Math.random() * 0.5,
      });
    };
    return () => ws.close();
  }, []);

  const liveAgents = useMemo(
    () => Object.values(agents).sort((a, b) => a.agent_id.localeCompare(b.agent_id)),
    [agents],
  );

  const statusClass = (status: string) => {
    const value = status.toLowerCase();
    if (['online', 'running'].includes(value)) return 'text-green-400 border-green-800 bg-green-950/30';
    if (['paused', 'idle', 'waiting'].includes(value)) return 'text-yellow-300 border-yellow-900 bg-yellow-950/30';
    if (['backtested', 'processing'].includes(value)) return 'text-blue-300 border-blue-900 bg-blue-950/30';
    return 'text-gray-300 border-gray-800 bg-gray-900';
  };

  return (
    <div className="p-6 bg-black text-white">
      <h1 className="text-3xl font-bold mb-6">Agent Orchestration</h1>

      <div className="bg-gray-900 p-6 rounded-lg mb-6 overflow-auto">
        <svg width="100%" height="400" viewBox="0 0 600 400" className="mx-auto">
          <rect x="50" y="20" width="120" height="50" fill="#1f2937" stroke="#3b82f6" strokeWidth="2" rx="5" />
          <text x="110" y="50" textAnchor="middle" fill="white" fontSize="12" fontWeight="bold">
            User Input
          </text>

          <rect x="230" y="20" width="120" height="50" fill="#1f2937" stroke="#3b82f6" strokeWidth="2" rx="5" />
          <text x="290" y="50" textAnchor="middle" fill="white" fontSize="12" fontWeight="bold">
            Dashboard
          </text>

          <rect x="230" y="120" width="120" height="50" fill="#1f2937" stroke="#8b5cf6" strokeWidth="2" rx="5" />
          <text x="290" y="150" textAnchor="middle" fill="white" fontSize="12" fontWeight="bold">
            Boss Agent
          </text>

          <rect x="50" y="120" width="120" height="50" fill="#1f2937" stroke="#ec4899" strokeWidth="2" rx="5" />
          <text x="110" y="145" textAnchor="middle" fill="white" fontSize="12" fontWeight="bold">
            Ollama LLM
          </text>
          <text x="110" y="160" textAnchor="middle" fill="#ec4899" fontSize="10">
            local models
          </text>

          <rect x="20" y="240" width="90" height="40" fill="#1f2937" stroke="#10b981" strokeWidth="2" rx="5" />
          <text x="65" y="265" textAnchor="middle" fill="white" fontSize="11" fontWeight="bold">
            Technical
          </text>

          <rect x="125" y="240" width="90" height="40" fill="#1f2937" stroke="#10b981" strokeWidth="2" rx="5" />
          <text x="170" y="265" textAnchor="middle" fill="white" fontSize="11" fontWeight="bold">
            Whale
          </text>

          <rect x="230" y="240" width="90" height="40" fill="#1f2937" stroke="#10b981" strokeWidth="2" rx="5" />
          <text x="275" y="265" textAnchor="middle" fill="white" fontSize="11" fontWeight="bold">
            Macro
          </text>

          <rect x="335" y="240" width="90" height="40" fill="#1f2937" stroke="#10b981" strokeWidth="2" rx="5" />
          <text x="380" y="265" textAnchor="middle" fill="white" fontSize="11" fontWeight="bold">
            News
          </text>

          <rect x="180" y="340" width="240" height="40" fill="#1f2937" stroke="#f59e0b" strokeWidth="2" rx="5" />
          <text x="300" y="365" textAnchor="middle" fill="white" fontSize="12" fontWeight="bold">
            Event Bus
          </text>

          <line x1="110" y1="70" x2="230" y2="20" stroke="#3b82f6" strokeWidth="2" markerEnd="url(#arrowblue)" />
          <line x1="290" y1="70" x2="290" y2="120" stroke="#3b82f6" strokeWidth="2" markerEnd="url(#arrowblue)" />
          <line x1="230" y1="145" x2="170" y2="145" stroke="#8b5cf6" strokeWidth="2" markerEnd="url(#arrowpurple)" />
          <line x1="290" y1="170" x2="290" y2="240" stroke="#8b5cf6" strokeWidth="2" markerEnd="url(#arrowpurple)" />
          <line x1="65" y1="280" x2="210" y2="340" stroke="#10b981" strokeWidth="2" markerEnd="url(#arrowgreen)" />
          <line x1="170" y1="280" x2="240" y2="340" stroke="#10b981" strokeWidth="2" markerEnd="url(#arrowgreen)" />
          <line x1="275" y1="280" x2="290" y2="340" stroke="#10b981" strokeWidth="2" markerEnd="url(#arrowgreen)" />
          <line x1="380" y1="280" x2="350" y2="340" stroke="#10b981" strokeWidth="2" markerEnd="url(#arrowgreen)" />

          <defs>
            <marker id="arrowblue" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
              <path d="M0,0 L0,6 L9,3 z" fill="#3b82f6" />
            </marker>
            <marker id="arrowpurple" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
              <path d="M0,0 L0,6 L9,3 z" fill="#8b5cf6" />
            </marker>
            <marker id="arrowgreen" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
              <path d="M0,0 L0,6 L9,3 z" fill="#10b981" />
            </marker>
          </defs>
        </svg>
      </div>

      {metrics ? (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
          <div className="bg-gray-900 p-4 rounded">
            <p className="text-gray-400 text-sm">Response Time</p>
            <p className="text-2xl font-bold text-blue-400">{metrics.response_time.toFixed(2)}s</p>
          </div>
          <div className="bg-gray-900 p-4 rounded">
            <p className="text-gray-400 text-sm">Agent Processing</p>
            <p className="text-2xl font-bold text-purple-400">{metrics.agent_processing.toFixed(2)}s</p>
          </div>
          <div className="bg-gray-900 p-4 rounded">
            <p className="text-gray-400 text-sm">LLM Generation</p>
            <p className="text-2xl font-bold text-pink-400">{metrics.llm_generation.toFixed(2)}s</p>
          </div>
          <div className="bg-gray-900 p-4 rounded">
            <p className="text-gray-400 text-sm">Network Latency</p>
            <p className="text-2xl font-bold text-amber-400">{metrics.network_latency.toFixed(2)}s</p>
          </div>
        </div>
      ) : null}

      <div className="bg-gray-900 p-4 rounded">
        <h3 className="text-lg font-bold mb-4">Event Timeline</h3>
        <div className="space-y-2 text-sm">
          <div className="flex gap-4">
            <span className="font-mono text-green-400 w-20">00:00</span>
            <span>User sends command: &quot;analyze INFY&quot;</span>
          </div>
          <div className="flex gap-4">
            <span className="font-mono text-blue-400 w-20">00:01</span>
            <span>Boss Agent receives request</span>
          </div>
          <div className="flex gap-4">
            <span className="font-mono text-purple-400 w-20">00:02</span>
            <span>Technical Agent starts analysis</span>
          </div>
          <div className="flex gap-4">
            <span className="font-mono text-pink-400 w-20">00:03</span>
            <span>Ollama LLM generating response...</span>
          </div>
          <div className="flex gap-4">
            <span className="font-mono text-amber-400 w-20">00:04</span>
            <span>Response sent to dashboard</span>
          </div>
        </div>
      </div>

      <div className="bg-gray-900 p-4 rounded mt-6">
        <h3 className="text-lg font-bold mb-4">Live Agent Status</h3>
        {liveAgents.length === 0 ? (
          <div className="text-gray-500 text-sm">Waiting for the backend to send live agent updates...</div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {liveAgents.map((agent) => (
              <div key={agent.agent_id} className={`rounded border p-3 ${statusClass(agent.status)}`}>
                <div className="flex items-center justify-between gap-3">
                  <div className="font-semibold text-sm">{agent.agent_id}</div>
                  <div className="text-xs uppercase tracking-wide">{agent.status}</div>
                </div>
                <div className="text-xs text-gray-300 mt-2">{agent.task}</div>
                <div className="mt-2 h-1 bg-gray-800 rounded overflow-hidden">
                  <div className="h-full bg-current" style={{ width: `${Math.max(0, Math.min(100, agent.progress || 0))}%` }} />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// Back-compat for existing import in App.tsx
export const AgentAnimation = AgentAnimationView;
