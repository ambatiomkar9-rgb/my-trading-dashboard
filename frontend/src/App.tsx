import React, { useState, useEffect } from 'react';
import './App.css';

interface AgentState {
  agent_id: string;
  status: string;
  task: string;
  progress: number;
  skills?: string[];
  cpu_percent?: number;
  memory_mb?: number;
  timestamp?: string;
}

function App() {
  const [agents, setAgents] = useState<Record<string, AgentState>>({});
  const [message, setMessage] = useState('');
  const [chatHistory, setChatHistory] = useState<Array<{role: string, content: string}>>([]);
  const [loading, setLoading] = useState(false);

  // Connect to WebSocket for live agent updates
  useEffect(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/agent-monitor`;
    
    try {
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        console.log('✓ WebSocket connected');
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.agent_id) {
            setAgents(prev => ({
              ...prev,
              [data.agent_id]: data
            }));
          }
        } catch (e) {
          console.error('WebSocket parse error:', e);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      ws.onclose = () => {
        console.log('WebSocket disconnected - will reconnect...');
        setTimeout(() => {
          window.location.reload();
        }, 5000);
      };

      return () => ws.close();
    } catch (error) {
      console.error('WebSocket setup error:', error);
    }
  }, []);

  // Send chat message
  const handleSendMessage = async () => {
    if (!message.trim()) return;

    setLoading(true);
    setChatHistory(prev => [...prev, { role: 'user', content: message }]);
    const userMessage = message;
    setMessage('');

    try {
      const response = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setChatHistory(prev => [...prev, { role: 'assistant', content: data.response }]);
    } catch (error) {
      console.error('Chat error:', error);
      setChatHistory(prev => [...prev, { role: 'assistant', content: 'Error: Could not reach server. Make sure backend is running.' }]);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch(status) {
      case 'online':
      case 'idle':
        return 'online';
      case 'processing':
        return 'processing';
      case 'error':
        return 'error';
      default:
        return 'idle';
    }
  };

  return (
    <div className="app">
      <div className="container">
        {/* Agent Monitor Sidebar */}
        <div className="sidebar">
          <h2>🤖 Agent Monitor</h2>
          <div className="agents-list">
            {Object.entries(agents).length === 0 ? (
              <div style={{ padding: '20px', textAlign: 'center', color: '#999' }}>
                <p>No agents connected yet</p>
                <p style={{ fontSize: '12px', marginTop: '10px' }}>Start your agents to see them here</p>
              </div>
            ) : (
              Object.entries(agents).map(([id, agent]) => (
                <div key={id} className={`agent-item ${getStatusColor(agent.status)}`}>
                  <div className="agent-name">
                    {agent.status === 'processing' ? '⟳ ' : '✓ '}
                    {id}
                  </div>
                  <div className="agent-status">Status: {agent.status}</div>
                  <div className="agent-task">{agent.task || 'Idle'}</div>
                  <div className="progress-bar" style={{width: `${agent.progress || 0}%`}}></div>
                  {agent.skills && agent.skills.length > 0 && (
                    <div style={{ fontSize: '11px', color: '#666', marginTop: '6px' }}>
                      Skills: {agent.skills.join(', ')}
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>

        {/* Main Chat Area */}
        <div className="main">
          <h1>Trading Dashboard</h1>
          
          <div className="chat-container">
            <div className="chat-messages">
              {chatHistory.length === 0 ? (
                <div style={{ textAlign: 'center', color: '#999', padding: '40px' }}>
                  <h2>Welcome to Trading Dashboard</h2>
                  <p style={{ marginTop: '20px' }}>Try these commands:</p>
                  <ul style={{ listStyle: 'none', marginTop: '20px', lineHeight: '1.8' }}>
                    <li>💬 "analyze INFY 4h"</li>
                    <li>📊 "backtest RSI strategy on RELIANCE"</li>
                    <li>🔍 "stock screener top 10"</li>
                    <li>💰 "what are whales doing in BTC"</li>
                    <li>📝 "generate Pine Script for momentum"</li>
                  </ul>
                </div>
              ) : (
                chatHistory.map((msg, idx) => (
                  <div key={idx} className={`message ${msg.role}`}>
                    <div className="message-content">{msg.content}</div>
                  </div>
                ))
              )}
              {loading && (
                <div className="message assistant">
                  <div className="message-content">⟳ Processing...</div>
                </div>
              )}
            </div>

            <div className="chat-input">
              <input
                type="text"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter' && !loading) {
                    handleSendMessage();
                  }
                }}
                placeholder="Type a command... (e.g., 'analyze INFY 4h')"
                disabled={loading}
              />
              <button onClick={handleSendMessage} disabled={loading}>
                {loading ? 'Sending...' : 'Send'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;