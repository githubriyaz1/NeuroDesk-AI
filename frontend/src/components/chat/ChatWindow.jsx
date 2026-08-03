import React, { useRef, useEffect } from 'react';
import {
  Sparkles,
  FileUp,
  FileDown,
  Trash2,
  Lightbulb,
} from 'lucide-react';
import { useChat } from '../../contexts/ChatContext';
import { ChatMessageItem } from './ChatMessageItem';
import { ChatInputBar } from './ChatInputBar';

export const ChatWindow = () => {
  const {
    activeConversation,
    messages,
    isLoadingMessages,
    isSending,
    sendMessage,
    clearMessages,
    setModalState,
  } = useChat();

  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    if (messagesEndRef.current && typeof messagesEndRef.current.scrollIntoView === 'function') {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isSending]);

  const samplePrompts = [
    'Write a Python script using pandas to clean and analyze financial datasets.',
    'Build a secure FastAPI router with JWT authentication and database dependencies.',
    'Explain how to optimize SQL queries in PostgreSQL and SQLite engines.',
    'Generate a modern React component using Tailwind CSS and glassmorphism styling.',
  ];

  return (
    <div className="flex-1 flex flex-col h-full bg-slate-950/80 overflow-hidden">
      {/* Active Conversation Header */}
      <div className="px-6 py-3.5 border-b border-slate-800/80 bg-slate-900/40 backdrop-blur-md flex items-center justify-between">
        <div className="min-w-0 pr-4">
          <h2 className="text-sm font-semibold text-slate-100 truncate">
            {activeConversation ? activeConversation.title : 'New AI Conversation'}
          </h2>
          <p className="text-[11px] text-slate-400 truncate">
            {activeConversation?.description || 'Provider Agnostic Enterprise AI Workspace'}
          </p>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-2">
          {activeConversation && (
            <>
              <button
                onClick={() => setModalState({ isExportOpen: true, isImportOpen: false })}
                className="px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-800/80 hover:bg-slate-700/80 text-slate-200 border border-slate-700/60 flex items-center gap-1.5 transition-all"
                title="Export conversation"
              >
                <FileDown className="w-3.5 h-3.5 text-blue-400" />
                <span className="hidden sm:inline">Export</span>
              </button>

              <button
                onClick={() => clearMessages(activeConversation.id)}
                className="p-1.5 rounded-lg text-slate-400 hover:text-red-400 hover:bg-slate-800/80 transition-colors"
                title="Clear messages"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </>
          )}

          <button
            onClick={() => setModalState({ isExportOpen: false, isImportOpen: true })}
            className="px-3 py-1.5 rounded-lg text-xs font-medium bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 border border-indigo-500/30 flex items-center gap-1.5 transition-all"
          >
            <FileUp className="w-3.5 h-3.5 text-indigo-400" />
            <span className="hidden sm:inline">Import</span>
          </button>
        </div>
      </div>

      {/* Message Feed Area */}
      <div className="flex-1 overflow-y-auto custom-scrollbar">
        {isLoadingMessages ? (
          <div className="flex flex-col items-center justify-center h-full gap-3 text-slate-400 text-sm">
            <div className="w-6 h-6 border-2 border-blue-500/30 border-t-blue-500 rounded-full animate-spin" />
            <p>Loading messages...</p>
          </div>
        ) : messages.length === 0 ? (
          /* Hero Empty State */
          <div className="max-w-2xl mx-auto py-16 px-6 text-center space-y-8 animate-in fade-in zoom-in-95 duration-200">
            <div className="w-16 h-16 rounded-3xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-purple-600 p-0.5 mx-auto shadow-xl shadow-indigo-500/20">
              <div className="w-full h-full bg-slate-900 rounded-[22px] flex items-center justify-center">
                <Sparkles className="w-8 h-8 text-blue-400" />
              </div>
            </div>

            <div className="space-y-2">
              <h1 className="text-2xl font-bold text-slate-100 tracking-tight">
                NeuroDesk AI Platform
              </h1>
              <p className="text-sm text-slate-400 max-w-md mx-auto">
                Provider-agnostic conversational intelligence engine ready to assist with code, analytics, and workflow automation.
              </p>
            </div>

            {/* Prompt Suggestion Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-left">
              {samplePrompts.map((prompt, idx) => (
                <button
                  key={idx}
                  onClick={() => sendMessage(prompt)}
                  className="p-3.5 rounded-2xl bg-slate-900/60 border border-slate-800 hover:border-blue-500/50 hover:bg-slate-800/60 text-slate-300 hover:text-slate-100 transition-all text-xs flex items-start gap-2.5 group shadow-sm"
                >
                  <Lightbulb className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5 group-hover:scale-110 transition-transform" />
                  <span className="leading-snug">{prompt}</span>
                </button>
              ))}
            </div>
          </div>
        ) : (
          /* Message List */
          <div className="divide-y divide-slate-800/40">
            {messages.map((msg) => (
              <ChatMessageItem key={msg.id} message={msg} />
            ))}
            {isSending && (
              <div className="py-4 px-6 flex gap-4 bg-slate-800/20">
                <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-purple-600 to-indigo-600 flex items-center justify-center text-white">
                  <Sparkles className="w-4 h-4 animate-spin" />
                </div>
                <div className="flex items-center gap-1.5 text-xs text-slate-400">
                  <span className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-bounce" />
                  <span className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-bounce [animation-delay:0.2s]" />
                  <span className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-bounce [animation-delay:0.4s]" />
                  <span className="ml-2 font-mono">Generating response via Mock Provider...</span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input Bar */}
      <ChatInputBar />
    </div>
  );
};
