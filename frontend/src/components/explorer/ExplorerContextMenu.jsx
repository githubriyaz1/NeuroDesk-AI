import React, { useEffect, useRef } from 'react';
import {
  Eye,
  Info,
  Edit2,
  Download,
  Star,
  Archive,
  Trash2,
  RotateCcw,
} from 'lucide-react';

export const ExplorerContextMenu = ({
  x,
  y,
  asset,
  onClose,
  onPreview,
  onInspect,
  onRename,
  onDownload,
  onToggleFavorite,
  onToggleArchive,
  onDelete,
  onRestore,
}) => {
  const menuRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        onClose();
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [onClose]);

  if (!asset) return null;

  return (
    <div
      ref={menuRef}
      style={{ top: y, left: x }}
      className="fixed z-50 w-48 py-1.5 rounded-xl bg-zinc-950/95 border border-zinc-800 shadow-2xl backdrop-blur-md text-xs text-zinc-200 space-y-0.5 animate-in fade-in zoom-in-95"
    >
      <button
        onClick={() => {
          onPreview(asset);
          onClose();
        }}
        className="w-full flex items-center gap-2 px-3 py-1.5 text-left hover:bg-indigo-600/20 hover:text-indigo-300 font-medium transition-colors"
      >
        <Eye size={14} className="text-indigo-400" /> Preview File
      </button>

      <button
        onClick={() => {
          onInspect(asset);
          onClose();
        }}
        className="w-full flex items-center gap-2 px-3 py-1.5 text-left hover:bg-zinc-900 transition-colors"
      >
        <Info size={14} className="text-zinc-400" /> Inspect Details
      </button>

      <div className="my-1 border-t border-zinc-900" />

      <button
        onClick={() => {
          onDownload(asset.id, asset.original_filename);
          onClose();
        }}
        className="w-full flex items-center gap-2 px-3 py-1.5 text-left hover:bg-zinc-900 transition-colors"
      >
        <Download size={14} className="text-zinc-400" /> Download
      </button>

      <button
        onClick={() => {
          onToggleFavorite(asset.id, asset.is_favorite);
          onClose();
        }}
        className="w-full flex items-center gap-2 px-3 py-1.5 text-left hover:bg-zinc-900 transition-colors"
      >
        <Star size={14} className={asset.is_favorite ? 'text-amber-400 fill-amber-400' : 'text-zinc-400'} />
        {asset.is_favorite ? 'Unfavorite' : 'Favorite'}
      </button>

      <button
        onClick={() => {
          onToggleArchive(asset.id, asset.status);
          onClose();
        }}
        className="w-full flex items-center gap-2 px-3 py-1.5 text-left hover:bg-zinc-900 transition-colors"
      >
        <Archive size={14} className="text-indigo-400" />
        {asset.status === 'ARCHIVED' ? 'Unarchive' : 'Archive'}
      </button>

      <div className="my-1 border-t border-zinc-900" />

      {!asset.is_deleted ? (
        <button
          onClick={() => {
            onDelete(asset.id);
            onClose();
          }}
          className="w-full flex items-center gap-2 px-3 py-1.5 text-left text-rose-400 hover:bg-rose-500/10 transition-colors"
        >
          <Trash2 size={14} /> Soft Delete
        </button>
      ) : (
        <button
          onClick={() => {
            onRestore(asset.id);
            onClose();
          }}
          className="w-full flex items-center gap-2 px-3 py-1.5 text-left text-emerald-400 hover:bg-emerald-500/10 transition-colors"
        >
          <RotateCcw size={14} /> Restore Asset
        </button>
      )}
    </div>
  );
};
