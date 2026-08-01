import React from 'react';
import { StatCard } from '../common/StatCard';
import { HardDrive, FolderKanban, Star, Trash2 } from 'lucide-react';
import { formatBytes } from '../../utils/formatters';

export const AssetStatsCards = ({ statistics }) => {
  if (!statistics) return null;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <StatCard
        title="Total DAMS Assets"
        value={statistics.total_assets || 0}
        change="+100% active"
        isPositive={true}
        icon={FolderKanban}
      />

      <StatCard
        title="Storage Consumption"
        value={formatBytes(statistics.total_storage_bytes || 0)}
        change="Local Provider"
        isPositive={true}
        icon={HardDrive}
      />

      <StatCard
        title="Favorite Assets"
        value={statistics.favorite_count || 0}
        change="Starred"
        isPositive={true}
        icon={Star}
      />

      <StatCard
        title="Soft Deleted Assets"
        value={statistics.deleted_count || 0}
        change="In Trash"
        isPositive={false}
        icon={Trash2}
      />
    </div>
  );
};
