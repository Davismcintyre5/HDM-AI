import { useState, useEffect, createContext, useContext, useCallback } from 'react';
import { X, CheckCircle, AlertCircle, XCircle } from 'lucide-react';

const ToastContext = createContext(null);

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const addToast = useCallback((message, type = 'success', duration = 3000) => {
    const id = Date.now();
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => setToasts((prev) => prev.filter((t) => t.id !== id)), duration);
  }, []);

  return (
    <ToastContext.Provider value={{ addToast }}>
      {children}
      <div className="fixed bottom-4 right-4 z-50 space-y-2">
        {toasts.map((t) => (
          <div key={t.id} className="flex items-center gap-2 bg-bg-secondary border border-border rounded-lg px-4 py-3 shadow-lg animate-in slide-in-from-right">
            {t.type === 'success' && <CheckCircle className="w-4 h-4 text-success" />}
            {t.type === 'error' && <XCircle className="w-4 h-4 text-danger" />}
            {t.type === 'info' && <AlertCircle className="w-4 h-4 text-blue-400" />}
            <span className="text-sm text-text-primary">{t.message}</span>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export const useToast = () => useContext(ToastContext);