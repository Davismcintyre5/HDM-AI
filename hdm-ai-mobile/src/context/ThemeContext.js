import React, { createContext, useContext, useState, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';

const ThemeContext = createContext(null);

const THEMES = {
  dark: {
    bg: '#0a0a0a',
    bgSecondary: '#141414',
    bgTertiary: '#1a1a1a',
    text: '#ffffff',
    textSecondary: '#a0a0a0',
    textMuted: '#666666',
    border: '#2a2a2a',
    accent: '#c084fc',
    accentHover: '#a855f7',
    danger: '#ef4444',
    success: '#22c55e',
  },
  light: {
    bg: '#ffffff',
    bgSecondary: '#f5f5f5',
    bgTertiary: '#e5e5e5',
    text: '#0a0a0a',
    textSecondary: '#555555',
    textMuted: '#999999',
    border: '#d4d4d4',
    accent: '#7c3aed',
    accentHover: '#6d28d9',
    danger: '#dc2626',
    success: '#16a34a',
  },
};

export function ThemeProvider({ children }) {
  const [theme, setTheme] = useState('dark');

  useEffect(() => {
    AsyncStorage.getItem('theme').then((saved) => {
      if (saved) setTheme(saved);
    });
  }, []);

  const toggleTheme = () => {
    const next = theme === 'dark' ? 'light' : 'dark';
    setTheme(next);
    AsyncStorage.setItem('theme', next);
  };

  const colors = THEMES[theme];
  const isDark = theme === 'dark';

  return (
    <ThemeContext.Provider value={{ theme, setTheme, toggleTheme, colors, isDark }}>
      {children}
    </ThemeContext.Provider>
  );
}

export const useTheme = () => useContext(ThemeContext);