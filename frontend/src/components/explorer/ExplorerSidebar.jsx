import React from 'react';
import {
  FolderKanban,
  Clock,
  Star,
  FileText,
  Image as ImageIcon,
  Database,
  Archive,
  Trash2,
} from 'lucide-react';
import { useAssets } from '../../contexts/AssetContext';

export const ExplorerSidebar = () => {
  const { activeCategory, selectCategory, statistics } = useAssets();

  const categories = [
    { id: 'all', label: 'All Assets', icon: FolderKanban, count: statistics?.total_assets || 0 },
    { id: 'recent', label: 'Recent', icon: Clock, count: statistics?.total_assets || 0 },
    { id: 'favorites', label: 'Favorites', icon: Star, count: statistics?.favorite_assets || 0 },
    { id: 'documents', label: 'Documents', icon: FileText, count: statistics?.asset_count_by_type?.DOCUMENT || 0 },
    { id: 'images', label: 'Images', icon: ImageIcon, count: statistics?.asset_count_by_type?.IMAGE || 0 },
    { id: 'datasets', label: 'Datasets', icon: Database, count: (statistics?.asset_count_by_type?.DATASET || 0) + (statistics?.asset_count_by_type?.SPREADSHEET || 0) },
    { id: 'archived', label: 'Archived', icon: Archive, count: statistics?.assets_by_status?.ARCHIVED || 0 },
    { id: 'trash', label: 'Trash', icon: Trash2, count: statistics?.deleted_assets || 0 },
  ];

  return (
    <aside className="w-full lg:w-56 bg-zinc-950/80 border border-zinc-800/80 rounded-xl p-3 flex flex-col gap-1">
      <h3 className="text-[10px] font-mono uppercase tracking-wider text-zinc-500 px-3 py-1.5 font-semibold">
        Asset Explorer
      </h3>
      <nav className="space-y-0.5">
        {categories.map((cat) => {
          const IconComponent = cat.icon;
          const isActive = activeCategory === cat.id;
          return (
            <button
              key={cat.id}
              onClick={() => selectCategory(cat.id)}
              className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
                isActive
                  ? 'bg-indigo-600/20 text-indigo-400 border border-indigo-500/30 font-semibold'
                  : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900/60'
              }`}
            >
              <div className="flex items-center gap-2.5">
                <IconComponent size={15} className={isActive ? 'text-indigo-400' : 'text-zinc-500'} />
                <span>{cat.label}</span>
              </div>
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-zinc-900 text-zinc-500 border border-zinc-800">
                {cat.count}
              </span>
            </button>
          );
        })}
      </nav>
    </aside>
  );
};
