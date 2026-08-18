import React, { useState } from 'react';
import { Download, FileText, Code, Check } from 'lucide-react';
import { generatorService } from '../../services/generatorService';

export default function ExportDialog({ blueprintId, onClose }) {
  const [format, setFormat] = useState('markdown');
  const [exporting, setExporting] = useState(false);
  const [exportedData, setExportedData] = useState(null);

  const handleExport = async () => {
    setExporting(true);
    try {
      const res = await generatorService.exportBlueprint({ blueprint_id: blueprintId, format });
      setExportedData(res);
    } catch (err) {
      alert(`Export failed: ${err.message}`);
    } finally {
      setExporting(false);
    }
  };

  const downloadFile = () => {
    if (!exportedData) return;
    const blob = new Blob([exportedData.content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = exportedData.filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-md p-6 space-y-5">
        <div className="flex items-center justify-between">
          <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
            <Download size={18} className="text-cyan-400" /> Export Project Specification
          </h3>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-200 text-xs">✕</button>
        </div>

        <div className="space-y-2">
          <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider">Format</label>
          <div className="grid grid-cols-3 gap-2">
            {['markdown', 'json', 'yaml'].map((fmt) => (
              <button
                key={fmt}
                type="button"
                onClick={() => setFormat(fmt)}
                className={`py-2 px-3 rounded-lg text-xs font-bold uppercase transition-colors border ${
                  format === fmt
                    ? 'bg-cyan-500/20 border-cyan-500/50 text-cyan-300'
                    : 'bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-700'
                }`}
              >
                {fmt}
              </button>
            ))}
          </div>
        </div>

        {exportedData ? (
          <div className="space-y-3">
            <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-xl text-xs text-emerald-300 flex items-center gap-2">
              <Check size={14} /> Ready for download: {exportedData.filename}
            </div>
            <button
              onClick={downloadFile}
              className="w-full py-2.5 bg-cyan-500 text-slate-950 font-bold text-xs rounded-xl hover:bg-cyan-400 transition-colors flex items-center justify-center gap-2"
            >
              <Download size={14} /> Download Document
            </button>
          </div>
        ) : (
          <button
            onClick={handleExport}
            disabled={exporting}
            className="w-full py-2.5 bg-cyan-500 text-slate-950 font-bold text-xs rounded-xl hover:bg-cyan-400 disabled:opacity-50 transition-colors"
          >
            {exporting ? 'Generating Specification...' : 'Generate Export'}
          </button>
        )}
      </div>
    </div>
  );
}
