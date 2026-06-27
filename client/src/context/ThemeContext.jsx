import { createContext, useContext, useState, useEffect } from 'react';

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

function ThemeProvider({ children }) {
  const [theme, setTheme] = useState(() => localStorage.getItem('theme') || 'dark');

  useEffect(() => {
    localStorage.setItem('theme', theme);
    const colors = THEMES[theme];
    const root = document.documentElement;
    Object.entries(colors).forEach(([key, value]) => {
      root.style.setProperty(`--${key}`, value);
    });
    root.classList.remove('light', 'dark');
    root.classList.add(theme);
  }, [theme]);

  const toggleTheme = () => setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'));

  return (
    <ThemeContext.Provider value={{ theme, setTheme, toggleTheme, colors: THEMES[theme] }}>
      {children}
    </ThemeContext.Provider>
  );
}

export const useTheme = () => useContext(ThemeContext);
export { ThemeProvider };