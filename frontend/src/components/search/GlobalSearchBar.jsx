import React, { useState, useEffect, useRef } from 'react';
import { Search, X, SlidersHorizontal } from 'lucide-react';
import { searchService } from '../../services/searchService';
import { SuggestionDropdown } from './SuggestionDropdown';
import { useKeyboardShortcut } from '../../hooks/useKeyboardShortcut';

export const GlobalSearchBar = ({ searchQuery, setSearchQuery, onSearch, onToggleFilters }) => {
  const [suggestions, setSuggestions] = useState([]);
  const [isFocused, setIsFocused] = useState(false);
  const inputRef = useRef(null);
  const dropdownRef = useRef(null);

  // Ctrl + K global keyboard listener using custom hook
  useKeyboardShortcut('k', () => {
    inputRef.current?.focus();
  }, 'ctrlKey');

  // Fetch search suggestions as user types
  useEffect(() => {
    let active = true;
    if (searchQuery.trim().length >= 2) {
      searchService.getSuggestions(searchQuery.trim())
        .then((res) => {
          if (active) setSuggestions(res.suggestions || []);
        })
        .catch(() => {
          if (active) setSuggestions([]);
        });
    } else {
      setSuggestions([]);
    }
    return () => { active = false; };
  }, [searchQuery]);

  const handleSubmit = (e) => {
    e.preventDefault();
    setSuggestions([]);
    if (onSearch) onSearch(searchQuery);
  };

  const handleSelectSuggestion = (text) => {
    setSearchQuery(text);
    setSuggestions([]);
    if (onSearch) onSearch(text);
  };

  return (
    <div className="relative w-full max-w-2xl" ref={dropdownRef}>
      <form onSubmit={handleSubmit} className="relative flex items-center" role="search">
        <Search size={16} className="absolute left-3.5 text-zinc-400 pointer-events-none" />
        <input
          ref={inputRef}
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setTimeout(() => setIsFocused(false), 200)}
          placeholder="Search assets (e.g. type:pdf, favorite:true, size>10MB, created:this-week)..."
          aria-label="Search assets repository"
          aria-expanded={isFocused && suggestions.length > 0}
          role="combobox"
          className="w-full pl-10 pr-24 py-2 rounded-xl bg-zinc-900/80 border border-zinc-800 text-xs text-zinc-200 placeholder-zinc-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/30 transition-all font-mono"
        />

        <div className="absolute right-2 flex items-center gap-1.5">
          {searchQuery && (
            <button
              type="button"
              onClick={() => {
                setSearchQuery('');
                setSuggestions([]);
                if (onSearch) onSearch('');
              }}
              aria-label="Clear search input"
              className="p-1 rounded-md text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 transition-colors"
            >
              <X size={13} />
            </button>
          )}

          {onToggleFilters && (
            <button
              type="button"
              onClick={onToggleFilters}
              title="Advanced Filters"
              aria-label="Toggle advanced filters"
              className="p-1.5 rounded-lg text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 transition-colors border border-zinc-800"
            >
              <SlidersHorizontal size={13} />
            </button>
          )}

          <kbd className="hidden sm:inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded text-[10px] font-mono text-zinc-500 bg-zinc-950 border border-zinc-800">
            <span>Ctrl</span><span>K</span>
          </kbd>
        </div>
      </form>

      {isFocused && (
        <SuggestionDropdown
          suggestions={suggestions}
          onSelect={handleSelectSuggestion}
        />
      )}
    </div>
  );
};
