import React from 'react';
import { ChatProvider } from '../contexts/ChatContext';
import { ConversationSidebar } from '../components/chat/ConversationSidebar';
import { ChatWindow } from '../components/chat/ChatWindow';
import { ImportExportModal } from '../components/chat/ImportExportModal';

export const AIChatPage = () => {
  return (
    <ChatProvider>
      <div className="h-[calc(100vh-80px)] flex bg-slate-950 text-slate-100 overflow-hidden rounded-2xl border border-slate-800/80 shadow-2xl">
        <ConversationSidebar />
        <ChatWindow />
        <ImportExportModal />
      </div>
    </ChatProvider>
  );
};

export default AIChatPage;
