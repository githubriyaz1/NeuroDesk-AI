import React from 'react';
import { History, Copy, Clock } from 'lucide-react';

export default function BlueprintHistoryPanel({ versions = [], currentVersion, onClone }) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-4">
      <div className="flex items-center justify-between">
        <h4 className="text-xs font-semibold text-slate-300 flex items-center gap-1.5 uppercase tracking-wider">
          <History size={14} className="text-cyan-400" /> Blueprint Version Snapshots
        </h4>
        <button
          onClick={onClone}
          className="flex items-center gap-1 text-xs text-cyan-400 bg-slate-950 border border-slate-800 px-2.5 py-1 rounded-md hover:bg-slate-800 transition-colors"
        >
          <Copy size={12} /> Clone Blueprint
        </button>
      </div>

      <div className="space-y-2">
        {versions.length === 0 ? (
          <div className="text-slate-500 text-xs italic">Version 1 (Initial Generation)</div>
        ) : (
          versions.map((v, idx) => (
            <div
              key={idx}
              className={`p-3 rounded-lg border text-xs flex items-center justify-between ${
                v.version_number === currentVersion
                  ? 'bg-cyan-500/10 border-cyan-500/30 text-cyan-300'
                  : 'bg-slate-950 border-slate-800/80 text-slate-400'
              }`}
            >
              <div>
                <span className="font-mono font-bold text-slate-200">v{v.version_number}</span>
                <span className="ml-2 text-slate-400">{v.changelog || 'Snapshot'}</span>
              </div>
              <div className="flex items-center gap-1 text-[11px] text-slate-500">
                <Clock size={11} /> {new Date(v.created_at || Date.now()).toLocaleDateString()}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
