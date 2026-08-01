import React, { useState, useRef } from 'react';
import { Modal } from '../common/Modal';
import { Button } from '../common/Button';
import { UploadCloud, File, X, CheckCircle2, AlertCircle, RefreshCw } from 'lucide-react';
import { assetService } from '../../services/assetService';
import { formatBytes } from '../../utils/formatters';

export const UploadModal = ({ isOpen, onClose, onSuccess }) => {
  const [dragActive, setDragActive] = useState(false);
  const [queue, setQueue] = useState([]); // [{ id, file, progress, status, error }]
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      addFilesToQueue(Array.from(e.dataTransfer.files));
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      addFilesToQueue(Array.from(e.target.files));
    }
  };

  const addFilesToQueue = (files) => {
    const newItems = files.map((file) => ({
      id: Math.random().toString(36).substring(7),
      file,
      progress: 0,
      status: 'pending', // pending, uploading, success, error
      error: null,
    }));
    setQueue((prev) => [...prev, ...newItems]);
  };

  const removeFile = (id) => {
    setQueue((prev) => prev.filter((item) => item.id !== id));
  };

  const uploadSingleItem = async (item) => {
    setQueue((prev) =>
      prev.map((i) => (i.id === item.id ? { ...i, status: 'uploading', progress: 0, error: null } : i))
    );

    try {
      await assetService.uploadAsset(item.file, '', (pct) => {
        setQueue((prev) =>
          prev.map((i) => (i.id === item.id ? { ...i, progress: pct } : i))
        );
      });

      setQueue((prev) =>
        prev.map((i) => (i.id === item.id ? { ...i, status: 'success', progress: 100 } : i))
      );
    } catch (err) {
      const errMsg = err.message || 'Upload failed';
      setQueue((prev) =>
        prev.map((i) => (i.id === item.id ? { ...i, status: 'error', error: errMsg } : i))
      );
    }
  };

  const handleUploadAll = async () => {
    setUploading(true);
    const pendingItems = queue.filter((i) => i.status === 'pending' || i.status === 'error');
    
    for (const item of pendingItems) {
      await uploadSingleItem(item);
    }
    
    setUploading(false);
    if (onSuccess) onSuccess();
  };

  const handleClose = () => {
    setQueue([]);
    setUploading(false);
    onClose();
  };

  return (
    <Modal isOpen={isOpen} onClose={handleClose} title="Upload Digital Assets to DAMS">
      <div className="space-y-4">
        {/* Drag & Drop Area */}
        <div
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-all ${
            dragActive
              ? 'border-indigo-500 bg-indigo-500/10'
              : 'border-zinc-800 hover:border-zinc-700 bg-zinc-950/60'
          }`}
        >
          <input
            ref={fileInputRef}
            type="file"
            multiple
            onChange={handleFileChange}
            className="hidden"
          />
          <div className="flex flex-col items-center justify-center gap-2">
            <div className="p-3 rounded-full bg-indigo-600/10 text-indigo-400 border border-indigo-500/20">
              <UploadCloud size={24} />
            </div>
            <div>
              <p className="text-xs font-semibold text-zinc-200">
                Click to browse or drag & drop files here
              </p>
              <p className="text-[11px] text-zinc-500 mt-0.5">
                Supports Documents, Datasets, Images, Reports, Prompts, Models up to 100MB
              </p>
            </div>
          </div>
        </div>

        {/* Upload Queue List */}
        {queue.length > 0 && (
          <div className="space-y-2 max-h-60 overflow-y-auto pr-1">
            <h4 className="text-xs font-semibold text-zinc-400 font-mono uppercase tracking-wider">
              Upload Queue ({queue.length})
            </h4>
            {queue.map((item) => (
              <div
                key={item.id}
                className="p-3 rounded-lg bg-zinc-900/90 border border-zinc-800 flex flex-col gap-2 text-xs"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 min-w-0">
                    <File size={16} className="text-zinc-400 flex-shrink-0" />
                    <span className="truncate font-medium text-zinc-200">{item.file.name}</span>
                    <span className="text-[10px] font-mono text-zinc-500 flex-shrink-0">
                      ({formatBytes(item.file.size)})
                    </span>
                  </div>

                  <div className="flex items-center gap-2 flex-shrink-0">
                    {item.status === 'success' && (
                      <span className="inline-flex items-center gap-1 text-emerald-400 text-[11px] font-semibold">
                        <CheckCircle2 size={14} /> Ready
                      </span>
                    )}
                    {item.status === 'error' && (
                      <div className="flex items-center gap-1 text-rose-400 text-[11px]">
                        <AlertCircle size={14} />
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            uploadSingleItem(item);
                          }}
                          className="hover:underline flex items-center gap-1 text-indigo-400 ml-1"
                        >
                          <RefreshCw size={12} /> Retry
                        </button>
                      </div>
                    )}
                    {item.status === 'pending' && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          removeFile(item.id);
                        }}
                        className="text-zinc-500 hover:text-zinc-300"
                      >
                        <X size={14} />
                      </button>
                    )}
                  </div>
                </div>

                {/* Progress Bar */}
                {item.status === 'uploading' && (
                  <div className="w-full bg-zinc-800 rounded-full h-1.5 overflow-hidden">
                    <div
                      className="bg-indigo-500 h-1.5 transition-all duration-200"
                      style={{ width: `${item.progress}%` }}
                    />
                  </div>
                )}
                {item.error && <p className="text-[10px] text-rose-400">{item.error}</p>}
              </div>
            ))}
          </div>
        )}

        {/* Modal Actions */}
        <div className="flex justify-end gap-2 pt-3 border-t border-zinc-800">
          <Button variant="outline" size="sm" onClick={handleClose} disabled={uploading}>
            Done / Close
          </Button>
          {queue.some((i) => i.status === 'pending' || i.status === 'error') && (
            <Button size="sm" onClick={handleUploadAll} isLoading={uploading}>
              Start Upload ({queue.filter((i) => i.status === 'pending' || i.status === 'error').length})
            </Button>
          )}
        </div>
      </div>
    </Modal>
  );
};
