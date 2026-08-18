import React, { useState, useEffect } from 'react';
import { Database, RefreshCw, X, ShieldCheck, Cpu } from 'lucide-react';
import knowledgeService from '../../services/knowledgeService';
import { CitationCard } from './CitationCard';

export const KnowledgePanel = ({ isOpen, onClose, queryResult }) => {
  const [diagnostics, setDiagnostics] = useState(null);
  const [isIndexing, setIsIndexing] = useState(false);

  const fetchDiagnostics = async () => {
    try {
      const data = await knowledgeService.getDiagnostics();
      setDiagnostics(data);
    } catch (err) {
      console.error('Failed to fetch knowledge diagnostics:', err);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchDiagnostics();
    }
  }, [isOpen]);

  const handleRefreshIndex = async () => {
    try {
      setIsIndexing(true);
      await knowledgeService.triggerIndexing();
      await fetchDiagnostics();
    } catch (err) {
      console.error('Failed to refresh knowledge index:', err);
    } finally {
      setIsIndexing(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-y-0 right-0 w-96 bg-slate-900 border-l border-slate-800 shadow-2xl z-50 flex flex-col backdrop-blur-xl">
      {/* Header */}
      <div className="p-4 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-2 text-slate-100 font-semibold">
          <Database className="w-5 h-5 text-blue-400" />
          <span>Knowledge Engine</span>
        </div>
        <button
          onClick={onClose}
          className="p-1.5 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded-lg"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Content Body */}
      <div className="flex-1 overflow-y-auto p-4 space-y-6 custom-scrollbar">
        {/* Diagnostics & Stats */}
        {diagnostics && (
          <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-3.5 space-y-3">
            <div className="flex items-center justify-between text-xs font-semibold text-slate-200">
              <span className="flex items-center gap-1.5">
                <Cpu className="w-4 h-4 text-indigo-400" /> Engine Diagnostics
              </span>
              <button
                onClick={handleRefreshIndex}
                disabled={isIndexing}
                className="flex items-center gap-1 text-blue-400 hover:text-blue-300 disabled:opacity-50"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${isIndexing ? 'animate-spin' : ''}`} /> Refresh Index
              </button>
            </div>

            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="bg-slate-900/60 p-2 rounded-lg border border-slate-800">
                <span className="text-[11px] text-slate-400 block">Indexed Assets</span>
                <span className="text-sm font-bold text-slate-100">{diagnostics.indexed_assets_count}</span>
              </div>
              <div className="bg-slate-900/60 p-2 rounded-lg border border-slate-800">
                <span className="text-[11px] text-slate-400 block">Retrieval Latency</span>
                <span className="text-sm font-bold text-emerald-400">{diagnostics.average_retrieval_latency_ms}ms</span>
              </div>
            </div>
          </div>
        )}

        {/* Retrieved Citations Section */}
        <div className="space-y-3">
          <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
            Retrieved Sources ({queryResult?.citations?.length || 0})
          </h4>

          {queryResult?.citations && queryResult.citations.length > 0 ? (
            <div className="space-y-2">
              {queryResult.citations.map((citation, idx) => (
                <CitationCard key={idx} citation={citation} />
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-slate-500 text-xs bg-slate-800/30 border border-slate-800 rounded-xl">
              No citations retrieved for current session.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
