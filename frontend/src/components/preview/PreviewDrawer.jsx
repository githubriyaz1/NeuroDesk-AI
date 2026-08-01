import React, { useEffect, useState } from 'react';
import { X, Download, RefreshCw, Eye, ShieldCheck, FileText } from 'lucide-react';
import { Button } from '../common/Button';
import { Badge } from '../common/Badge';
import { LoadingSpinner } from '../common/LoadingSpinner';
import { previewService } from '../../services/previewService';
import { formatBytes, formatDate } from '../../utils/formatters';

import { PdfPreview } from './PdfPreview';
import { CsvPreview } from './CsvPreview';
import { ExcelPreview } from './ExcelPreview';
import { ImagePreview } from './ImagePreview';
import { UnsupportedPreview } from './UnsupportedPreview';

export const PreviewDrawer = ({ isOpen, onClose, asset, onDownload }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [previewData, setPreviewData] = useState(null);
  const [metadataData, setMetadataData] = useState(null);

  const fetchPreviewData = async () => {
    if (!asset) return;
    try {
      setLoading(true);
      setError(null);
      const [previewRes, metadataRes] = await Promise.all([
        previewService.getPreview(asset.id),
        previewService.getMetadata(asset.id),
      ]);
      setPreviewData(previewRes);
      setMetadataData(metadataRes);
    } catch (err) {
      console.error('Failed to load asset preview:', err);
      setError(err.message || 'Failed to generate preview for asset.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen && asset) {
      fetchPreviewData();
    } else {
      setPreviewData(null);
      setMetadataData(null);
    }
  }, [isOpen, asset]);

  if (!isOpen || !asset) return null;

  const previewType = previewData?.preview_type || 'UNSUPPORTED';

  const renderPreviewComponent = () => {
    if (loading) {
      return (
        <div className="py-12">
          <LoadingSpinner label="Universal Preview Engine loading payload..." />
        </div>
      );
    }

    if (error) {
      return (
        <div className="p-6 rounded-xl bg-rose-500/10 border border-rose-500/20 text-center space-y-3 my-4">
          <p className="text-xs text-rose-400 font-medium">{error}</p>
          <Button variant="outline" size="sm" onClick={fetchPreviewData}>
            <RefreshCw size={12} className="mr-1.5" /> Retry Preview
          </Button>
        </div>
      );
    }

    switch (previewType) {
      case 'PDF':
        return <PdfPreview content={previewData?.content} metadata={metadataData} />;
      case 'CSV':
        return <CsvPreview content={previewData?.content} />;
      case 'EXCEL':
        return <ExcelPreview content={previewData?.content} />;
      case 'IMAGE':
        return <ImagePreview asset={asset} content={previewData?.content} metadata={metadataData} />;
      default:
        return <UnsupportedPreview asset={asset} content={previewData?.content} onDownload={onDownload} />;
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-black/70 backdrop-blur-sm transition-opacity">
      <div className="absolute inset-y-0 right-0 max-w-full flex pl-10">
        <div className="w-screen max-w-2xl bg-zinc-950 border-l border-zinc-800 shadow-2xl flex flex-col">
          {/* Header */}
          <div className="p-4 sm:p-5 border-b border-zinc-800/80 flex items-center justify-between">
            <div className="flex items-center gap-3 min-w-0">
              <div className="p-2.5 rounded-lg bg-indigo-600/10 text-indigo-400 border border-indigo-500/20">
                <Eye size={20} />
              </div>
              <div className="min-w-0">
                <h3 className="text-sm font-bold text-zinc-100 truncate">{asset.name}</h3>
                <div className="flex items-center gap-2 mt-0.5 text-[11px] font-mono text-zinc-500">
                  <Badge variant="indigo">{previewType}</Badge>
                  <span>{formatBytes(asset.file_size)}</span>
                  <span>v{asset.version}</span>
                </div>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-zinc-400 hover:text-zinc-100 hover:bg-zinc-900 transition-colors"
            >
              <X size={18} />
            </button>
          </div>

          {/* Body */}
          <div className="flex-1 overflow-y-auto p-4 sm:p-5 space-y-5">
            {/* Metadata Summary Strip */}
            <div className="p-3 rounded-lg bg-zinc-900/60 border border-zinc-800 text-xs flex flex-wrap justify-between gap-2 text-zinc-400">
              <div>
                <span className="text-zinc-500 font-mono">Original Name: </span>
                <span className="text-zinc-200 font-medium">{asset.original_filename}</span>
              </div>
              <div>
                <span className="text-zinc-500 font-mono">MIME: </span>
                <span className="text-indigo-400 font-mono">{asset.mime_type}</span>
              </div>
            </div>

            {/* Renderer Container */}
            {renderPreviewComponent()}
          </div>

          {/* Footer */}
          <div className="p-4 sm:p-5 border-t border-zinc-800/80 bg-zinc-950 flex items-center justify-between">
            <div className="flex items-center gap-1.5 text-[11px] font-mono text-zinc-500">
              <ShieldCheck size={14} className="text-emerald-400" />
              <span>Verified Preview Stream</span>
            </div>
            <Button size="sm" onClick={() => onDownload(asset.id, asset.original_filename)}>
              <Download size={14} className="mr-1.5" /> Download Full Asset
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};
