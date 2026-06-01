import { useState, useEffect, useCallback, useRef } from 'react';

export interface WsMessage {
  type: string;
  payload?: any;
  timestamp?: number;
}

export interface WsStatus {
  connected: boolean;
  lastMessage: WsMessage | null;
  reconnectCount: number;
}

const RECONNECT_DELAY = 3000;
const MAX_RECONNECT = 10;

export function useWebSocket(path: string = '/ws') {
  const [status, setStatus] = useState<WsStatus>({
    connected: false,
    lastMessage: null,
    reconnectCount: 0,
  });
  const [messages, setMessages] = useState<WsMessage[]>([]);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const maxReconnectRef = useRef(MAX_RECONNECT);

  const connect = useCallback(() => {
    try {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const host = window.location.host;
      const url = `${protocol}//${host}${path}`;

      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        setStatus((prev) => ({ ...prev, connected: true, reconnectCount: 0 }));
      };

      ws.onmessage = (event) => {
        try {
          const msg: WsMessage = JSON.parse(event.data);
          setMessages((prev) => [...prev.slice(-99), msg]); // Keep last 100
          setStatus((prev) => ({ ...prev, lastMessage: msg }));
        } catch {
          // Ignore malformed messages
        }
      };

      ws.onclose = () => {
        setStatus((prev) => ({ ...prev, connected: false }));
        // Reconnect
        if (maxReconnectRef.current > 0) {
          maxReconnectRef.current--;
          reconnectRef.current = setTimeout(() => {
            reconnectRef.current = null;
            connect();
          }, RECONNECT_DELAY);
        }
      };

      ws.onerror = () => {
        ws.close();
      };
    } catch {
      // Connection failed, retry
      if (maxReconnectRef.current > 0) {
        maxReconnectRef.current--;
        reconnectRef.current = setTimeout(() => {
          reconnectRef.current = null;
          connect();
        }, RECONNECT_DELAY);
      }
    }
  }, [path]);

  useEffect(() => {
    connect();
    return () => {
      if (reconnectRef.current) {
        clearTimeout(reconnectRef.current);
      }
      wsRef.current?.close();
    };
  }, [connect]);

  const send = useCallback((type: string, payload?: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type, payload, timestamp: Date.now() }));
    }
  }, []);

  return { status, messages, send };
}
