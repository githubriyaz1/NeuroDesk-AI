import React from 'react';
import { Filter, X, Sparkles, Bookmark, RotateCcw } from 'lucide-react';

export const AdvancedFilterPanel = ({
  searchQuery,
  setSearchQuery,
  onApply,
  onReset,
  onOpenSavedViews,
}) => {
  const quickFilters = [
    { label: 'PDF Documents', syntax: 'type:pdf' },
    { label: 'Spreadsheets', syntax: 'type:csv' },
    { label: 'Images', syntax: 'type:image' },
    { label: 'Datasets', syntax: 'type:dataset' },
    { label: 'Favorites', syntax: 'favorite:true' },
    { label: 'Large Files (>10MB)', syntax: 'size>10MB' },
    { label: 'Created This Week', syntax: 'created:this-week' },
  ];

  const handleAddSyntax = (syntax) => {
    if (searchQuery.includes(syntax)) return;
    const newQuery = searchQuery ? `${searchQuery.trim()} ${syntax}` : syntax;
    setSearchQuery(newQuery);
    if (onApply) onApply(newQuery);
  };

  return (
    <div className="p-4 rounded-xl bg-zinc-900/90 border border-zinc-800 space-y-3 animate-in fade-in slide-in-from-top-2">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-xs font-semibold text-zinc-300">
          <Filter size={14} className="text-indigo-400" />
          <span>Advanced Query Builder & Syntax Chips</span>
        </div>

        <div className="flex items-center gap-2">
          {onOpenSavedViews && (
            <button
              onClick={onOpenSavedViews}
              className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs bg-zinc-950 hover:bg-zinc-800 text-zinc-300 border border-zinc-800 transition-colors font-mono"
            >
              <Bookmark size={12} className="text-amber-400" />
              <span>Saved Views</span>
            </button>
          )}

          {onReset && (
            <button
              onClick={onReset}
              className="flex items-center gap-1 px-2 py-1 rounded-lg text-xs text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 transition-colors"
            >
              <RotateCcw size={12} />
              <span>Reset</span>
            </button>
          )}
        </div>
      </div>

      <div className="flex flex-wrap gap-2 pt-1">
        {quickFilters.map((chip, idx) => {
          const isActive = searchQuery.includes(chip.syntax);
          return (
            <button
              key={idx}
              onClick={() => handleAddSyntax(chip.syntax)}
              className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-mono transition-all border ${
                isActive
                  ? 'bg-indigo-600/30 text-indigo-300 border-indigo-500/50 shadow-sm shadow-indigo-500/20'
                  : 'bg-zinc-950 text-zinc-400 border-zinc-800 hover:border-zinc-700 hover:text-zinc-200'
              }`}
            >
              <Sparkles size={11} className={isActive ? 'text-indigo-400' : 'text-zinc-500'} />
              <span>{chip.label}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
};
