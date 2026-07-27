import { useTheme } from '../../context/ThemeContext';
import { useAuth } from '../../context/AuthContext';
import { Sun, Moon } from 'lucide-react';

export default function Header() {
  const { theme, toggleTheme } = useTheme();
  const { user } = useAuth();

  return (
    <header className="flex-1 flex items-center justify-between">
      <span className="text-sm text-text-secondary">
        Welcome, <span className="text-text-primary">{user?.username || user?.email || 'User'}</span>
      </span>
      <button onClick={toggleTheme} className="p-2 rounded-lg text-text-secondary hover:text-text-primary hover:bg-bg-tertiary transition-colors">
        {theme === 'dark' ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
      </button>
    </header>
  );
}