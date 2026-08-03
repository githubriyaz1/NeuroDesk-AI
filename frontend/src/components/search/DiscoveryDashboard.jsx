import React, { useState, useEffect } from 'react';
import { Clock, Star, HardDrive, Sparkles, Eye, Download } from 'lucide-react';
import { discoveryService } from '../../services/discoveryService';

export const DiscoveryDashboard = ({ onSelectAsset, onPreviewAsset }) => {
  const [loading, setLoading] = useState(true);
  const [recent, setRecent] = useState([]);
  const [favorites, setFavorites] = useState([]);
  const [largest, setLargest] = useState([]);
  const [newest, setNewest] = useState([]);

  useEffect(() => {
    let active = true;
    setLoading(true);

    Promise.all([
      discoveryService.getRecent(5),
      discoveryService.getFavorites(5),
      discoveryService.getLargest(5),
      discoveryService.getNewest(5),
    ])
      .then(([recRes, favRes, lrgRes, newRes]) => {
        if (active) {
          setRecent(recRes || []);
          setFavorites(favRes || []);
          setLargest(lrgRes || []);
          setNewest(newRes || []);
          setLoading(false);
        }
      })
      .catch((err) => {
        console.error('Failed to load discovery collections', err);
        if (active) setLoading(false);
      });

    return () => { active = false; };
  }, []);

  const formatSize = (bytes) => {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
  };

  const renderSection = (title, icon, items, badgeColor) => {
    const IconComp = icon;
    return (
      <div className="p-4 rounded-2xl bg-zinc-950/70 border border-zinc-800/80 space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-xs font-semibold text-zinc-200">
            <IconComp size={15} className={badgeColor} />
            <span>{title}</span>
          </div>
          <span className="text-[10px] font-mono text-zinc-500">{items.length} items</span>
        </div>

        {loading ? (
          <div className="space-y-2 animate-pulse">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-10 rounded-xl bg-zinc-900/60" />
            ))}
          </div>
        ) : items.length === 0 ? (
          <div className="py-6 text-center text-xs text-zinc-500 font-mono">
            No assets found in this collection
          </div>
        ) : (
          <div className="space-y-1.5">
            {items.map((asset) => (
              <div
                key={asset.id}
                onClick={() => onSelectAsset && onSelectAsset(asset)}
                className="group flex items-center justify-between p-2.5 rounded-xl bg-zinc-900/40 border border-zinc-800/50 hover:bg-zinc-800/60 hover:border-zinc-700 transition-all cursor-pointer"
              >
                <div className="min-w-0 pr-2">
                  <div className="text-xs font-medium text-zinc-200 truncate group-hover:text-indigo-300 transition-colors">
                    {asset.name}
                  </div>
                  <div className="flex items-center gap-2 text-[10px] font-mono text-zinc-500">
                    <span>{asset.asset_type}</span>
                    <span>•</span>
                    <span>{formatSize(asset.file_size)}</span>
                  </div>
                </div>

                <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  {onPreviewAsset && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onPreviewAsset(asset);
                      }}
                      className="p-1 rounded-md text-zinc-400 hover:text-indigo-300 hover:bg-indigo-600/20"
                      title="Quick Preview"
                    >
                      <Eye size={12} />
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-sm font-semibold text-zinc-200">
          <Sparkles size={16} className="text-indigo-400" />
          <span>Curated Discovery Dashboard</span>
        </div>
        <span className="text-xs font-mono text-zinc-500">Automated Smart Collections</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {renderSection('Recent Assets', Clock, recent, 'text-blue-400')}
        {renderSection('Favorites', Star, favorites, 'text-amber-400')}
        {renderSection('Largest Files', HardDrive, largest, 'text-emerald-400')}
        {renderSection('Newest Assets', Sparkles, newest, 'text-purple-400')}
      </div>
    </div>
  );
};
