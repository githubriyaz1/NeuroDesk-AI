import React, { useState } from 'react';
import { Card } from '../common/Card';
import { Badge } from '../common/Badge';
import {
  FileText,
  Database,
  Image as ImageIcon,
  Music,
  Film,
  Sparkles,
  Box,
  Code,
  Star,
  MoreVertical,
  Maximize2,
  Eye,
} from 'lucide-react';
import { formatBytes, formatDate } from '../../utils/formatters';
import { useAssets } from '../../contexts/AssetContext';
import { ExplorerContextMenu } from './ExplorerContextMenu';

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

export const ExplorerGrid = () => {
  const {
    assets,
    selectedAssetIds,
    toggleSelectAsset,
    toggleFavoriteItem,
    archiveAssetItem,
    deleteAssetItem,
    restoreAssetItem,
    downloadAssetItem,
    openDrawer,
    openPreview,
  } = useAssets();

  const [contextMenu, setContextMenu] = useState(null);

  const handleContextMenu = (e, asset) => {
    e.preventDefault();
    setContextMenu({
      x: e.clientX,
      y: e.clientY,
      asset,
    });
  };

  return (
    <>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {assets.map((asset) => {
          const IconComponent = getAssetIcon(asset.asset_type);
          const isSelected = selectedAssetIds.includes(asset.id);

          return (
            <Card
              key={asset.id}
              onContextMenu={(e) => handleContextMenu(e, asset)}
              className={`relative hover:border-zinc-700/80 transition-all flex flex-col justify-between group ${
                isSelected ? 'border-indigo-500/80 bg-indigo-500/5 ring-1 ring-indigo-500/30' : ''
              }`}
            >
              <div>
                {/* Header Strip with Checkbox, Icon, Favorites, and Context Trigger */}
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-center gap-2.5 min-w-0">
                    <input
                      type="checkbox"
                      checked={isSelected}
                      onChange={() => toggleSelectAsset(asset.id)}
                      className="w-4 h-4 rounded border-zinc-700 bg-zinc-900 text-indigo-600 focus:ring-indigo-500/20"
                    />
                    <div className="p-2.5 rounded-lg bg-zinc-900 text-indigo-400 border border-zinc-800 flex-shrink-0">
                      <IconComponent size={18} />
                    </div>
                    <div className="min-w-0">
                      <h4 className="text-xs font-bold text-zinc-100 truncate group-hover:text-indigo-400 transition-colors">
                        {asset.name}
                      </h4>
                      <span className="text-[10px] font-mono text-zinc-500 uppercase">{asset.asset_type}</span>
                    </div>
                  </div>

                  <div className="flex items-center gap-1 flex-shrink-0">
                    <button
                      onClick={() => toggleFavoriteItem(asset.id, asset.is_favorite)}
                      className="text-zinc-500 hover:text-amber-400 transition-colors p-1"
                    >
                      <Star size={15} className={asset.is_favorite ? 'text-amber-400 fill-amber-400' : ''} />
                    </button>
                    <button
                      onClick={(e) => handleContextMenu(e, asset)}
                      className="p-1 rounded text-zinc-500 hover:text-zinc-200 hover:bg-zinc-900"
                    >
                      <MoreVertical size={15} />
                    </button>
                  </div>
                </div>

                <p className="text-[11px] text-zinc-400 mt-2.5 line-clamp-2 leading-relaxed">
                  {asset.description || asset.original_filename}
                </p>
              </div>

              {/* Footer specs & buttons */}
              <div className="mt-4 pt-2.5 border-t border-zinc-800/80 flex items-center justify-between text-[10px] font-mono text-zinc-500">
                <span>{formatBytes(asset.file_size)}</span>
                <Badge variant={asset.is_deleted ? 'danger' : asset.status === 'ARCHIVED' ? 'indigo' : 'success'}>
                  {asset.status}
                </Badge>

                <div className="flex items-center gap-1">
                  <button
                    onClick={() => openPreview(asset)}
                    className="p-1 rounded bg-indigo-600/10 hover:bg-indigo-600/20 text-indigo-400 border border-indigo-500/20 transition-colors"
                    title="Preview"
                  >
                    <Maximize2 size={12} />
                  </button>
                  <button
                    onClick={() => openDrawer(asset)}
                    className="p-1 rounded bg-zinc-900 hover:bg-zinc-800 text-zinc-300 transition-colors"
                    title="Inspect"
                  >
                    <Eye size={12} />
                  </button>
                </div>
              </div>
            </Card>
          );
        })}
      </div>

      {contextMenu && (
        <ExplorerContextMenu
          x={contextMenu.x}
          y={contextMenu.y}
          asset={contextMenu.asset}
          onClose={() => setContextMenu(null)}
          onPreview={openPreview}
          onInspect={openDrawer}
          onDownload={downloadAssetItem}
          onToggleFavorite={toggleFavoriteItem}
          onToggleArchive={archiveAssetItem}
          onDelete={deleteAssetItem}
          onRestore={restoreAssetItem}
        />
      )}
    </>
  );
};
