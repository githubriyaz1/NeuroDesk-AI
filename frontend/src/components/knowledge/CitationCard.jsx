import React from 'react';
import { FileText, Table, Database, Tag, ShieldCheck } from 'lucide-react';

export const CitationCard = ({ citation }) => {
  const getSourceIcon = (type) => {
    switch (type?.toLowerCase()) {
      case 'pdf':
        return <FileText className="w-4 h-4 text-red-400" />;
      case 'csv':
      case 'excel':
        return <Table className="w-4 h-4 text-emerald-400" />;
      case 'metadata':
      case 'image_metadata':
        return <Tag className="w-4 h-4 text-purple-400" />;
      default:
        return <Database className="w-4 h-4 text-blue-400" />;
    }
  };

  const confidencePct = Math.round((citation.confidence_score || 0.8) * 100);

  return (
    <div className="p-3 bg-slate-800/80 border border-slate-700/60 rounded-xl space-y-2 hover:border-blue-500/50 transition-colors">
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2 min-w-0">
          {getSourceIcon(citation.source_type)}
          <span className="text-xs font-semibold text-slate-200 truncate">
            {citation.asset_name}
          </span>
        </div>
        <span className="flex items-center gap-1 text-[10px] font-mono bg-blue-500/20 text-blue-300 border border-blue-400/30 px-2 py-0.5 rounded-full">
          <ShieldCheck className="w-3 h-3" /> {confidencePct}% Match
        </span>
      </div>

      {(citation.page_number || citation.section) && (
        <div className="flex items-center gap-2 text-[11px] text-slate-400 font-mono">
          {citation.page_number && <span>Page {citation.page_number}</span>}
          {citation.section && <span>Section: {citation.section}</span>}
        </div>
      )}

      <p className="text-xs text-slate-300 line-clamp-3 bg-slate-900/50 p-2 rounded-lg font-sans">
        "{citation.snippet}"
      </p>
    </div>
  );
};
