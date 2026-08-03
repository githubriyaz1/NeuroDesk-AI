import React, { useState } from 'react';
import { Terminal, X, CheckCircle2, XCircle, Clock, ChevronRight, Layers } from 'lucide-react';

export const ExecutionConsole = ({ execution, onClose }) => {
  const [activeTab, setActiveTab] = useState('summary'); // summary, nodes, logs

  if (!execution) {
    return (
      <div className="h-64 bg-slate-950 border-t border-slate-800 p-4 font-mono text-xs text-slate-500 flex items-center justify-center">
        No execution trace available. Click "Run Execution" to execute workflow.
      </div>
    );
  }

  return (
    <div className="h-72 bg-slate-950/95 border-t border-slate-800 flex flex-col font-mono text-xs backdrop-blur-md z-30 shadow-2xl">
      {/* Console Header */}
      <div className="h-10 px-4 bg-slate-900 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2 text-cyan-400">
            <Terminal className="w-4 h-4" />
            <span className="font-bold">Execution Console</span>
          </div>

          <div className="flex items-center space-x-1 border-l border-slate-800 pl-4">
            <button
              type="button"
              onClick={() => setActiveTab('summary')}
              className={`px-3 py-1 rounded-md transition-colors ${
                activeTab === 'summary' ? 'bg-slate-800 text-slate-100 font-semibold' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Summary
            </button>
            <button
              type="button"
              onClick={() => setActiveTab('nodes')}
              className={`px-3 py-1 rounded-md transition-colors ${
                activeTab === 'nodes' ? 'bg-slate-800 text-slate-100 font-semibold' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Nodes ({execution.nodes?.length || 0})
            </button>
            <button
              type="button"
              onClick={() => setActiveTab('logs')}
              className={`px-3 py-1 rounded-md transition-colors ${
                activeTab === 'logs' ? 'bg-slate-800 text-slate-100 font-semibold' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Logs ({execution.logs?.length || 0})
            </button>
          </div>
        </div>

        <button
          type="button"
          onClick={onClose}
          className="p-1 text-slate-400 hover:text-slate-200 rounded-md hover:bg-slate-800"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Tab Contents */}
      <div className="flex-1 overflow-y-auto p-4 text-slate-300">
        {activeTab === 'summary' && (
          <div className="space-y-4">
            <div className="grid grid-cols-4 gap-4">
              <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                <span className="text-slate-500 block text-[10px] uppercase font-bold">Status</span>
                <span
                  className={`font-bold uppercase ${
                    execution.status === 'SUCCESS'
                      ? 'text-emerald-400'
                      : execution.status === 'FAILED'
                      ? 'text-rose-400'
                      : 'text-amber-400'
                  }`}
                >
                  {execution.status}
                </span>
              </div>
              <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                <span className="text-slate-500 block text-[10px] uppercase font-bold">Total Latency</span>
                <span className="font-bold text-cyan-400">{execution.total_latency_ms} ms</span>
              </div>
              <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                <span className="text-slate-500 block text-[10px] uppercase font-bold">Trigger Source</span>
                <span className="font-bold text-purple-400 uppercase">{execution.trigger_source}</span>
              </div>
              <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                <span className="text-slate-500 block text-[10px] uppercase font-bold">Execution ID</span>
                <span className="font-bold text-slate-300 text-[10px] truncate block">{execution.id}</span>
              </div>
            </div>

            {/* Execution Final Output */}
            <div>
              <span className="text-slate-400 font-bold block mb-1">Final Output Payload:</span>
              <pre className="p-3 rounded-lg bg-slate-900 border border-slate-800 text-[11px] text-cyan-300 overflow-x-auto">
                {JSON.stringify(execution.outputs || {}, null, 2)}
              </pre>
            </div>
          </div>
        )}

        {activeTab === 'nodes' && (
          <div className="space-y-2">
            {(execution.nodes || []).map((node) => (
              <div
                key={node.id}
                className="p-3 rounded-lg bg-slate-900 border border-slate-800 flex items-center justify-between"
              >
                <div className="flex items-center space-x-3">
                  {node.status === 'SUCCESS' ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  ) : (
                    <XCircle className="w-4 h-4 text-rose-400" />
                  )}
                  <div>
                    <span className="font-bold text-slate-200">{node.node_id}</span>
                    <span className="text-slate-500 text-[10px] ml-2">({node.node_type})</span>
                  </div>
                </div>

                <div className="flex items-center space-x-4 text-[11px]">
                  <span className="text-slate-400 font-mono">{node.latency_ms} ms</span>
                  <span
                    className={`font-semibold ${
                      node.status === 'SUCCESS' ? 'text-emerald-400' : 'text-rose-400'
                    }`}
                  >
                    {node.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'logs' && (
          <div className="space-y-1 font-mono text-[11px]">
            {(execution.logs || []).map((log, idx) => (
              <div key={idx} className="py-1 border-b border-slate-900 flex space-x-3">
                <span className="text-slate-600 font-bold">{log.timestamp ? new Date(log.timestamp).toLocaleTimeString() : 'LOG'}</span>
                <span
                  className={`font-bold ${
                    log.log_level === 'ERROR'
                      ? 'text-rose-400'
                      : log.log_level === 'WARN'
                      ? 'text-amber-400'
                      : 'text-cyan-400'
                  }`}
                >
                  [{log.log_level}]
                </span>
                <span className="text-slate-300">{log.message}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
