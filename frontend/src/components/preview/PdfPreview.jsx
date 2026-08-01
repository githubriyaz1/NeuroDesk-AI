import React from 'react';
import { FileText, BookOpen, User, HardDrive } from 'lucide-react';
import { formatBytes } from '../../utils/formatters';

export const PdfPreview = ({ content, metadata }) => {
  const title = content?.title || metadata?.metadata?.title || 'PDF Document';
  const author = content?.author || metadata?.metadata?.author || 'Unknown Author';
  const pageCount = content?.page_count || metadata?.metadata?.page_count || 1;
  const sampleText = content?.sample_text || '';

  return (
    <div className="space-y-4 text-xs">
      {/* Header Info Card */}
      <div className="p-4 rounded-xl bg-zinc-900/90 border border-zinc-800 flex items-start gap-4">
        <div className="p-3 rounded-lg bg-rose-600/10 text-rose-400 border border-rose-500/20">
          <FileText size={24} />
        </div>
        <div className="space-y-1 flex-1">
          <h3 className="text-sm font-bold text-zinc-100">{title}</h3>
          <div className="flex flex-wrap gap-4 text-zinc-400 text-[11px] font-mono">
            <span className="flex items-center gap-1">
              <User size={12} /> {author}
            </span>
            <span className="flex items-center gap-1 text-indigo-400">
              <BookOpen size={12} /> {pageCount} Pages
            </span>
            <span className="flex items-center gap-1 text-zinc-500">
              <HardDrive size={12} /> {formatBytes(metadata?.file_size || 0)}
            </span>
          </div>
        </div>
      </div>

      {/* Extracted Document Text Preview */}
      <div className="space-y-2">
        <h4 className="text-[11px] font-mono uppercase text-zinc-500 tracking-wider">
          Page 1 Content Extract
        </h4>
        <div className="p-4 rounded-xl bg-zinc-950 border border-zinc-800/80 font-mono text-[11px] text-zinc-300 whitespace-pre-wrap leading-relaxed max-h-80 overflow-y-auto">
          {sampleText || 'No text extracted from PDF page 1.'}
        </div>
      </div>
    </div>
  );
};
