import React, { createContext, useContext, useState, useEffect, useCallback, useRef } from 'react';
import chatService from '../services/chatService';

export const ChatContext = createContext();

export const ChatProvider = ({ children }) => {
  const [conversations, setConversations] = useState([]);
  const [activeConversation, setActiveConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isLoadingConversations, setIsLoadingConversations] = useState(false);
  const [isLoadingMessages, setIsLoadingMessages] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [activeStreamId, setActiveStreamId] = useState(null);
  const [activeMessageId, setActiveMessageId] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterMode, setFilterMode] = useState('all'); // 'all', 'pinned', 'favorites', 'archived'
  const [selectedModel, setSelectedModel] = useState('neurodesk-mock-v1');
  const [attachedAssets, setAttachedAssets] = useState([]);
  const [modalState, setModalState] = useState({ isExportOpen: false, isImportOpen: false });

  // Fetch list of conversations
  const loadConversations = useCallback(async () => {
    try {
      setIsLoadingConversations(true);
      const isArchived = filterMode === 'archived';
      const isFavorite = filterMode === 'favorites' ? true : undefined;
      const isPinned = filterMode === 'pinned' ? true : undefined;

      const data = await chatService.listConversations({
        is_archived: isArchived,
        is_favorite: isFavorite,
        is_pinned: isPinned,
        search: searchQuery || undefined,
      });
      setConversations(data.items || []);
    } catch (err) {
      console.error('Failed to load conversations:', err);
    } finally {
      setIsLoadingConversations(false);
    }
  }, [filterMode, searchQuery]);

  useEffect(() => {
    loadConversations();
  }, [loadConversations]);

  // Select conversation & fetch message history
  const selectConversation = useCallback(async (conversationId) => {
    if (!conversationId) {
      setActiveConversation(null);
      setMessages([]);
      return;
    }
    try {
      setIsLoadingMessages(true);
      const convData = await chatService.getConversation(conversationId);
      setActiveConversation(convData);
      setMessages(convData.messages || []);
    } catch (err) {
      console.error('Failed to fetch conversation details:', err);
    } finally {
      setIsLoadingMessages(false);
    }
  }, []);

  // Create new conversation
  const createNewConversation = useCallback(async (title = 'New Conversation') => {
    try {
      const newConv = await chatService.createConversation({
        title,
        settings_json: { model: selectedModel, temperature: 0.7, max_tokens: 4096 },
      });
      setConversations((prev) => [newConv, ...prev]);
      setActiveConversation(newConv);
      setMessages([]);
      return newConv;
    } catch (err) {
      console.error('Failed to create conversation:', err);
    }
  }, [selectedModel]);

  // Real-time Streaming Send Message
  const sendMessageStream = useCallback(async (promptText) => {
    if (!promptText || !promptText.trim() || isSending) return;

    try {
      setIsSending(true);
      let targetConvId = activeConversation?.id;
      const streamId = `stream-${Date.now()}`;
      setActiveStreamId(streamId);

      // 1. Optimistically append User Message
      const userMsgId = `temp-user-${Date.now()}`;
      const tempUserMsg = {
        id: userMsgId,
        role: 'user',
        content: promptText,
        created_at: new Date().toISOString(),
        message_status: 'completed',
      };

      // 2. Optimistically append Assistant Placeholder Message
      const assistantMsgId = `temp-assistant-${Date.now()}`;
      setActiveMessageId(assistantMsgId);
      const tempAssistantMsg = {
        id: assistantMsgId,
        role: 'assistant',
        content: '',
        created_at: new Date().toISOString(),
        message_status: 'streaming',
      };

      setMessages((prev) => [...prev, tempUserMsg, tempAssistantMsg]);

      // 3. Initiate SSE Streaming
      await chatService.streamResponse({
        conversation_id: targetConvId,
        prompt: promptText,
        stream_id: streamId,
        onChunk: (chunk) => {
          setMessages((prevMsgs) =>
            prevMsgs.map((m) =>
              m.id === assistantMsgId
                ? {
                    ...m,
                    content: m.content + chunk.content,
                    message_status: chunk.is_final ? 'completed' : 'streaming',
                  }
                : m
            )
          );
        },
        onError: (err) => {
          console.error('Streaming error:', err);
          setMessages((prevMsgs) =>
            prevMsgs.map((m) =>
              m.id === assistantMsgId
                ? { ...m, message_status: 'failed', content: m.content + ' [Stream interrupted]' }
                : m
            )
          );
        },
        onComplete: () => {
          setIsSending(false);
          setActiveStreamId(null);
          setActiveMessageId(null);
          loadConversations();
        },
      });

      setAttachedAssets([]);
    } catch (err) {
      console.error('Failed to send streaming message:', err);
      setIsSending(false);
      setActiveStreamId(null);
      setActiveMessageId(null);
    }
  }, [activeConversation, isSending, loadConversations]);

  // Cancel active stream
  const cancelActiveStream = useCallback(async () => {
    if (!activeStreamId || !activeMessageId) return;
    try {
      await chatService.cancelStream(activeMessageId, activeStreamId);
      setMessages((prev) =>
        prev.map((m) =>
          m.id === activeMessageId
            ? { ...m, message_status: 'cancelled', content: m.content + ' [Cancelled by user]' }
            : m
        )
      );
    } catch (err) {
      console.error('Failed to cancel stream:', err);
    } finally {
      setIsSending(false);
      setActiveStreamId(null);
      setActiveMessageId(null);
    }
  }, [activeStreamId, activeMessageId]);

  // Regenerate message
  const regenerateMessage = useCallback(async (messageId) => {
    try {
      setIsSending(true);
      const updatedMsg = await chatService.regenerateMessage(messageId);
      setMessages((prev) => prev.map((m) => (m.id === messageId ? updatedMsg : m)));
    } catch (err) {
      console.error('Failed to regenerate message:', err);
    } finally {
      setIsSending(false);
    }
  }, []);

  // Standard Send Message fallback
  const sendMessage = useCallback(async (promptText) => {
    return sendMessageStream(promptText);
  }, [sendMessageStream]);

  // Flag actions (Pin, Favorite, Archive)
  const togglePin = useCallback(async (id) => {
    try {
      const updated = await chatService.pinConversation(id);
      setConversations((prev) => prev.map((c) => (c.id === id ? updated : c)));
      if (activeConversation?.id === id) setActiveConversation(updated);
    } catch (err) {
      console.error('Failed to pin conversation:', err);
    }
  }, [activeConversation]);

  const toggleFavorite = useCallback(async (id) => {
    try {
      const updated = await chatService.favoriteConversation(id);
      setConversations((prev) => prev.map((c) => (c.id === id ? updated : c)));
      if (activeConversation?.id === id) setActiveConversation(updated);
    } catch (err) {
      console.error('Failed to favorite conversation:', err);
    }
  }, [activeConversation]);

  const archiveConversation = useCallback(async (id) => {
    try {
      const updated = await chatService.archiveConversation(id);
      loadConversations();
      if (activeConversation?.id === id) setActiveConversation(null);
    } catch (err) {
      console.error('Failed to archive conversation:', err);
    }
  }, [activeConversation, loadConversations]);

  const duplicateConversation = useCallback(async (id) => {
    try {
      const dup = await chatService.duplicateConversation(id);
      await loadConversations();
      selectConversation(dup.id);
    } catch (err) {
      console.error('Failed to duplicate conversation:', err);
    }
  }, [loadConversations, selectConversation]);

  const deleteConversation = useCallback(async (id) => {
    try {
      await chatService.deleteConversation(id);
      setConversations((prev) => prev.filter((c) => c.id !== id));
      if (activeConversation?.id === id) {
        setActiveConversation(null);
        setMessages([]);
      }
    } catch (err) {
      console.error('Failed to delete conversation:', err);
    }
  }, [activeConversation]);

  const clearMessages = useCallback(async (id) => {
    try {
      await chatService.clearConversation(id);
      if (activeConversation?.id === id) {
        setMessages([]);
      }
    } catch (err) {
      console.error('Failed to clear messages:', err);
    }
  }, [activeConversation]);

  return (
    <ChatContext.Provider
      value={{
        conversations,
        activeConversation,
        messages,
        isLoadingConversations,
        isLoadingMessages,
        isSending,
        activeStreamId,
        activeMessageId,
        searchQuery,
        setSearchQuery,
        filterMode,
        setFilterMode,
        selectedModel,
        setSelectedModel,
        attachedAssets,
        setAttachedAssets,
        modalState,
        setModalState,
        loadConversations,
        selectConversation,
        createNewConversation,
        sendMessage,
        sendMessageStream,
        cancelActiveStream,
        regenerateMessage,
        togglePin,
        toggleFavorite,
        archiveConversation,
        duplicateConversation,
        deleteConversation,
        clearMessages,
      }}
    >
      {children}
    </ChatContext.Provider>
  );
};

export const useChat = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
};
