import React from 'react';
import {
  Download,
  Star,
  Archive,
  Trash2,
  RotateCcw,
  X,
} from 'lucide-react';
import { Button } from '../common/Button';
import { useAssets } from '../../contexts/AssetContext';

export const BulkActionBar = () => {
  const { selectedAssetIds, clearSelection, executeBulkAction, activeCategory } = useAssets();

  if (selectedAssetIds.length === 0) return null;

  const count = selectedAssetIds.length;

  return (
    <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-40 px-4 py-2.5 rounded-2xl bg-zinc-900/95 border border-zinc-700/80 shadow-2xl backdrop-blur-md flex items-center gap-3 text-xs text-zinc-100 animate-in fade-in slide-in-from-bottom-4">
      <span className="font-mono px-2 py-0.5 rounded bg-indigo-600/20 text-indigo-400 border border-indigo-500/30 font-bold">
        {count} Selected
      </span>

      <div className="h-4 w-[1px] bg-zinc-800" />

      <div className="flex items-center gap-1.5">
        <Button
          variant="outline"
          size="sm"
          onClick={() => executeBulkAction('favorite')}
          className="text-amber-400 border-amber-400/30 hover:bg-amber-400/10"
        >
          <Star size={13} className="mr-1 fill-amber-400" /> Favorite
        </Button>

        <Button
          variant="outline"
          size="sm"
          onClick={() => executeBulkAction('archive')}
          className="text-indigo-400 border-indigo-400/30 hover:bg-indigo-400/10"
        >
          <Archive size={13} className="mr-1" /> Archive
        </Button>

        {activeCategory === 'trash' ? (
          <Button
            variant="outline"
            size="sm"
            onClick={() => executeBulkAction('restore')}
            className="text-emerald-400 border-emerald-400/30 hover:bg-emerald-400/10"
          >
            <RotateCcw size={13} className="mr-1" /> Restore
          </Button>
        ) : (
          <Button
            variant="danger"
            size="sm"
            onClick={() => executeBulkAction('delete')}
          >
            <Trash2 size={13} className="mr-1" /> Delete
          </Button>
        )}
      </div>

      <div className="h-4 w-[1px] bg-zinc-800" />

      <button
        onClick={clearSelection}
        className="p-1 rounded text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800 transition-colors"
        title="Clear Selection"
      >
        <X size={15} />
      </button>
    </div>
  );
};
