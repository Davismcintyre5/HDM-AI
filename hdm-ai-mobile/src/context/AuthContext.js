import React, { createContext, useContext, useState, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import api from '../api/axios';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      const token = await AsyncStorage.getItem('token');
      const savedUser = await AsyncStorage.getItem('user');
      if (token && savedUser) {
        try { setUser(JSON.parse(savedUser)); } catch { setUser(null); }
      }
      setLoading(false);
    })();
  }, []);

  const login = async (email, password) => {
    const { data } = await api.post('/auth/login', { email, password });
    const userData = { email: data.data.email, username: data.data.username, role: data.data.role };
    await AsyncStorage.setItem('token', data.data.accessToken);
    await AsyncStorage.setItem('user', JSON.stringify(userData));
    setUser(userData);
    return data.data;
  };

  const register = async (email, username, password) => {
    const { data } = await api.post('/auth/register', { email, username, password });
    return data;
  };

  const verifyEmail = async (token) => {
    const { data } = await api.post('/auth/verify-email', { token });
    if (data.data?.accessToken) {
      const userData = { email: data.data.email, username: data.data.username, role: data.data.role };
      await AsyncStorage.setItem('token', data.data.accessToken);
      await AsyncStorage.setItem('user', JSON.stringify(userData));
      setUser(userData);
    }
    return data;
  };

  const logout = async () => {
    await AsyncStorage.multiRemove(['token', 'user']);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, verifyEmail, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);