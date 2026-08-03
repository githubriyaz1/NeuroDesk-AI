import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Search,
  LayoutDashboard,
  Folder,
  Wand2,
  MessageSquare,
  GitFork,
  Settings,
  User,
  Upload,
  Plus,
  BarChart2,
  Sparkles,
  Sun,
  LogOut,
  Clock,
  ArrowRight,
} from 'lucide-react';
import { useActivity } from '../../contexts/ActivityContext';
import { useAuth } from '../../hooks/useAuth';
import { useTheme } from '../../contexts/ThemeContext';

export function CommandPaletteModal() {
  const { isCommandPaletteOpen, setIsCommandPaletteOpen, recentlyOpened, trackActivity } = useActivity();
  const { logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();
  const [query, setQuery] = useState('');

  useEffect(() => {
    if (isCommandPaletteOpen) {
      setQuery('');
    }
  }, [isCommandPaletteOpen]);

  if (!isCommandPaletteOpen) return null;

  const navigateTo = (path, name, type = 'page') => {
    trackActivity(type, name, path);
    setIsCommandPaletteOpen(false);
    navigate(path);
  };

  const pages = [
    { title: 'Dashboard Overview', path: '/', icon: LayoutDashboard, category: 'Pages' },
    { title: 'Asset Workspace Explorer', path: '/workspace', icon: Folder, category: 'Pages' },
    { title: 'AI Studio & Blueprint Engine', path: '/ai-studio', icon: Wand2, category: 'Pages' },
    { title: 'Project Generator Wizard', path: '/project-generator', icon: Wand2, category: 'Pages' },
    { title: 'AI Chat & Conversation Studio', path: '/chat', icon: MessageSquare, category: 'Pages' },
    { title: 'Workflow Automation Studio', path: '/workflows', icon: GitFork, category: 'Pages' },
    { title: 'User Profile', path: '/profile', icon: User, category: 'Pages' },
    { title: 'Settings', path: '/settings', icon: Settings, category: 'Pages' },
  ];

  const quickActions = [
    { title: 'Upload New Asset', action: () => navigateTo('/workspace', 'Upload Asset'), icon: Upload, category: 'Quick Action' },
    { title: 'New Workflow Pipeline', action: () => navigateTo('/workflows', 'New Workflow'), icon: Plus, category: 'Quick Action' },
    { title: 'Open AI Chat', action: () => navigateTo('/chat', 'Open AI Chat'), icon: Sparkles, category: 'Quick Action' },
    { title: 'Generate Project Blueprint', action: () => navigateTo('/ai-studio', 'Generate Project'), icon: Wand2, category: 'Quick Action' },
    { title: 'Analyze Asset', action: () => navigateTo('/workspace', 'Analyze Asset'), icon: BarChart2, category: 'Quick Action' },
    { title: 'Run Workflow', action: () => navigateTo('/workflows', 'Run Workflow'), icon: GitFork, category: 'Quick Action' },
    { title: 'Toggle Theme', action: () => { toggleTheme(); setIsCommandPaletteOpen(false); }, icon: Sun, category: 'Quick Action' },
    { title: 'Logout', action: () => { logout(); setIsCommandPaletteOpen(false); }, icon: LogOut, category: 'Quick Action' },
  ];

  const filteredPages = pages.filter((p) => p.title.toLowerCase().includes(query.toLowerCase()));
  const filteredActions = quickActions.filter((a) => a.title.toLowerCase().includes(query.toLowerCase()));
  const filteredRecent = recentlyOpened.filter((r) => r.title.toLowerCase().includes(query.toLowerCase()));

  return (
    <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-start justify-center pt-20 p-4 animate-in fade-in">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-2xl shadow-2xl overflow-hidden flex flex-col">
        {/* Search Input Bar */}
        <div className="p-4 border-b border-slate-800 flex items-center gap-3">
          <Search className="text-cyan-400 w-5 h-5 shrink-0" />
          <input
            type="text"
            autoFocus
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Type a command or search pages, assets, actions (Ctrl+Shift+P)..."
            className="w-full bg-transparent text-sm text-slate-100 placeholder-slate-500 focus:outline-none"
          />
          <kbd className="px-2 py-0.5 rounded bg-slate-800 border border-slate-700 text-[10px] font-mono text-slate-400">ESC</kbd>
        </div>

        {/* Results List */}
        <div className="max-h-96 overflow-y-auto p-3 space-y-4">
          {/* Quick Actions */}
          {filteredActions.length > 0 && (
            <div className="space-y-1">
              <div className="px-2 py-1 text-[10px] font-mono uppercase text-cyan-400 font-bold">Quick Actions</div>
              {filteredActions.map((item, idx) => {
                const Icon = item.icon;
                return (
                  <button
                    key={idx}
                    onClick={item.action}
                    className="w-full flex items-center justify-between p-2.5 rounded-xl hover:bg-cyan-500/10 hover:text-cyan-300 text-xs text-slate-300 transition-colors group"
                  >
                    <div className="flex items-center gap-2.5">
                      <Icon className="w-4 h-4 text-cyan-400 group-hover:scale-110 transition-transform" />
                      <span className="font-semibold">{item.title}</span>
                    </div>
                    <ArrowRight className="w-3.5 h-3.5 opacity-0 group-hover:opacity-100 transition-opacity" />
                  </button>
                );
              })}
            </div>
          )}

          {/* Navigation Pages */}
          {filteredPages.length > 0 && (
            <div className="space-y-1">
              <div className="px-2 py-1 text-[10px] font-mono uppercase text-slate-500 font-bold">Navigation Pages</div>
              {filteredPages.map((item, idx) => {
                const Icon = item.icon;
                return (
                  <button
                    key={idx}
                    onClick={() => navigateTo(item.path, item.title)}
                    className="w-full flex items-center justify-between p-2.5 rounded-xl hover:bg-slate-800 text-xs text-slate-300 transition-colors group"
                  >
                    <div className="flex items-center gap-2.5">
                      <Icon className="w-4 h-4 text-indigo-400" />
                      <span className="font-medium">{item.title}</span>
                    </div>
                    <span className="text-[10px] font-mono text-slate-500">{item.path}</span>
                  </button>
                );
              })}
            </div>
          )}

          {/* Recent Items */}
          {filteredRecent.length > 0 && (
            <div className="space-y-1">
              <div className="px-2 py-1 text-[10px] font-mono uppercase text-amber-400 font-bold">Recently Opened</div>
              {filteredRecent.map((item, idx) => (
                <button
                  key={idx}
                  onClick={() => navigateTo(item.path, item.title)}
                  className="w-full flex items-center justify-between p-2.5 rounded-xl hover:bg-amber-500/10 text-xs text-slate-300 transition-colors"
                >
                  <div className="flex items-center gap-2.5">
                    <Clock className="w-4 h-4 text-amber-400" />
                    <span>{item.title}</span>
                  </div>
                  <span className="text-[10px] font-mono text-slate-500">{item.type}</span>
                </button>
              ))}
            </div>
          )}

          {filteredActions.length === 0 && filteredPages.length === 0 && filteredRecent.length === 0 && (
            <div className="p-8 text-center text-xs text-slate-500">No matching commands or pages found.</div>
          )}
        </div>
      </div>
    </div>
  );
}
