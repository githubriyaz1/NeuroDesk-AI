import React from 'react';

export const StatCard = ({ title, value, change, icon: Icon, trend = 'up' }) => {
  return (
    <div className="bg-zinc-900/90 border border-zinc-800/80 rounded-xl p-5 hover:border-zinc-700/60 transition-all">
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium text-zinc-400 uppercase tracking-wider">{title}</span>
        {Icon && (
          <div className="p-2 rounded-lg bg-zinc-800/60 text-indigo-400 border border-zinc-700/40">
            <Icon size={18} />
          </div>
        )}
      </div>
      <div className="mt-3 flex items-baseline gap-2">
        <span className="text-2xl font-bold text-zinc-100 tracking-tight">{value}</span>
        {change && (
          <span className={`text-xs font-medium ${trend === 'up' ? 'text-emerald-400' : 'text-rose-400'}`}>
            {change}
          </span>
        )}
      </div>
    </div>
  );
};
