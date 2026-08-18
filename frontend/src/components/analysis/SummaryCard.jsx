import React from 'react';
import { FileText, CheckCircle, Tag } from 'lucide-react';

export const SummaryCard = ({ summary, keyPoints = [], keywords = [] }) => {
  return (
    <div className="bg-slate-800/80 border border-slate-700/60 rounded-xl p-4 space-y-4 shadow-md">
      <div className="flex items-center gap-2 text-slate-100 font-semibold text-sm">
        <FileText className="w-4 h-4 text-blue-400" />
        <span>Executive Summary</span>
      </div>

      <p className="text-xs text-slate-300 leading-relaxed bg-slate-900/60 p-3 rounded-lg border border-slate-800">
        {summary || 'No summary available.'}
      </p>

      {keyPoints.length > 0 && (
        <div className="space-y-2">
          <h5 className="text-xs font-semibold text-slate-300 uppercase tracking-wider">Key Highlights</h5>
          <ul className="space-y-1.5">
            {keyPoints.map((pt, idx) => (
              <li key={idx} className="flex items-start gap-2 text-xs text-slate-300">
                <CheckCircle className="w-3.5 h-3.5 text-emerald-400 mt-0.5 shrink-0" />
                <span>{pt}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {keywords.length > 0 && (
        <div className="flex flex-wrap gap-1.5 pt-2">
          {keywords.map((word, idx) => (
            <span key={idx} className="flex items-center gap-1 text-[11px] bg-slate-700/60 text-slate-300 px-2 py-0.5 rounded-md">
              <Tag className="w-3 h-3 text-indigo-400" /> {word}
            </span>
          ))}
        </div>
      )}
    </div>
  );
};
