import React, { useEffect, useState } from 'react';
import { Paperclip, X, FileText, Check } from 'lucide-react';
import { assetService } from '../../services/assetService';

export default function AssetPickerModal({ isOpen, onClose, onSelectAsset, selectedAssets = [] }) {
  const [assets, setAssets] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setLoading(true);
      assetService
        .getAssets()
        .then((res) => setAssets(res.items || res || []))
        .catch((err) => console.error('Failed to load workspace assets:', err))
        .finally(() => setLoading(false));
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-md p-5 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
            <Paperclip size={16} className="text-cyan-400" /> Select Workspace Asset
          </h3>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-200 text-xs">✕</button>
        </div>

        <div className="space-y-2 max-h-64 overflow-y-auto pr-1">
          {loading ? (
            <div className="text-xs text-slate-400 text-center py-6">Loading workspace assets...</div>
          ) : assets.length === 0 ? (
            <div className="text-xs text-slate-500 text-center py-6">No workspace assets uploaded yet.</div>
          ) : (
            assets.map((asset) => {
              const isSelected = selectedAssets.some((a) => a.id === asset.id);
              return (
                <div
                  key={asset.id}
                  onClick={() => {
                    onSelectAsset(asset);
                    onClose();
                  }}
                  className={`p-2.5 rounded-xl border text-xs flex items-center justify-between cursor-pointer transition-all ${
                    isSelected
                      ? 'bg-cyan-500/20 border-cyan-500/50 text-cyan-300'
                      : 'bg-slate-950 border-slate-800 text-slate-300 hover:border-slate-700'
                  }`}
                >
                  <div className="flex items-center gap-2 truncate">
                    <FileText size={14} className="text-cyan-400 shrink-0" />
                    <span className="truncate">{asset.name || asset.original_filename}</span>
                  </div>
                  {isSelected && <Check size={14} className="text-cyan-400 shrink-0" />}
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}
