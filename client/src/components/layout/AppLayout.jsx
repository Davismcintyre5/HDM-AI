import { useState } from 'react';
import { Outlet, Navigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import Sidebar from './Sidebar';
import Header from './Header';
import Spinner from '../ui/Spinner';
import { Menu } from 'lucide-react';

export default function AppLayout() {
  const { user, loading } = useAuth();
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  if (loading) return <div className="h-screen flex items-center justify-center bg-bg"><Spinner size="lg" /></div>;
  if (!user) return <Navigate to="/login" />;

  return (
    <div className="h-screen flex overflow-hidden bg-bg">
      {/* Desktop sidebar */}
      <div className="hidden lg:block shrink-0">
        <Sidebar collapsed={collapsed} onToggle={() => setCollapsed(!collapsed)} />
      </div>

      {/* Mobile sidebar overlay */}
      {mobileOpen && (
        <>
          <div className="fixed inset-0 z-40 bg-black/50 lg:hidden" onClick={() => setMobileOpen(false)} />
          <div className="fixed inset-y-0 left-0 z-50 w-64 lg:hidden">
            <Sidebar collapsed={false} onMobileClose={() => setMobileOpen(false)} />
          </div>
        </>
      )}

      {/* Main area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Header with hamburger */}
        <div className="shrink-0 flex items-center h-14 bg-bg-secondary border-b border-border px-4 lg:px-6">
          <button onClick={() => setMobileOpen(true)} className="lg:hidden p-2 mr-3 text-text-secondary hover:text-text-primary hover:bg-bg-tertiary rounded-lg">
            <Menu size={20} />
          </button>
          <Header />
        </div>
        {/* Scrollable content */}
        <main className="flex-1 overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}