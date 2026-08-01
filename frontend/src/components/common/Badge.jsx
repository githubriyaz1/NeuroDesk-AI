import React from 'react';

export const Badge = ({ children, variant = 'neutral', className = '' }) => {
  const variants = {
    neutral: 'bg-zinc-800 text-zinc-300 border-zinc-700/60',
    success: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
    warning: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
    info: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/30',
    danger: 'bg-rose-500/10 text-rose-400 border-rose-500/30',
  };

  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border ${variants[variant]} ${className}`}>
      {children}
    </span>
  );
};
