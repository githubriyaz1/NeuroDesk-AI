import React from 'react';
import { Bell, CheckCircle2, AlertTriangle, Info, XCircle, X } from 'lucide-react';
import { useActivity } from '../../contexts/ActivityContext';

export function NotificationDrawer({ isOpen, onClose }) {
  const { notifications, markAllNotificationsRead } = useActivity();

  if (!isOpen) return null;

  const getIcon = (type) => {
    switch (type) {
      case 'success':
        return <CheckCircle2 size={16} className="text-emerald-400 shrink-0" />;
      case 'warning':
        return <AlertTriangle size={16} className="text-amber-400 shrink-0" />;
      case 'error':
        return <XCircle size={16} className="text-rose-400 shrink-0" />;
      default:
        return <Info size={16} className="text-cyan-400 shrink-0" />;
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-black/60 backdrop-blur-sm transition-opacity">
      <div className="absolute inset-y-0 right-0 max-w-full flex pl-10">
        <div className="w-screen max-w-sm bg-slate-900 border-l border-slate-800 shadow-2xl flex flex-col">
          {/* Header */}
          <div className="p-4 border-b border-slate-800 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Bell size={18} className="text-cyan-400" />
              <h3 className="text-sm font-bold text-slate-100">Global Notifications</h3>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={markAllNotificationsRead}
                className="text-[11px] font-semibold text-cyan-400 hover:underline"
              >
                Mark all read
              </button>
              <button onClick={onClose} className="text-slate-400 hover:text-slate-200">
                <X size={18} />
              </button>
            </div>
          </div>

          {/* List */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            {notifications.length === 0 ? (
              <div className="text-center py-12 text-xs text-slate-500">No notifications yet.</div>
            ) : (
              notifications.map((n) => (
                <div
                  key={n.id}
                  className={`p-3 rounded-xl border text-xs space-y-1 transition-all ${
                    !n.read
                      ? 'bg-slate-800/90 border-cyan-500/40 text-slate-100 shadow-md'
                      : 'bg-slate-950/60 border-slate-800/80 text-slate-400'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2 font-bold">
                      {getIcon(n.type)}
                      <span>{n.title}</span>
                    </div>
                    <span className="text-[10px] font-mono text-slate-500">{n.time}</span>
                  </div>
                  <p className="text-xs text-slate-300 leading-relaxed pl-6">{n.message}</p>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
