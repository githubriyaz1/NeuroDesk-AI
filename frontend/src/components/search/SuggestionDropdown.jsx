import React from 'react';
import { Search, Tag, FileText, Sparkles } from 'lucide-react';

export const SuggestionDropdown = ({ suggestions, onSelect, onClose }) => {
  if (!suggestions || suggestions.length === 0) return null;

  const getIcon = (type) => {
    switch (type) {
      case 'filename':
        return FileText;
      case 'metadata':
        return Tag;
      case 'tag':
        return Sparkles;
      default:
        return Search;
    }
  };

  return (
    <div className="absolute top-full left-0 right-0 mt-1.5 z-50 py-1.5 rounded-xl bg-zinc-950/95 border border-zinc-800 shadow-2xl backdrop-blur-md text-xs text-zinc-200 divide-y divide-zinc-900 animate-in fade-in zoom-in-95">
      <div className="px-3 py-1 font-mono text-[10px] uppercase text-zinc-500 font-semibold tracking-wider">
        Search Suggestions
      </div>
      <div className="py-1">
        {suggestions.map((item, idx) => {
          const IconComp = getIcon(item.type);
          return (
            <button
              key={idx}
              onClick={() => onSelect(item.text)}
              className="w-full flex items-center justify-between px-3 py-2 text-left hover:bg-indigo-600/20 hover:text-indigo-300 transition-colors"
            >
              <div className="flex items-center gap-2.5 min-w-0">
                <IconComp size={14} className="text-indigo-400 flex-shrink-0" />
                <span className="truncate">{item.text}</span>
              </div>
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-zinc-900 text-zinc-500 border border-zinc-800 uppercase">
                {item.type}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
};
