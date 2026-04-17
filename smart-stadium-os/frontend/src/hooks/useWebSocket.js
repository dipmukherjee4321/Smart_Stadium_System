import { useState, useEffect, useCallback, useRef } from 'react';

/**
 * Enterprise WebSocket Hook
 * handles connection lifecycle, automatic reconnection with exponential backoff,
 * and structured event parsing.
 */
export default function useWebSocket(url) {
  const [data, setData] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const socketRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const reconnectAttempts = useRef(0);

  const connect = useCallback(() => {
    if (socketRef.current?.readyState === WebSocket.OPEN) return;

    // Determine absolute WebSocket URL
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const wsUrl = url.startsWith('ws') ? url : `${protocol}//${host}${url}`;

    const socket = new WebSocket(wsUrl);
    socketRef.current = socket;

    socket.onopen = () => {
      console.log('✅ WebSocket Connected');
      setIsConnected(true);
      reconnectAttempts.current = 0;
    };

    socket.onmessage = (event) => {
      try {
        const parsed = JSON.parse(event.data);
        setData(parsed);
      } catch (err) {
        console.error('❌ WebSocket message parse error:', err);
      }
    };

    socket.onclose = () => {
      console.log('⚠️ WebSocket Disconnected');
      setIsConnected(false);
      
      // Exponential backoff reconnection (max 30s)
      const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 30000);
      reconnectTimeoutRef.current = setTimeout(() => {
        reconnectAttempts.current += 1;
        connect();
      }, delay);
    };

    socket.onerror = (err) => {
      console.error('❌ WebSocket Error:', err);
      socket.close();
    };
  }, [url]);

  useEffect(() => {
    connect();
    return () => {
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
      if (socketRef.current) socketRef.current.close();
    };
  }, [connect]);

  return { data, isConnected };
}
