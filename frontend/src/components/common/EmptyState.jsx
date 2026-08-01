import React from 'react';
import { Button } from './Button';

export const EmptyState = ({ title, description, icon: Icon, actionLabel, onAction }) => {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center border border-dashed border-zinc-800 rounded-xl bg-zinc-900/40">
      {Icon && (
        <div className="p-3 mb-4 rounded-xl bg-zinc-800/80 text-zinc-400 border border-zinc-700/60">
          <Icon size={24} />
        </div>
      )}
      <h4 className="text-base font-semibold text-zinc-200">{title}</h4>
      {description && <p className="text-xs text-zinc-400 max-w-sm mt-1 mb-6 leading-relaxed">{description}</p>}
      {actionLabel && onAction && (
        <Button onClick={onAction} size="sm">
          {actionLabel}
        </Button>
      )}
    </div>
  );
};
