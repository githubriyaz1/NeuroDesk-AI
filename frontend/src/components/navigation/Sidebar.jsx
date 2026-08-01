import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  FolderKanban, 
  Cpu, 
  Sparkles, 
  MessageSquareText, 
  GitFork, 
  Settings,
  User,
  BrainCircuit,
  ChevronRight
} from 'lucide-react';
import { APP_NAME } from '../../utils/constants';

const navIcons = {
  LayoutDashboard,
  FolderKanban,
  Cpu,
  Sparkles,
  MessageSquareText,
  GitFork,
  Settings,
  User,
};

export const Sidebar = ({ navItems, isOpen, onClose }) => {
  return (
    <aside className={`fixed inset-y-0 left-0 z-40 w-64 bg-zinc-950/95 border-r border-zinc-800/80 transition-transform duration-300 ease-in-out lg:static lg:translate-x-0 ${isOpen ? 'translate-x-0' : '-translate-x-full'}`}>
      <div className="flex flex-col h-full">
        {/* Brand Header */}
        <div className="flex items-center gap-3 px-6 py-5 border-b border-zinc-800/60">
          <div className="p-2 rounded-lg bg-indigo-600/20 text-indigo-400 border border-indigo-500/30">
            <BrainCircuit size={20} />
          </div>
          <div>
            <h1 className="text-base font-bold text-zinc-100 tracking-tight">{APP_NAME}</h1>
            <span className="text-[10px] uppercase font-mono tracking-widest text-indigo-400">Enterprise AI</span>
          </div>
        </div>

        {/* Navigation Items */}
        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
          {navItems.map((item) => {
            const Icon = navIcons[item.icon] || LayoutDashboard;
            return (
              <NavLink
                key={item.id}
                to={item.path}
                onClick={onClose}
                className={({ isActive }) =>
                  `flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-medium transition-all group ${
                    isActive
                      ? 'bg-zinc-800/90 text-white font-semibold border border-zinc-700/60 shadow-sm'
                      : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900/60'
                  }`
                }
              >
                <div className="flex items-center gap-3">
                  <Icon size={16} className="text-zinc-400 group-hover:text-zinc-200 transition-colors" />
                  <span>{item.label}</span>
                </div>
                <ChevronRight size={14} className="opacity-0 group-hover:opacity-100 transition-opacity text-zinc-500" />
              </NavLink>
            );
          })}
        </nav>

        {/* Footer info */}
        <div className="p-4 border-t border-zinc-800/60 bg-zinc-950">
          <div className="flex items-center justify-between px-3 py-2 rounded-lg bg-zinc-900/60 border border-zinc-800 text-[11px] text-zinc-400 font-mono">
            <span>Status</span>
            <span className="inline-flex items-center gap-1.5 text-emerald-400">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              Authenticated
            </span>
          </div>
        </div>
      </div>
    </aside>
  );
};
