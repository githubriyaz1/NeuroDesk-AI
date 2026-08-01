import React from 'react';

export const LoadingSpinner = ({ label = 'Loading...' }) => {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-zinc-400 gap-3">
      <div className="w-8 h-8 border-2 border-indigo-500/30 border-t-indigo-500 rounded-full animate-spin" />
      <span className="text-xs font-medium tracking-wide">{label}</span>
    </div>
  );
};
