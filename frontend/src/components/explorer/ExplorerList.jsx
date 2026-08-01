import React, { useState } from 'react';
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

export const ExplorerList = () => {
  const {
    assets,
    selectedAssetIds,
    toggleSelectAsset,
    selectAllAssets,
    toggleFavoriteItem,
    archiveAssetItem,
    deleteAssetItem,
    restoreAssetItem,
    downloadAssetItem,
    openDrawer,
    openPreview,
  } = useAssets();

  const [contextMenu, setContextMenu] = useState(null);

  const allSelected = assets.length > 0 && selectedAssetIds.length === assets.length;

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
      <div className="border border-zinc-800 rounded-xl overflow-hidden bg-zinc-950/80">
        <table className="w-full text-left border-collapse text-xs">
          <thead className="bg-zinc-900/90 border-b border-zinc-800 font-mono text-[11px] text-zinc-400">
            <tr>
              <th className="p-3 w-10 text-center">
                <input
                  type="checkbox"
                  checked={allSelected}
                  onChange={selectAllAssets}
                  className="w-4 h-4 rounded border-zinc-700 bg-zinc-900 text-indigo-600 focus:ring-indigo-500/20"
                />
              </th>
              <th className="p-3 font-semibold">Name & Original File</th>
              <th className="p-3 font-semibold w-28">Type</th>
              <th className="p-3 font-semibold w-24 font-mono">Size</th>
              <th className="p-3 font-semibold w-28">Status</th>
              <th className="p-3 font-semibold w-32 font-mono">Updated</th>
              <th className="p-3 font-semibold w-24 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-900/80 text-zinc-300">
            {assets.map((asset) => {
              const IconComponent = getAssetIcon(asset.asset_type);
              const isSelected = selectedAssetIds.includes(asset.id);

              return (
                <tr
                  key={asset.id}
                  onContextMenu={(e) => handleContextMenu(e, asset)}
                  className={`hover:bg-zinc-900/50 transition-colors group ${
                    isSelected ? 'bg-indigo-500/10' : ''
                  }`}
                >
                  <td className="p-3 text-center">
                    <input
                      type="checkbox"
                      checked={isSelected}
                      onChange={() => toggleSelectAsset(asset.id)}
                      className="w-4 h-4 rounded border-zinc-700 bg-zinc-900 text-indigo-600 focus:ring-indigo-500/20"
                    />
                  </td>

                  <td className="p-3">
                    <div className="flex items-center gap-3">
                      <div className="p-2 rounded bg-zinc-900 text-indigo-400 border border-zinc-800 flex-shrink-0">
                        <IconComponent size={16} />
                      </div>
                      <div className="min-w-0">
                        <h4 className="font-semibold text-zinc-100 truncate group-hover:text-indigo-400 transition-colors">
                          {asset.name}
                        </h4>
                        <span className="text-[10px] font-mono text-zinc-500 truncate block">
                          {asset.original_filename}
                        </span>
                      </div>
                    </div>
                  </td>

                  <td className="p-3">
                    <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-zinc-900 text-zinc-400 border border-zinc-800">
                      {asset.asset_type}
                    </span>
                  </td>

                  <td className="p-3 font-mono text-[11px] text-zinc-400">{formatBytes(asset.file_size)}</td>

                  <td className="p-3">
                    <Badge variant={asset.is_deleted ? 'danger' : asset.status === 'ARCHIVED' ? 'indigo' : 'success'}>
                      {asset.status}
                    </Badge>
                  </td>

                  <td className="p-3 font-mono text-[11px] text-zinc-500">{formatDate(asset.updated_at)}</td>

                  <td className="p-3 text-right">
                    <div className="flex items-center justify-end gap-1">
                      <button
                        onClick={() => toggleFavoriteItem(asset.id, asset.is_favorite)}
                        className="p-1 text-zinc-500 hover:text-amber-400 transition-colors"
                      >
                        <Star size={14} className={asset.is_favorite ? 'text-amber-400 fill-amber-400' : ''} />
                      </button>
                      <button
                        onClick={() => openPreview(asset)}
                        className="p-1 rounded text-indigo-400 hover:bg-indigo-600/10 transition-colors"
                        title="Preview"
                      >
                        <Maximize2 size={13} />
                      </button>
                      <button
                        onClick={() => openDrawer(asset)}
                        className="p-1 rounded text-zinc-400 hover:text-white transition-colors"
                        title="Inspect"
                      >
                        <Eye size={13} />
                      </button>
                      <button
                        onClick={(e) => handleContextMenu(e, asset)}
                        className="p-1 rounded text-zinc-500 hover:text-zinc-200"
                      >
                        <MoreVertical size={14} />
                      </button>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
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
