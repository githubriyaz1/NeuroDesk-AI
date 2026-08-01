import React from 'react';
import { AlertCircle, Download, FileCode } from 'lucide-react';
import { Button } from '../common/Button';
import { formatBytes } from '../../utils/formatters';

export const UnsupportedPreview = ({ asset, content, onDownload }) => {
  const message =
    content?.message ||
    `In-browser preview is currently unavailable for '.${asset?.extension?.lstrip('.') || 'this'}' files.`;

  return (
    <div className="p-6 rounded-xl bg-zinc-950 border border-zinc-800 text-center space-y-4 my-2">
      <div className="p-3 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20 inline-block">
        <FileCode size={28} />
      </div>

      <div className="space-y-1">
        <h3 className="text-sm font-bold text-zinc-100">No Preview Available Screen</h3>
        <p className="text-xs text-zinc-400 max-w-sm mx-auto leading-relaxed">{message}</p>
      </div>

      <div className="pt-2">
        <Button size="sm" onClick={() => onDownload(asset.id, asset.original_filename)}>
          <Download size={14} className="mr-1.5" /> Download File ({formatBytes(asset?.file_size || 0)})
        </Button>
      </div>
    </div>
  );
};
