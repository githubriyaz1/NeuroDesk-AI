import React, { useState, useEffect } from 'react';
import { X, Download, Star, Trash2, RotateCcw, Edit2, Check, ShieldCheck, FileText, Database, Image as ImageIcon, Music, Film, Sparkles, Box, Code } from 'lucide-react';
import { Button } from '../common/Button';
import { Badge } from '../common/Badge';
import { formatBytes, formatDate } from '../../utils/formatters';
import { MetadataSection } from './MetadataSection';

const getAssetIcon = (type) => {
  switch (type) {
    case 'IMAGE':
      return ImageIcon;
    case 'AUDIO':
      return Music;
    case 'VIDEO':
      return Film;
    case 'SPREADSHEET':
      return Database;
    case 'DATASET':
      return Box;
    case 'PROMPT':
      return Sparkles;
    case 'MODEL':
      return Code;
    case 'REPORT':
      return FileText;
    default:
      return FileText;
  }
};

export const AssetDetailsDrawer = ({
  isOpen,
  onClose,
  asset,
  onDownload,
  onRename,
  onToggleFavorite,
  onDelete,
  onRestore,
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (asset) {
      setName(asset.name || '');
      setDescription(asset.description || '');
      setIsEditing(false);
    }
  }, [asset]);

  if (!isOpen || !asset) return null;

  const IconComponent = getAssetIcon(asset.asset_type);

  const handleSave = async () => {
    try {
      setSaving(true);
      await onRename(asset.id, name, description);
      setIsEditing(false);
    } catch (err) {
      console.error('Failed to update asset:', err);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-black/60 backdrop-blur-sm transition-opacity">
      <div className="absolute inset-y-0 right-0 max-w-full flex pl-10">
        <div className="w-screen max-w-md bg-zinc-950 border-l border-zinc-800 shadow-2xl flex flex-col">
          {/* Header */}
          <div className="p-5 border-b border-zinc-800/80 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-lg bg-indigo-600/10 text-indigo-400 border border-indigo-500/20">
                <IconComponent size={20} />
              </div>
              <div>
                <h3 className="text-sm font-bold text-zinc-100">Asset Inspector</h3>
                <span className="text-[10px] font-mono text-zinc-500 uppercase">{asset.asset_type}</span>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-zinc-400 hover:text-zinc-100 hover:bg-zinc-900 transition-colors"
            >
              <X size={18} />
            </button>
          </div>

          {/* Body Content */}
          <div className="flex-1 overflow-y-auto p-5 space-y-6">
            {/* Asset Status & Favorites */}
            <div className="flex items-center justify-between p-3 rounded-lg bg-zinc-900/60 border border-zinc-800">
              <div className="flex items-center gap-2">
                <Badge variant={asset.is_deleted ? 'danger' : 'success'}>{asset.status}</Badge>
                <span className="text-[11px] font-mono text-zinc-500">v{asset.version}</span>
              </div>
              <button
                onClick={() => onToggleFavorite(asset.id, asset.is_favorite)}
                className={`p-1.5 rounded-lg border transition-colors ${
                  asset.is_favorite
                    ? 'text-amber-400 bg-amber-400/10 border-amber-400/30'
                    : 'text-zinc-500 hover:text-zinc-300 border-zinc-800'
                }`}
              >
                <Star size={16} className={asset.is_favorite ? 'fill-amber-400' : ''} />
              </button>
            </div>

            {/* Editable Name & Description */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <label className="text-[11px] font-mono uppercase text-zinc-500 tracking-wider">Title & Summary</label>
                {!isEditing ? (
                  <button
                    onClick={() => setIsEditing(true)}
                    className="text-xs text-indigo-400 hover:underline flex items-center gap-1"
                  >
                    <Edit2 size={12} /> Edit
                  </button>
                ) : (
                  <button
                    onClick={handleSave}
                    disabled={saving}
                    className="text-xs text-emerald-400 hover:underline flex items-center gap-1 font-semibold"
                  >
                    <Check size={12} /> Save Changes
                  </button>
                )}
              </div>

              {!isEditing ? (
                <div>
                  <h2 className="text-base font-bold text-zinc-100">{asset.name}</h2>
                  <p className="text-xs text-zinc-400 mt-1 leading-relaxed">
                    {asset.description || 'No description provided.'}
                  </p>
                </div>
              ) : (
                <div className="space-y-2">
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="w-full px-3 py-1.5 bg-zinc-900 border border-zinc-700 rounded text-xs text-zinc-100 focus:outline-none focus:border-indigo-500"
                  />
                  <textarea
                    rows={3}
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    className="w-full px-3 py-1.5 bg-zinc-900 border border-zinc-700 rounded text-xs text-zinc-100 focus:outline-none focus:border-indigo-500"
                  />
                </div>
              )}
            </div>

            {/* Metadata Indexing Section */}
            <MetadataSection assetId={asset.id} />

            {/* Detailed File Specs */}
            <div className="space-y-2.5 pt-4 border-t border-zinc-800/80 text-xs">
              <h4 className="text-[11px] font-mono uppercase text-zinc-500 tracking-wider mb-2">Technical System Specs</h4>
              
              <div className="flex justify-between py-1 border-b border-zinc-900 text-zinc-300">
                <span className="text-zinc-500 font-mono">Original File:</span>
                <span className="font-medium truncate max-w-[200px]">{asset.original_filename}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-zinc-900 text-zinc-300">
                <span className="text-zinc-500 font-mono">MIME Type:</span>
                <span className="font-mono text-[11px] text-indigo-400">{asset.mime_type}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-zinc-900 text-zinc-300">
                <span className="text-zinc-500 font-mono">File Size:</span>
                <span className="font-mono">{formatBytes(asset.file_size)}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-zinc-900 text-zinc-300">
                <span className="text-zinc-500 font-mono">Provider:</span>
                <span className="font-mono text-emerald-400 uppercase">{asset.storage_provider}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-zinc-900 text-zinc-300">
                <span className="text-zinc-500 font-mono">Created:</span>
                <span>{formatDate(asset.created_at)}</span>
              </div>
            </div>

            {/* SHA256 Integrity Verification Card */}
            <div className="p-3 rounded-lg bg-zinc-900/90 border border-zinc-800 space-y-1">
              <div className="flex items-center gap-1.5 text-xs text-emerald-400 font-medium">
                <ShieldCheck size={14} />
                <span>SHA-256 Cryptographic Checksum</span>
              </div>
              <p className="text-[10px] font-mono text-zinc-400 break-all bg-zinc-950 p-2 rounded border border-zinc-800/80 mt-1">
                {asset.checksum}
              </p>
            </div>
          </div>

          {/* Footer Actions */}
          <div className="p-5 border-t border-zinc-800/80 bg-zinc-950 space-y-2">
            {!asset.is_deleted ? (
              <div className="grid grid-cols-2 gap-2">
                <Button variant="outline" size="sm" onClick={() => onDownload(asset.id, asset.original_filename)}>
                  <Download size={14} className="mr-1.5" /> Download
                </Button>
                <Button variant="danger" size="sm" onClick={() => onDelete(asset.id)}>
                  <Trash2 size={14} className="mr-1.5" /> Soft Delete
                </Button>
              </div>
            ) : (
              <Button size="sm" className="w-full" onClick={() => onRestore(asset.id)}>
                <RotateCcw size={14} className="mr-1.5" /> Restore Asset
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
