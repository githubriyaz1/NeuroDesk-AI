import React from 'react';
import { GitCompare, ShieldCheck, PlusCircle, MinusCircle } from 'lucide-react';

export const ComparisonViewer = ({ comparisonReport }) => {
  if (!comparisonReport) return null;

  const {
    asset_a_name,
    asset_b_name,
    similarity_score,
    change_summary,
    added_information = [],
    removed_information = [],
    common_sections = [],
  } = comparisonReport;

  const similarityPct = Math.round(similarity_score * 100);

  return (
    <div className="bg-slate-800/80 border border-slate-700/60 rounded-xl p-4 space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-slate-100 font-semibold text-sm">
          <GitCompare className="w-4 h-4 text-purple-400" />
          <span>Asset Comparison Matrix</span>
        </div>
        <span className="flex items-center gap-1 text-xs font-mono bg-purple-500/20 text-purple-300 border border-purple-400/30 px-2.5 py-1 rounded-full">
          <ShieldCheck className="w-3.5 h-3.5" /> {similarityPct}% Similarity
        </span>
      </div>

      <p className="text-xs text-slate-300 bg-slate-900/60 p-3 rounded-lg border border-slate-800 leading-relaxed">
        {change_summary}
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {/* Added Information */}
        <div className="bg-emerald-500/10 border border-emerald-500/30 p-3 rounded-xl space-y-2">
          <div className="flex items-center gap-1.5 text-xs font-semibold text-emerald-400">
            <PlusCircle className="w-4 h-4" />
            <span>Added Information ({added_information.length})</span>
          </div>
          <ul className="space-y-1 text-xs text-slate-300 font-mono">
            {added_information.map((item, idx) => (
              <li key={idx}>+ {item}</li>
            ))}
          </ul>
        </div>

        {/* Removed Information */}
        <div className="bg-red-500/10 border border-red-500/30 p-3 rounded-xl space-y-2">
          <div className="flex items-center gap-1.5 text-xs font-semibold text-red-400">
            <MinusCircle className="w-4 h-4" />
            <span>Removed Information ({removed_information.length})</span>
          </div>
          <ul className="space-y-1 text-xs text-slate-300 font-mono">
            {removed_information.map((item, idx) => (
              <li key={idx}>- {item}</li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};
