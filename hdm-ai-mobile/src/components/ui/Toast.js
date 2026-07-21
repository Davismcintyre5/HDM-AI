import React, { createContext, useContext, useState, useCallback, useRef } from 'react';
import { View, Text, Animated, StyleSheet } from 'react-native';
import { CheckCircle, XCircle, AlertCircle } from 'lucide-react-native';

const ToastContext = createContext(null);

export function ToastProvider({ children }) {
  const [toast, setToast] = useState(null);
  const opacity = useRef(new Animated.Value(0)).current;

  const addToast = useCallback((message, type = 'success') => {
    setToast({ message, type });
    Animated.sequence([
      Animated.timing(opacity, { toValue: 1, duration: 200, useNativeDriver: true }),
      Animated.delay(2500),
      Animated.timing(opacity, { toValue: 0, duration: 300, useNativeDriver: true }),
    ]).start(() => setToast(null));
  }, []);

  const icons = {
    success: <CheckCircle size={18} color="#22c55e" />,
    error: <XCircle size={18} color="#ef4444" />,
    info: <AlertCircle size={18} color="#3b82f6" />,
  };

  return (
    <ToastContext.Provider value={{ addToast }}>
      {children}
      {toast && (
        <Animated.View style={[styles.toast, { opacity }]}>
          {icons[toast.type]}
          <Text style={styles.text}>{toast.message}</Text>
        </Animated.View>
      )}
    </ToastContext.Provider>
  );
}

export const useToast = () => useContext(ToastContext);

const styles = StyleSheet.create({
  toast: {
    position: 'absolute', bottom: 40, left: 20, right: 20,
    backgroundColor: '#1a1a1a', borderWidth: 1, borderColor: '#2a2a2a',
    borderRadius: 12, padding: 14, flexDirection: 'row', alignItems: 'center', gap: 10,
    zIndex: 9999, elevation: 10,
  },
  text: { color: '#fff', fontSize: 13, flex: 1 },
});