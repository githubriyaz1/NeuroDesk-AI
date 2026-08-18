import React from 'react';
import { Layers, ShieldCheck, Zap, ArrowDown } from 'lucide-react';

export default function ArchitectureViewer({ architecture }) {
  if (!architecture) {
    return <div className="text-slate-500 text-xs">No architecture specification available.</div>;
  }

  return (
    <div className="space-y-6">
      {/* Pattern Header */}
      <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl flex items-center justify-between">
        <div>
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Architecture Pattern</span>
          <h3 className="text-sm font-bold text-cyan-400 mt-0.5">{architecture.pattern || '4-Tier Layered Pattern'}</h3>
        </div>
        <div className="flex items-center gap-2 text-xs text-slate-400 bg-slate-950 px-3 py-1.5 rounded-lg border border-slate-800">
          <Zap size={14} className="text-amber-400" /> Enterprise Ready
        </div>
      </div>

      {/* 4-Tier Stack Visualizer */}
      <div className="space-y-3">
        <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">4-Tier System Layers</h4>
        <div className="space-y-2">
          {(architecture.layers || []).map((layer, idx) => (
            <React.Fragment key={idx}>
              <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-3.5 flex items-center justify-between hover:border-cyan-500/30 transition-colors">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="w-6 h-6 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 text-xs font-bold flex items-center justify-center">
                      L{idx + 1}
                    </span>
                    <h5 className="text-xs font-bold text-slate-100">{layer.name}</h5>
                    <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-slate-800 text-cyan-300">
                      {layer.component}
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 pl-8">{layer.description}</p>
                </div>
              </div>
              {idx < (architecture.layers || []).length - 1 && (
                <div className="flex justify-center text-slate-600 my-1">
                  <ArrowDown size={16} />
                </div>
              )}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* Security & Scalability */}
      <div className="grid gap-4 md:grid-cols-2">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-2">
          <h4 className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
            <ShieldCheck size={16} className="text-emerald-400" /> Security Considerations
          </h4>
          <ul className="space-y-1.5 text-xs text-slate-400 pl-2">
            {(architecture.security || []).map((sec, sIdx) => (
              <li key={sIdx} className="list-disc list-inside">{sec}</li>
            ))}
          </ul>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-2">
          <h4 className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
            <Zap size={16} className="text-amber-400" /> Scalability Recommendations
          </h4>
          <ul className="space-y-1.5 text-xs text-slate-400 pl-2">
            {(architecture.scalability || []).map((sc, scIdx) => (
              <li key={scIdx} className="list-disc list-inside">{sc}</li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
