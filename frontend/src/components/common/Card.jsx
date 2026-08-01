import React from 'react';

export const Card = ({ children, className = '', title, subtitle, action }) => {
  return (
    <div className={`bg-zinc-900/80 border border-zinc-800 rounded-xl p-5 shadow-glass ${className}`}>
      {(title || action) && (
        <div className="flex items-center justify-between mb-4 pb-3 border-b border-zinc-800/80">
          <div>
            {title && <h3 className="text-base font-semibold text-zinc-100">{title}</h3>}
            {subtitle && <p className="text-xs text-zinc-400 mt-0.5">{subtitle}</p>}
          </div>
          {action && <div>{action}</div>}
        </div>
      )}
      {children}
    </div>
  );
};
