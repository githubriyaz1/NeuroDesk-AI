import React, { useState, useEffect } from 'react';
import { Bookmark, Plus, Trash2, X, Play } from 'lucide-react';

const LOCAL_STORAGE_KEY = 'neurodesk_saved_search_views';

export const SavedViewsModal = ({ isOpen, onClose, currentQuery, onSelectQuery }) => {
  const [savedViews, setSavedViews] = useState([]);
  const [newViewName, setNewViewName] = useState('');

  useEffect(() => {
    try {
      const stored = localStorage.getItem(LOCAL_STORAGE_KEY);
      if (stored) setSavedViews(JSON.parse(stored));
    } catch {
      setSavedViews([]);
    }
  }, []);

  const saveViewsToStorage = (views) => {
    setSavedViews(views);
    try {
      localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(views));
    } catch (e) {
      console.error('Failed to save search views', e);
    }
  };

  const handleSaveCurrent = () => {
    if (!newViewName.trim() || !currentQuery.trim()) return;
    const newView = {
      id: Date.now().toString(),
      name: newViewName.trim(),
      query: currentQuery.trim(),
      createdAt: new Date().toISOString(),
    };
    saveViewsToStorage([newView, ...savedViews]);
    setNewViewName('');
  };

  const handleDelete = (id) => {
    saveViewsToStorage(savedViews.filter((v) => v.id !== id));
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in">
      <div className="w-full max-w-md bg-zinc-950 border border-zinc-800 rounded-2xl p-5 shadow-2xl space-y-4">
        <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
          <div className="flex items-center gap-2 text-sm font-semibold text-zinc-200">
            <Bookmark size={16} className="text-amber-400" />
            <span>Saved Search Views</span>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800"
          >
            <X size={16} />
          </button>
        </div>

        {/* Save Current Query */}
        <div className="p-3 rounded-xl bg-zinc-900/60 border border-zinc-800/80 space-y-2">
          <div className="text-xs text-zinc-400">Save current active filter:</div>
          <div className="font-mono text-xs px-2.5 py-1.5 rounded-lg bg-zinc-950 text-indigo-300 border border-zinc-800 truncate">
            {currentQuery || '(Empty query)'}
          </div>
          <div className="flex gap-2 pt-1">
            <input
              type="text"
              value={newViewName}
              onChange={(e) => setNewViewName(e.target.value)}
              placeholder="View title (e.g. Weekly Reports)"
              className="flex-1 px-3 py-1.5 rounded-lg bg-zinc-950 border border-zinc-800 text-xs text-zinc-200 focus:outline-none focus:border-indigo-500"
            />
            <button
              onClick={handleSaveCurrent}
              disabled={!newViewName.trim() || !currentQuery.trim()}
              className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-xs text-white font-medium transition-colors"
            >
              <Plus size={13} />
              <span>Save</span>
            </button>
          </div>
        </div>

        {/* Saved Views List */}
        <div className="space-y-2 max-h-60 overflow-y-auto pr-1">
          {savedViews.length === 0 ? (
            <div className="text-center py-6 text-xs text-zinc-500">
              No saved views yet. Create one above!
            </div>
          ) : (
            savedViews.map((view) => (
              <div
                key={view.id}
                className="flex items-center justify-between p-2.5 rounded-xl bg-zinc-900/40 border border-zinc-800/60 hover:border-zinc-700 transition-colors"
              >
                <div className="min-w-0 pr-2">
                  <div className="text-xs font-medium text-zinc-200 truncate">{view.name}</div>
                  <div className="font-mono text-[10px] text-zinc-500 truncate">{view.query}</div>
                </div>

                <div className="flex items-center gap-1.5 flex-shrink-0">
                  <button
                    onClick={() => {
                      onSelectQuery(view.query);
                      onClose();
                    }}
                    className="p-1.5 rounded-lg bg-indigo-600/20 text-indigo-400 hover:bg-indigo-600/40 transition-colors"
                    title="Load View"
                  >
                    <Play size={12} />
                  </button>

                  <button
                    onClick={() => handleDelete(view.id)}
                    className="p-1.5 rounded-lg text-zinc-500 hover:text-rose-400 hover:bg-rose-500/10 transition-colors"
                    title="Delete View"
                  >
                    <Trash2 size={12} />
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
