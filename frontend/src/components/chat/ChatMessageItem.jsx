import React, { useState } from 'react';
import {
  User,
  Sparkles,
  Copy,
  Check,
  RotateCcw,
  AlertCircle,
  Loader2,
} from 'lucide-react';
import { useChat } from '../../contexts/ChatContext';

export const ChatMessageItem = ({ message }) => {
  const { regenerateMessage } = useChat();
  const [copied, setCopied] = useState(false);

  const isUser = message.role === 'user';
  const isError = message.role === 'error';
  const isStreaming = message.message_status === 'streaming';
  const isCancelled = message.message_status === 'cancelled';
  const isFailed = message.message_status === 'failed';

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div
      className={`py-4 px-6 flex gap-4 transition-colors ${
        isUser
          ? 'bg-slate-900/40'
          : 'bg-slate-800/30 border-y border-slate-800/60'
      }`}
    >
      {/* Role Avatar */}
      <div className="flex-shrink-0">
        {isUser ? (
          <div className="w-8 h-8 rounded-xl bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400 font-semibold shadow-sm">
            <User className="w-4 h-4" />
          </div>
        ) : (
          <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-purple-600 to-indigo-600 flex items-center justify-center text-white font-semibold shadow-md shadow-indigo-500/20">
            <Sparkles className="w-4 h-4" />
          </div>
        )}
      </div>

      {/* Message Body */}
      <div className="flex-1 min-w-0 space-y-2">
        {/* Header line */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-sm font-semibold text-slate-200">
              {isUser ? 'You' : 'NeuroDesk Assistant'}
            </span>
            <span className="text-[11px] text-slate-400">
              {new Date(message.created_at).toLocaleTimeString([], {
                hour: '2-digit',
                minute: '2-digit',
              })}
            </span>

            {/* Status Badges */}
            {isStreaming && (
              <span className="flex items-center gap-1 text-[10px] bg-blue-500/20 border border-blue-400/30 text-blue-300 px-2 py-0.5 rounded-full font-medium animate-pulse">
                <Loader2 className="w-3 h-3 animate-spin" /> Streaming
              </span>
            )}
            {isCancelled && (
              <span className="text-[10px] bg-amber-500/20 border border-amber-400/30 text-amber-300 px-2 py-0.5 rounded-full font-medium">
                Cancelled
              </span>
            )}
            {isFailed && (
              <span className="text-[10px] bg-red-500/20 border border-red-400/30 text-red-300 px-2 py-0.5 rounded-full font-medium">
                Failed
              </span>
            )}
          </div>

          {/* Action buttons */}
          <div className="flex items-center gap-1 opacity-80 hover:opacity-100 transition-opacity">
            {!isUser && (
              <button
                onClick={() => regenerateMessage(message.id)}
                className="p-1 text-slate-400 hover:text-slate-200 rounded-md hover:bg-slate-700/50"
                title="Regenerate response"
              >
                <RotateCcw className="w-3.5 h-3.5" />
              </button>
            )}
            <button
              onClick={handleCopy}
              className="p-1 text-slate-400 hover:text-slate-200 rounded-md hover:bg-slate-700/50"
              title="Copy response"
            >
              {copied ? (
                <Check className="w-4 h-4 text-emerald-400" />
              ) : (
                <Copy className="w-4 h-4" />
              )}
            </button>
          </div>
        </div>

        {/* Content */}
        <div
          className={`text-sm leading-relaxed ${
            isError ? 'text-red-400 font-medium' : 'text-slate-200'
          }`}
        >
          <p className="whitespace-pre-wrap font-sans">
            {message.content}
            {isStreaming && (
              <span className="inline-block w-2 h-4 ml-1 bg-blue-400 animate-pulse align-middle" />
            )}
          </p>
        </div>

        {/* Metadata chip (Tokens & Latency) */}
        {!isUser && message.token_usage && (
          <div className="pt-2 flex items-center gap-3 text-[11px] text-slate-400 border-t border-slate-800/40">
            <span className="bg-slate-800/80 px-2 py-0.5 rounded-md border border-slate-700/50 font-mono">
              Tokens: {message.token_usage.total_tokens || 0}
            </span>
            {message.latency_ms > 0 && (
              <span className="bg-slate-800/80 px-2 py-0.5 rounded-md border border-slate-700/50 font-mono">
                Latency: {message.latency_ms}ms
              </span>
            )}
            <span className="text-slate-400">Mock Provider v1</span>
          </div>
        )}
      </div>
    </div>
  );
};
