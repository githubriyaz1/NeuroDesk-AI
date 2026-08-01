import React, { useEffect, useState, useRef } from 'react';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { MessageSquareText, Send, Bot, User, Sparkles } from 'lucide-react';
import { chatService } from '../services/chatService';

export const AIChatPage = () => {
  const [session, setSession] = useState(null);
  const [prompt, setPrompt] = useState('');
  const [sending, setSending] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    const initChat = async () => {
      try {
        const data = await chatService.getSession();
        setSession(data);
      } catch (err) {
        console.error('Failed to initialize AI Chat:', err);
      }
    };
    initChat();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [session?.messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!prompt.trim() || sending) return;
    try {
      setSending(true);
      const userMessage = prompt;
      setPrompt('');
      const updatedSession = await chatService.sendPrompt(userMessage, session?.id);
      setSession(updatedSession);
    } catch (err) {
      console.error('Failed to send prompt:', err);
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="h-[calc(100vh-140px)] flex flex-col space-y-4">
      <div>
        <h1 className="text-xl font-bold text-zinc-100">AI Assistant Chat</h1>
        <p className="text-xs text-zinc-400 mt-1">Chat with NeuroDesk AI to query datasets, analyze models, or issue workspace commands.</p>
      </div>

      <div className="flex-1 bg-zinc-900/80 border border-zinc-800 rounded-xl shadow-glass flex flex-col overflow-hidden">
        {/* Chat History Messages */}
        <div className="flex-1 p-6 overflow-y-auto space-y-4">
          {session?.messages?.map((msg, idx) => (
            <div
              key={idx}
              className={`flex gap-3 max-w-3xl ${msg.role === 'user' ? 'ml-auto flex-row-reverse' : ''}`}
            >
              <div
                className={`w-8 h-8 rounded-lg flex items-center justify-center text-xs shrink-0 ${
                  msg.role === 'user'
                    ? 'bg-indigo-600/20 text-indigo-400 border border-indigo-500/30'
                    : 'bg-zinc-800 text-emerald-400 border border-zinc-700/60'
                }`}
              >
                {msg.role === 'user' ? <User size={16} /> : <Bot size={16} />}
              </div>
              <div
                className={`p-4 rounded-2xl text-xs leading-relaxed ${
                  msg.role === 'user'
                    ? 'bg-indigo-600 text-white rounded-tr-none'
                    : 'bg-zinc-950/80 border border-zinc-800 text-zinc-200 rounded-tl-none'
                }`}
              >
                {msg.content}
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Bar */}
        <form onSubmit={handleSend} className="p-4 border-t border-zinc-800/80 bg-zinc-950 flex gap-3">
          <input
            type="text"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Ask NeuroDesk AI about datasets, models, or system architecture..."
            className="flex-1 px-4 py-2.5 bg-zinc-900 border border-zinc-800 rounded-xl text-xs text-zinc-100 focus:outline-none focus:border-indigo-500"
          />
          <Button type="submit" isLoading={sending} disabled={!prompt.trim()}>
            <Send size={14} className="mr-1.5" /> Send
          </Button>
        </form>
      </div>
    </div>
  );
};
