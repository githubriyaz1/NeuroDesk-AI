import React from 'react';
import { Lock, Globe } from 'lucide-react';

const METHOD_COLORS = {
  GET: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
  POST: 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30',
  PUT: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
  DELETE: 'bg-rose-500/20 text-rose-300 border-rose-500/30',
};

export default function APIViewer({ apiContracts }) {
  if (!apiContracts || !apiContracts.endpoints) {
    return <div className="text-slate-500 text-xs">No REST API specifications found.</div>;
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between bg-slate-900 border border-slate-800 p-3 rounded-xl">
        <div>
          <span className="text-xs font-semibold text-slate-400">Base API URL: </span>
          <code className="text-xs font-mono text-cyan-400 ml-1">{apiContracts.base_url || '/api/v1'}</code>
        </div>
        <div className="text-xs text-slate-400">
          Auth: <span className="text-slate-200 font-medium">{apiContracts.authentication_strategy?.type || 'Bearer JWT'}</span>
        </div>
      </div>

      <div className="grid gap-3">
        {apiContracts.endpoints.map((ep, idx) => {
          const badgeStyle = METHOD_COLORS[ep.method] || 'bg-slate-800 text-slate-300';
          return (
            <div key={idx} className="bg-slate-900/80 border border-slate-800 rounded-xl p-3.5 space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className={`px-2.5 py-0.5 rounded text-[11px] font-bold font-mono border ${badgeStyle}`}>
                    {ep.method}
                  </span>
                  <code className="text-xs font-mono text-slate-100 font-semibold">{ep.path}</code>
                </div>
                <div className="flex items-center gap-1.5 text-[11px] text-slate-400">
                  {ep.auth_required ? (
                    <span className="flex items-center gap-1 text-amber-400/80">
                      <Lock size={12} /> Auth
                    </span>
                  ) : (
                    <span className="flex items-center gap-1 text-slate-500">
                      <Globe size={12} /> Public
                    </span>
                  )}
                </div>
              </div>
              <p className="text-xs text-slate-300">{ep.summary}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
}
