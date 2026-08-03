import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import React from 'react';
import { CitationCard } from '../components/knowledge/CitationCard';
import { KnowledgePanel } from '../components/knowledge/KnowledgePanel';
import knowledgeService from '../services/knowledgeService';

vi.mock('../services/knowledgeService', () => ({
  default: {
    queryKnowledge: vi.fn().mockResolvedValue({ query: 'Q3', documents: [], citations: [] }),
    triggerIndexing: vi.fn().mockResolvedValue({ status: 'success' }),
    getDiagnostics: vi.fn().mockResolvedValue({
      status: 'healthy',
      indexed_assets_count: 5,
      average_retrieval_latency_ms: 12.5,
    }),
  },
  knowledgeService: {
    queryKnowledge: vi.fn().mockResolvedValue({ query: 'Q3', documents: [], citations: [] }),
    triggerIndexing: vi.fn().mockResolvedValue({ status: 'success' }),
    getDiagnostics: vi.fn().mockResolvedValue({
      status: 'healthy',
      indexed_assets_count: 5,
      average_retrieval_latency_ms: 12.5,
    }),
  },
}));

describe('Knowledge Engine Frontend Components', () => {
  it('renders CitationCard with source name and confidence score', () => {
    const citation = {
      asset_name: 'Financial_Q3_Report.pdf',
      source_type: 'pdf',
      confidence_score: 0.92,
      page_number: 2,
      snippet: 'Q3 Net Revenue grew 22% quarter over quarter.',
    };

    render(<CitationCard citation={citation} />);
    expect(screen.getByText('Financial_Q3_Report.pdf')).toBeDefined();
    expect(screen.getByText('92% Match')).toBeDefined();
  });

  it('renders KnowledgePanel drawer with diagnostics stats', async () => {
    render(<KnowledgePanel isOpen={true} onClose={() => {}} queryResult={{ citations: [] }} />);
    expect(screen.getByText('Knowledge Engine')).toBeDefined();

    await waitFor(() => {
      expect(screen.getByText('Indexed Assets')).toBeDefined();
      expect(screen.getByText('12.5ms')).toBeDefined();
    });
  });
});
