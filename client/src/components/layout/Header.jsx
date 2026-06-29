import { useTheme } from '../../context/ThemeContext';
import { useAuth } from '../../context/AuthContext';
import { Sun, Moon, Menu } from 'lucide-react';

export default function Header({ onMenuClick }) {
  const { theme, toggleTheme } = useTheme();
  const { user } = useAuth();

  return (
    <header className="h-14 bg-bg-secondary border-b border-border flex items-center justify-between px-4 lg:px-6 shrink-0">
      <div className="flex items-center gap-3">
        <button onClick={onMenuClick} className="lg:hidden p-1.5 text-text-secondary hover:text-text-primary rounded-lg">
          <Menu size={20} />
        </button>
        <span className="text-sm text-text-secondary">Welcome, <span className="text-text-primary">{user?.username || user?.email || 'User'}</span></span>
      </div>
      <button onClick={toggleTheme} className="p-2 rounded-lg text-text-secondary hover:text-text-primary hover:bg-bg-tertiary transition-colors">
        {theme === 'dark' ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
      </button>
    </header>
  );
}