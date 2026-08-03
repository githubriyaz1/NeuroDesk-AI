import React, { useState } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { Sidebar } from '../components/navigation/Sidebar';
import { TopNav } from '../components/navigation/TopNav';
import { NAVIGATION_ITEMS } from '../utils/constants';
import { ActivityProvider } from '../contexts/ActivityContext';
import { CommandPaletteModal } from '../components/common/CommandPaletteModal';

export const DashboardLayout = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();

  const currentNav = NAVIGATION_ITEMS.find((item) => item.path === location.pathname) || {
    label: 'Dashboard',
  };

  return (
    <ActivityProvider>
      <div className="flex h-screen bg-background text-zinc-100 overflow-hidden">
        {/* Mobile backdrop */}
        {sidebarOpen && (
          <div
            className="fixed inset-0 z-30 bg-black/60 backdrop-blur-xs lg:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}

        {/* Sidebar */}
        <Sidebar
          navItems={NAVIGATION_ITEMS}
          isOpen={sidebarOpen}
          onClose={() => setSidebarOpen(false)}
        />

        {/* Main Content Area */}
        <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
          <TopNav
            currentTitle={currentNav.label}
            onMenuClick={() => setSidebarOpen((prev) => !prev)}
          />
          <main className="flex-1 overflow-y-auto p-6 md:p-8 bg-zinc-950/40">
            <div className="max-w-7xl mx-auto space-y-6">
              <Outlet />
            </div>
          </main>
        </div>

        <CommandPaletteModal />
      </div>
    </ActivityProvider>
  );
};
