import React, { useState, useRef, useEffect } from 'react';
import {
  Send,
  Paperclip,
  X,
  Cpu,
  Square,
  Plus,
} from 'lucide-react';
import { useChat } from '../../contexts/ChatContext';
import AssetPickerModal from './AssetPickerModal';

export const ChatInputBar = () => {
  const {
    sendMessage,
    cancelActiveStream,
    isSending,
    selectedModel,
    setSelectedModel,
    attachedAssets,
    setAttachedAssets,
  } = useChat();
  const [promptText, setPromptText] = useState('');
  const [isAssetPickerOpen, setIsAssetPickerOpen] = useState(false);
  const textareaRef = useRef(null);

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleSend = () => {
    if (!promptText.trim() || isSending) return;
    sendMessage(promptText);
    setPromptText('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 180)}px`;
    }
  }, [promptText]);

  const handleSelectAsset = (asset) => {
    if (!attachedAssets.some((a) => a.id === asset.id)) {
      setAttachedAssets([...attachedAssets, { id: asset.id, filename: asset.name || asset.original_filename }]);
    }
  };

  return (
    <div className="p-4 bg-slate-900/80 border-t border-slate-800/80 backdrop-blur-lg">
      <div className="max-w-4xl mx-auto space-y-2">
        {/* Model Selection & Controls Bar */}
        <div className="flex items-center justify-between text-xs px-1 text-slate-400">
          <div className="flex items-center gap-2">
            <Cpu className="w-4 h-4 text-indigo-400" />
            <span className="font-medium text-slate-300">Engine:</span>
            <select
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              className="bg-slate-800 border border-slate-700/60 rounded-md px-2.5 py-1 text-xs text-slate-200 focus:outline-none focus:border-blue-500 cursor-pointer"
            >
              <option value="neurodesk-mock-v1">Mock LLM Engine (Offline)</option>
              <option value="gemini-1.5-pro">Gemini 1.5 Pro</option>
              <option value="gpt-4o">OpenAI GPT-4o</option>
              <option value="claude-3-5-sonnet">Claude 3.5 Sonnet</option>
            </select>

            <button
              onClick={() => setIsAssetPickerOpen(true)}
              className="flex items-center gap-1 px-2.5 py-1 rounded-md bg-blue-600/20 border border-blue-500/30 text-blue-300 hover:bg-blue-600/30 font-medium transition-colors"
            >
              <Paperclip className="w-3.5 h-3.5" />
              <span>Attach Asset</span>
            </button>
          </div>

          <span className="text-[11px] text-slate-400">
            Press <kbd className="bg-slate-800 px-1 rounded border border-slate-700">Enter</kbd> to send, <kbd className="bg-slate-800 px-1 rounded border border-slate-700">Shift+Enter</kbd> for newline
          </span>
        </div>

        {/* Attached Assets Chips */}
        {attachedAssets.length > 0 && (
          <div className="flex flex-wrap gap-2 py-1">
            {attachedAssets.map((asset) => (
              <div
                key={asset.id}
                className="flex items-center gap-1.5 bg-blue-600/20 border border-blue-500/30 text-blue-300 px-2.5 py-1 rounded-lg text-xs font-medium"
              >
                <Paperclip className="w-3.5 h-3.5" />
                <span className="truncate max-w-[150px]">{asset.filename || asset.name}</span>
                <button
                  onClick={() => setAttachedAssets((prev) => prev.filter((a) => a.id !== asset.id))}
                  className="hover:text-blue-100"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              </div>
            ))}
          </div>
        )}

        {/* Text Input Container */}
        <div className="relative flex items-end gap-2 bg-slate-800/90 border border-slate-700/70 rounded-2xl p-2 shadow-inner focus-within:border-blue-500/80 transition-colors">
          <textarea
            ref={textareaRef}
            value={promptText}
            onChange={(e) => setPromptText(e.target.value)}
            onKeyDown={handleKeyDown}
            rows={1}
            placeholder="Ask NeuroDesk AI anything..."
            className="flex-1 bg-transparent border-0 px-3 py-2 text-sm text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-0 resize-none max-h-44 custom-scrollbar"
          />

          {isSending ? (
            <button
              onClick={cancelActiveStream}
              title="Stop Generation"
              className="p-2.5 rounded-xl bg-red-600/80 hover:bg-red-500 text-white transition-all flex items-center justify-center shadow-lg shadow-red-500/25 active:scale-95"
            >
              <Square className="w-4 h-4 fill-white" />
            </button>
          ) : (
            <button
              onClick={handleSend}
              disabled={!promptText.trim()}
              className={`p-2.5 rounded-xl transition-all flex items-center justify-center ${
                promptText.trim()
                  ? 'bg-blue-600 hover:bg-blue-500 text-white shadow-lg shadow-blue-500/25 active:scale-95'
                  : 'bg-slate-700/50 text-slate-500 cursor-not-allowed'
              }`}
            >
              <Send className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      <AssetPickerModal
        isOpen={isAssetPickerOpen}
        onClose={() => setIsAssetPickerOpen(false)}
        onSelectAsset={handleSelectAsset}
        selectedAssets={attachedAssets}
      />
    </div>
  );
};
