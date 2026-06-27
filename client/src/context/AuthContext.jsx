import { createContext, useContext, useState, useEffect } from 'react';
import api from '../api/axios';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    const savedUser = localStorage.getItem('user');
    if (token && savedUser) {
      try {
        setUser(JSON.parse(savedUser));
      } catch {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
      }
    }
    setLoading(false);
  }, []);

  const login = async (email, password) => {
    const { data } = await api.post('/auth/login', { email, password });
    const userData = { email: data.data.email, username: data.data.username, role: data.data.role };
    localStorage.setItem('token', data.data.accessToken);
    localStorage.setItem('user', JSON.stringify(userData));
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
      localStorage.setItem('token', data.data.accessToken);
      localStorage.setItem('user', JSON.stringify(userData));
      setUser(userData);
    }
    return data;
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
  };

  const value = { user, loading, login, register, verifyEmail, logout };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (ctx === null) {
    return { user: null, loading: true, login: () => {}, register: () => {}, verifyEmail: () => {}, logout: () => {} };
  }
  return ctx;
};