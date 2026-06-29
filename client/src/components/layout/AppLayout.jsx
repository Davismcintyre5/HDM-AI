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
    <div className="flex h-screen bg-bg">
      {/* Mobile overlay */}
      {mobileOpen && <div className="lg:hidden fixed inset-0 z-40 bg-black/50" onClick={() => setMobileOpen(false)} />}

      {/* Sidebar — hidden on mobile unless open */}
      <div className={`${mobileOpen ? 'fixed inset-y-0 left-0 z-50' : 'hidden'} lg:flex`}>
        <Sidebar collapsed={collapsed} onToggle={() => setCollapsed(!collapsed)} onMobileClose={() => setMobileOpen(false)} />
      </div>

      <div className="flex-1 flex flex-col min-w-0">
        <Header onMenuClick={() => setMobileOpen(true)} />
        <main className="flex-1 overflow-y-auto p-4 lg:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}