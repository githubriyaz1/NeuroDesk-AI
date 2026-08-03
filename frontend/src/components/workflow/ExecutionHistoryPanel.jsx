import React, { useState } from 'react';
import { History, X, CheckCircle2, XCircle, Clock, ArrowRight } from 'lucide-react';

export const ExecutionHistoryPanel = ({ executions = [], onSelectExecution, onClose }) => {
  const [filter, setFilter] = useState('ALL');

  const filteredExecutions = executions.filter((e) => {
    if (filter === 'ALL') return true;
    return e.status === filter;
  });

  return (
    <aside className="w-80 bg-slate-900/95 border-l border-slate-800 flex flex-col backdrop-blur-md z-20 shadow-2xl">
      <div className="p-4 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <History className="w-4 h-4 text-purple-400" />
          <h3 className="text-sm font-bold text-slate-100">Execution History</h3>
        </div>
        <button
          type="button"
          onClick={onClose}
          className="p-1 text-slate-400 hover:text-slate-200 rounded-md hover:bg-slate-800 transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Filter Selector */}
      <div className="p-3 border-b border-slate-800/80 flex items-center space-x-1">
        {['ALL', 'SUCCESS', 'FAILED', 'RUNNING'].map((st) => (
          <button
            key={st}
            type="button"
            onClick={() => setFilter(st)}
            className={`px-2.5 py-1 rounded text-[10px] font-semibold transition-colors ${
              filter === st
                ? 'bg-purple-500/20 text-purple-300 border border-purple-500/40'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
            }`}
          >
            {st}
          </button>
        ))}
      </div>

      {/* Execution List */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2 text-xs">
        {filteredExecutions.length === 0 ? (
          <div className="text-slate-500 text-center py-8">No executions recorded yet.</div>
        ) : (
          filteredExecutions.map((exec) => (
            <div
              key={exec.id}
              onClick={() => onSelectExecution(exec)}
              className="p-3 rounded-xl bg-slate-950/60 hover:bg-slate-800/80 border border-slate-800/80 hover:border-purple-500/40 cursor-pointer transition-all space-y-2 group"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  {exec.status === 'SUCCESS' ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  ) : (
                    <XCircle className="w-4 h-4 text-rose-400" />
                  )}
                  <span className="font-semibold text-slate-200 uppercase text-[11px]">{exec.status}</span>
                </div>
                <span className="text-[10px] font-mono text-cyan-400">{exec.total_latency_ms} ms</span>
              </div>

              <div className="flex justify-between items-center text-[10px] text-slate-500">
                <span>{exec.created_at ? new Date(exec.created_at).toLocaleString() : 'Just now'}</span>
                <div className="flex items-center space-x-1 group-hover:text-purple-400">
                  <span>Trace</span>
                  <ArrowRight className="w-3 h-3" />
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </aside>
  );
};
