import React, { useEffect, useState, useCallback } from 'react';

interface Toast {
  id: number;
  message: string;
}

let _toastId = 0;
let _addToast: ((msg: string) => void) | null = null;

export function showToast(message: string) {
  _addToast?.(message);
}

export function ToastContainer() {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const addToast = useCallback((message: string) => {
    const id = ++_toastId;
    setToasts((prev) => [...prev, { id, message }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 5000);
  }, []);

  useEffect(() => {
    _addToast = addToast;
    const handler = (e: Event) => {
      const detail = (e as CustomEvent).detail;
      addToast(typeof detail === 'string' ? detail : 'Unknown error');
    };
    window.addEventListener('api-error', handler);
    return () => {
      _addToast = null;
      window.removeEventListener('api-error', handler);
    };
  }, [addToast]);

  if (toasts.length === 0) return null;

  return (
    <div style={{
      position: 'fixed', top: 12, right: 12, zIndex: 10000,
      display: 'flex', flexDirection: 'column', gap: 8, maxWidth: 400,
    }}>
      {toasts.map((t) => (
        <div
          key={t.id}
          style={{
            background: '#1a1a2e', border: '1px solid #ff3b5c',
            borderRadius: 6, padding: '10px 14px',
            color: '#ff6b7a', fontSize: 13, lineHeight: 1.4,
            boxShadow: '0 4px 20px rgba(0,0,0,0.5)',
            animation: 'slide-in 0.2s ease-out',
          }}
        >
          {t.message}
        </div>
      ))}
    </div>
  );
}
