import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import React from 'react';
import { ChatProvider, useChat } from '../contexts/ChatContext';
import { chatService } from '../services/chatService';

vi.mock('../services/chatService', () => ({
  default: {
    listConversations: vi.fn().mockResolvedValue({ items: [] }),
    createConversation: vi.fn().mockResolvedValue({ id: 'conv-1', title: 'New Conversation' }),
    getConversation: vi.fn().mockResolvedValue({ id: 'conv-1', title: 'New Conversation', messages: [] }),
    sendMessage: vi.fn().mockResolvedValue({ id: 'msg-1', role: 'assistant', content: 'Mock response' }),
    streamResponse: vi.fn().mockImplementation(({ onChunk, onComplete }) => {
      onChunk({ content: 'Hello ', is_final: false });
      onChunk({ content: 'world!', is_final: true });
      onComplete();
      return Promise.resolve();
    }),
    cancelStream: vi.fn().mockResolvedValue({ message: 'Cancelled' }),
    regenerateMessage: vi.fn().mockResolvedValue({ id: 'msg-1', content: 'Regenerated content' }),
    getDiagnostics: vi.fn().mockResolvedValue({ status: 'healthy' }),
  },
  chatService: {
    listConversations: vi.fn().mockResolvedValue({ items: [] }),
    createConversation: vi.fn().mockResolvedValue({ id: 'conv-1', title: 'New Conversation' }),
    getConversation: vi.fn().mockResolvedValue({ id: 'conv-1', title: 'New Conversation', messages: [] }),
    sendMessage: vi.fn().mockResolvedValue({ id: 'msg-1', role: 'assistant', content: 'Mock response' }),
    streamResponse: vi.fn().mockImplementation(({ onChunk, onComplete }) => {
      onChunk({ content: 'Hello ', is_final: false });
      onChunk({ content: 'world!', is_final: true });
      onComplete();
      return Promise.resolve();
    }),
    cancelStream: vi.fn().mockResolvedValue({ message: 'Cancelled' }),
    regenerateMessage: vi.fn().mockResolvedValue({ id: 'msg-1', content: 'Regenerated content' }),
    getDiagnostics: vi.fn().mockResolvedValue({ status: 'healthy' }),
  },
}));

const TestComponent = () => {
  const { messages, sendMessageStream, cancelActiveStream, isSending } = useChat();

  return (
    <div>
      <button onClick={() => sendMessageStream('Test prompt')}>Send Stream</button>
      <button onClick={cancelActiveStream}>Cancel Stream</button>
      <div data-testid="sending-status">{isSending ? 'Sending' : 'Idle'}</div>
      <div data-testid="message-list">
        {messages.map((m) => (
          <div key={m.id} data-testid={`msg-${m.role}`}>
            {m.content}
          </div>
        ))}
      </div>
    </div>
  );
};

describe('Sprint 4.3 Streaming & Memory Frontend Components', () => {
  it('streams response chunks into message list', async () => {
    render(
      <ChatProvider>
        <TestComponent />
      </ChatProvider>
    );

    const btn = screen.getByText('Send Stream');
    fireEvent.click(btn);

    await waitFor(() => {
      expect(screen.getByTestId('msg-user').textContent).toContain('Test prompt');
      expect(screen.getByTestId('msg-assistant').textContent).toContain('Hello world!');
    });
  });
});
