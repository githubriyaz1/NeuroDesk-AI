import React, { useState } from 'react';
import { X, FileUp, FileDown, Check } from 'lucide-react';
import { useChat } from '../../contexts/ChatContext';
import chatService from '../../services/chatService';

export const ImportExportModal = () => {
  const { modalState, setModalState, activeConversation, loadConversations, selectConversation } = useChat();
  const [exportFormat, setExportFormat] = useState('markdown');
  const [exportedContent, setExportedContent] = useState('');
  const [importJsonText, setImportJsonText] = useState('');
  const [copied, setCopied] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [isImporting, setIsImporting] = useState(false);

  if (!modalState.isExportOpen && !modalState.isImportOpen) return null;

  const handleExport = async (format) => {
    if (!activeConversation) return;
    try {
      setIsExporting(true);
      setExportFormat(format);
      const res = await chatService.exportConversation(activeConversation.id, format);
      setExportedContent(res.content);
    } catch (err) {
      console.error('Failed to export conversation:', err);
    } finally {
      setIsExporting(false);
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(exportedContent);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleImportSubmit = async () => {
    if (!importJsonText.trim()) return;
    try {
      setIsImporting(true);
      const parsed = JSON.parse(importJsonText);
      const imported = await chatService.importConversation(parsed);
      await loadConversations();
      await selectConversation(imported.id);
      setModalState({ isExportOpen: false, isImportOpen: false });
    } catch (err) {
      alert('Invalid JSON structure. Please verify the import format.');
      console.error('Failed to import conversation:', err);
    } finally {
      setIsImporting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-in fade-in duration-150">
      <div className="bg-slate-900 border border-slate-700/80 rounded-2xl max-w-xl w-full p-6 shadow-2xl space-y-4">
        {/* Modal Header */}
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div className="flex items-center gap-2 text-slate-100 font-semibold text-base">
            {modalState.isExportOpen ? (
              <>
                <FileDown className="w-5 h-5 text-blue-400" />
                <span>Export Conversation</span>
              </>
            ) : (
              <>
                <FileUp className="w-5 h-5 text-indigo-400" />
                <span>Import Conversation Backup</span>
              </>
            )}
          </div>
          <button
            onClick={() => setModalState({ isExportOpen: false, isImportOpen: false })}
            className="p-1 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Export View */}
        {modalState.isExportOpen && (
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <button
                onClick={() => handleExport('markdown')}
                className={`px-4 py-2 rounded-xl text-xs font-medium transition-all ${
                  exportFormat === 'markdown'
                    ? 'bg-blue-600 text-white shadow-md'
                    : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                }`}
              >
                Markdown (.md)
              </button>
              <button
                onClick={() => handleExport('json')}
                className={`px-4 py-2 rounded-xl text-xs font-medium transition-all ${
                  exportFormat === 'json'
                    ? 'bg-blue-600 text-white shadow-md'
                    : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                }`}
              >
                JSON Payload
              </button>
            </div>

            {exportedContent ? (
              <div className="relative">
                <textarea
                  readOnly
                  value={exportedContent}
                  className="w-full h-64 bg-slate-950 border border-slate-800 rounded-xl p-3 font-mono text-xs text-slate-300 focus:outline-none custom-scrollbar"
                />
                <button
                  onClick={handleCopy}
                  className="absolute right-3 top-3 bg-blue-600/90 hover:bg-blue-500 text-white px-3 py-1.5 rounded-lg text-xs font-medium shadow-md flex items-center gap-1.5"
                >
                  <Check className="w-4 h-4" />
                  <span>{copied ? 'Copied!' : 'Copy Code'}</span>
                </button>
              </div>
            ) : (
              <div className="text-center py-12 text-slate-400 text-xs">
                Select a format above to generate export content.
              </div>
            )}
          </div>
        )}

        {/* Import View */}
        {modalState.isImportOpen && (
          <div className="space-y-4">
            <p className="text-xs text-slate-400">
              Paste the exported conversation JSON payload below to restore messages into a new session.
            </p>
            <textarea
              value={importJsonText}
              onChange={(e) => setImportJsonText(e.target.value)}
              placeholder='{ "title": "Imported Session", "messages": [...] }'
              className="w-full h-60 bg-slate-950 border border-slate-800 rounded-xl p-3 font-mono text-xs text-slate-200 placeholder-slate-600 focus:outline-none focus:border-indigo-500 custom-scrollbar"
            />
            <div className="flex justify-end gap-2">
              <button
                onClick={() => setModalState({ isExportOpen: false, isImportOpen: false })}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs"
              >
                Cancel
              </button>
              <button
                onClick={handleImportSubmit}
                disabled={!importJsonText.trim() || isImporting}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-medium shadow-lg shadow-indigo-500/20 disabled:opacity-50"
              >
                {isImporting ? 'Importing...' : 'Restore Backup'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
