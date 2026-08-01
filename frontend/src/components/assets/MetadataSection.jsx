import React, { useState, useEffect, useCallback } from 'react';
import { RefreshCw, ChevronDown, ChevronRight, FileSearch, AlertCircle } from 'lucide-react';
import { metadataService } from '../../services/metadataService';
import { LoadingSpinner } from '../common/LoadingSpinner';

export const MetadataSection = ({ assetId }) => {
  const [metadata, setMetadata] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);
  const [openGroups, setOpenGroups] = useState({});

  const fetchMetadata = useCallback(async () => {
    if (!assetId) return;
    try {
      setLoading(true);
      setError(null);
      const data = await metadataService.getMetadata(assetId);
      setMetadata(data);
      // Open all groups by default
      const initialOpen = {};
      (data.groups || []).forEach((g, idx) => {
        initialOpen[idx] = true;
      });
      setOpenGroups(initialOpen);
    } catch (err) {
      console.error('Failed to load metadata:', err);
      setError(err.response?.data?.detail || err.message || 'Failed to load metadata');
    } finally {
      setLoading(false);
    }
  }, [assetId]);

  useEffect(() => {
    fetchMetadata();
  }, [fetchMetadata]);

  const handleRefresh = async () => {
    try {
      setRefreshing(true);
      setError(null);
      const data = await metadataService.refreshMetadata(assetId);
      setMetadata(data);
    } catch (err) {
      console.error('Failed to refresh metadata:', err);
      setError(err.response?.data?.detail || err.message || 'Failed to refresh metadata');
    } finally {
      setRefreshing(false);
    }
  };

  const toggleGroup = (index) => {
    setOpenGroups((prev) => ({
      ...prev,
      [index]: !prev[index],
    }));
  };

  if (loading) {
    return (
      <div className="p-4 rounded-lg bg-zinc-900/60 border border-zinc-800 space-y-2">
        <LoadingSpinner label="Extracting metadata index..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-xs text-rose-400 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <AlertCircle size={14} />
          <span>{error}</span>
        </div>
        <button onClick={fetchMetadata} className="underline text-[11px]">Retry</button>
      </div>
    );
  }

  if (!metadata || !metadata.groups || metadata.groups.length === 0) {
    return (
      <div className="p-4 text-center rounded-lg bg-zinc-900/40 border border-zinc-800/80 text-xs text-zinc-500 space-y-2">
        <FileSearch size={20} className="mx-auto text-zinc-600" />
        <p>No metadata index found for this asset.</p>
        <button
          onClick={handleRefresh}
          className="text-xs text-indigo-400 hover:underline inline-flex items-center gap-1"
        >
          <RefreshCw size={12} /> Index Metadata
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-3 pt-4 border-t border-zinc-800/80 text-xs">
      <div className="flex items-center justify-between">
        <h4 className="text-[11px] font-mono uppercase text-zinc-500 tracking-wider">
          Metadata Engine ({metadata.total_keys} Keys)
        </h4>
        <button
          onClick={handleRefresh}
          disabled={refreshing}
          className="text-xs text-indigo-400 hover:text-indigo-300 flex items-center gap-1 font-mono transition-colors disabled:opacity-50"
          title="Refresh Metadata Index"
        >
          <RefreshCw size={12} className={refreshing ? 'animate-spin' : ''} />
          {refreshing ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>

      <div className="space-y-2">
        {metadata.groups.map((group, groupIdx) => {
          const isOpen = !!openGroups[groupIdx];
          return (
            <div key={groupIdx} className="rounded-lg bg-zinc-900/60 border border-zinc-800 overflow-hidden">
              <button
                onClick={() => toggleGroup(groupIdx)}
                className="w-full px-3 py-2 bg-zinc-900 flex items-center justify-between text-xs font-semibold text-zinc-200 hover:bg-zinc-800/80 transition-colors"
              >
                <span className="font-mono text-[11px] text-indigo-300">{group.category}</span>
                {isOpen ? <ChevronDown size={14} className="text-zinc-400" /> : <ChevronRight size={14} className="text-zinc-400" />}
              </button>

              {isOpen && (
                <div className="p-3 space-y-1.5 bg-zinc-950/60 divide-y divide-zinc-900/80">
                  {group.items.map((item, itemIdx) => (
                    <div key={itemIdx} className="flex justify-between items-start pt-1.5 text-[11px]">
                      <span className="text-zinc-500 font-mono">{item.key}:</span>
                      <span className="font-mono text-zinc-200 text-right break-all max-w-[200px]">
                        {item.value !== null && item.value !== undefined ? String(item.value) : 'N/A'}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
