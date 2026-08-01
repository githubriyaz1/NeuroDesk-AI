import React, { useState } from 'react';
import { Image as ImageIcon, ZoomIn, ZoomOut, Maximize2 } from 'lucide-react';
import { previewService } from '../../services/previewService';

export const ImagePreview = ({ asset, content, metadata }) => {
  const [zoom, setZoom] = useState(100);
  const dims = content?.dimensions || metadata?.metadata || {};
  const width = dims.width || 0;
  const height = dims.height || 0;
  const format = content?.format || metadata?.metadata?.format || 'PNG';

  const thumbnailUrl = previewService.getThumbnailUrl(asset.id);

  return (
    <div className="space-y-3 text-xs">
      {/* Controls Bar */}
      <div className="flex items-center justify-between p-3 rounded-xl bg-zinc-900/90 border border-zinc-800">
        <div className="flex items-center gap-2 font-mono text-zinc-300">
          <ImageIcon size={16} className="text-indigo-400" />
          <span>{width} × {height} px</span>
          <span className="text-zinc-500 uppercase">({format})</span>
        </div>

        <div className="flex items-center gap-1">
          <button
            onClick={() => setZoom((z) => Math.max(50, z - 25))}
            className="p-1 rounded hover:bg-zinc-800 text-zinc-400 hover:text-zinc-200"
            title="Zoom Out"
          >
            <ZoomOut size={14} />
          </button>
          <span className="font-mono text-[11px] text-zinc-400 w-10 text-center">{zoom}%</span>
          <button
            onClick={() => setZoom((z) => Math.min(200, z + 25))}
            className="p-1 rounded hover:bg-zinc-800 text-zinc-400 hover:text-zinc-200"
            title="Zoom In"
          >
            <ZoomIn size={14} />
          </button>
          <button
            onClick={() => setZoom(100)}
            className="p-1 rounded hover:bg-zinc-800 text-zinc-400 hover:text-zinc-200 ml-1"
            title="Reset Zoom"
          >
            <Maximize2 size={14} />
          </button>
        </div>
      </div>

      {/* Image Display Canvas */}
      <div className="p-4 rounded-xl bg-zinc-950 border border-zinc-800/80 flex items-center justify-center min-h-[240px] max-h-96 overflow-auto">
        <img
          src={thumbnailUrl}
          alt={asset.name}
          style={{ width: `${zoom}%`, maxHeight: '350px', objectFit: 'contain' }}
          className="rounded-lg shadow-lg transition-all duration-200"
          onError={(e) => {
            e.target.style.display = 'none';
          }}
        />
      </div>
    </div>
  );
};
