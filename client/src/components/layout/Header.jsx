import { useTheme } from '../../context/ThemeContext';
import { useAuth } from '../../context/AuthContext';
import { Sun, Moon } from 'lucide-react';

export default function Header() {
  const { theme, toggleTheme } = useTheme();
  const { user } = useAuth();

  const displayName = user?.username || user?.email || 'User';

  return (
    <header className="h-14 bg-bg-secondary border-b border-border flex items-center justify-between px-4 lg:px-6 shrink-0">
      <div>
        <span className="text-sm text-text-secondary">Welcome, <span className="text-text-primary">{displayName}</span></span>
      </div>
      <button
        onClick={toggleTheme}
        className="p-2 rounded-lg text-text-secondary hover:text-text-primary hover:bg-bg-tertiary transition-colors"
      >
        {theme === 'dark' ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
      </button>
    </header>
  );
}