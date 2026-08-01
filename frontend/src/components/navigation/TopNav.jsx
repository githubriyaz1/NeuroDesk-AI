import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Menu, Bell, Search, User } from 'lucide-react';
import { useAuth } from '../../hooks/useAuth';

export const TopNav = ({ onMenuClick, currentTitle }) => {
  const { user } = useAuth();
  const navigate = useNavigate();

  return (
    <header className="sticky top-0 z-30 flex items-center justify-between h-16 px-6 bg-zinc-950/80 border-b border-zinc-800/80 backdrop-blur-md">
      <div className="flex items-center gap-4">
        <button
          onClick={onMenuClick}
          className="lg:hidden p-2 text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800/60 rounded-lg transition"
          aria-label="Toggle Sidebar"
        >
          <Menu size={20} />
        </button>
        <div className="flex items-center gap-2">
          <span className="text-xs font-mono text-zinc-500 uppercase tracking-widest">Workspace</span>
          <span className="text-zinc-600">/</span>
          <h2 className="text-sm font-semibold text-zinc-100">{currentTitle}</h2>
        </div>
      </div>

      <div className="flex items-center gap-3">
        {/* Quick Search Trigger */}
        <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-zinc-900 border border-zinc-800 text-xs text-zinc-400 w-64">
          <Search size={14} className="text-zinc-500" />
          <span className="flex-1">Search workspace...</span>
          <kbd className="px-1.5 py-0.5 text-[10px] font-mono bg-zinc-800 rounded border border-zinc-700 text-zinc-400">⌘K</kbd>
        </div>

        {/* Notifications */}
        <button className="p-2 text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800/60 rounded-lg transition relative">
          <Bell size={18} />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-indigo-500" />
        </button>

        {/* User Profile Button */}
        <button
          onClick={() => navigate('/profile')}
          className="flex items-center gap-3 pl-3 border-l border-zinc-800 hover:opacity-80 transition text-left focus:outline-none"
        >
          <div className="w-8 h-8 rounded-full bg-indigo-600/20 border border-indigo-500/40 flex items-center justify-center text-indigo-300 font-semibold text-xs">
            {user?.full_name ? user.full_name.charAt(0) : user?.fullName ? user.fullName.charAt(0) : 'U'}
          </div>
          <div className="hidden md:block">
            <div className="text-xs font-medium text-zinc-200">{user?.full_name || user?.fullName || 'User'}</div>
            <div className="text-[10px] text-zinc-400 font-mono">{user?.role || 'user'}</div>
          </div>
        </button>
      </div>
    </header>
  );
};
