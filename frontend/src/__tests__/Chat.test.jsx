import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { AIChatPage } from '../pages/AIChatPage';
import chatService from '../services/chatService';

vi.mock('../services/chatService', () => ({
  default: {
    listConversations: vi.fn(),
    createConversation: vi.fn(),
    getConversation: vi.fn(),
    sendMessage: vi.fn(),
    streamResponse: vi.fn(),
    getMessages: vi.fn(),
    pinConversation: vi.fn(),
    favoriteConversation: vi.fn(),
    archiveConversation: vi.fn(),
    duplicateConversation: vi.fn(),
    deleteConversation: vi.fn(),
    clearConversation: vi.fn(),
    exportConversation: vi.fn(),
    importConversation: vi.fn(),
  },
}));

describe('AIChatPage Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    chatService.listConversations.mockResolvedValue({
      items: [
        {
          id: 'conv-1',
          title: 'Existing Chat Session',
          description: 'Testing conversation list',
          message_count: 2,
          is_pinned: false,
          is_favorite: false,
          is_archived: false,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          last_message_at: new Date().toISOString(),
        },
      ],
      total: 1,
    });

    chatService.getConversation.mockResolvedValue({
      id: 'conv-1',
      title: 'Existing Chat Session',
      message_count: 2,
      messages: [
        {
          id: 'msg-1',
          role: 'user',
          content: 'Hello AI',
          created_at: new Date().toISOString(),
        },
        {
          id: 'msg-2',
          role: 'assistant',
          content: 'Hello User! How can I assist you?',
          created_at: new Date().toISOString(),
          token_usage: { total_tokens: 30 },
          latency_ms: 120,
        },
      ],
    });
  });

  it('renders AI Chat workspace with conversation sidebar', async () => {
    render(<AIChatPage />);

    expect(screen.getByText('New Conversation')).toBeDefined();
    await waitFor(() => {
      expect(screen.getByText('Existing Chat Session')).toBeDefined();
    });
  });

  it('allows user to type a prompt and send a message', async () => {
    chatService.streamResponse.mockImplementation(({ onChunk, onComplete }) => {
      onChunk({ content: 'Here is your response.', is_final: true });
      onComplete();
      return Promise.resolve();
    });

    render(<AIChatPage />);

    const input = screen.getByPlaceholderText('Ask NeuroDesk AI anything...');
    fireEvent.change(input, { target: { value: 'Can you analyze dataset X?' } });
    expect(input.value).toBe('Can you analyze dataset X?');

    const sendButton = input.nextElementSibling;
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(chatService.streamResponse).toHaveBeenCalledWith(
        expect.objectContaining({
          prompt: 'Can you analyze dataset X?',
        })
      );
    });
  });
});
