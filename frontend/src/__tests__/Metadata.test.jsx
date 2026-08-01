import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import '@testing-library/jest-dom';
import { MetadataSection } from '../components/assets/MetadataSection';

// Mock metadataService API
vi.mock('../services/metadataService', () => ({
  metadataService: {
    getMetadata: vi.fn().mockResolvedValue({
      asset_id: 'test-asset-123',
      total_keys: 3,
      groups: [
        {
          category: 'Spreadsheet Format Metadata',
          items: [
            { key: 'row_count', value: '150', value_type: 'number', extracted_at: '2026-08-01T00:00:00Z' },
            { key: 'column_count', value: '10', value_type: 'number', extracted_at: '2026-08-01T00:00:00Z' },
          ],
        },
        {
          category: 'General File Attributes',
          items: [
            { key: 'mime_type', value: 'text/csv', value_type: 'string', extracted_at: '2026-08-01T00:00:00Z' },
          ],
        },
      ],
      items: [
        { key: 'row_count', value: '150', value_type: 'number', extracted_at: '2026-08-01T00:00:00Z' },
        { key: 'column_count', value: '10', value_type: 'number', extracted_at: '2026-08-01T00:00:00Z' },
        { key: 'mime_type', value: 'text/csv', value_type: 'string', extracted_at: '2026-08-01T00:00:00Z' },
      ],
    }),
    refreshMetadata: vi.fn().mockResolvedValue({
      asset_id: 'test-asset-123',
      total_keys: 3,
      groups: [],
      items: [],
    }),
  },
}));

describe('Sprint 3.4 Metadata Engine Frontend Component', () => {
  it('renders extracted metadata categories and key-value entries', async () => {
    render(<MetadataSection assetId="test-asset-123" />);

    await waitFor(() => {
      expect(screen.getByText(/Metadata Engine \(3 Keys\)/i)).toBeInTheDocument();
      expect(screen.getByText('Spreadsheet Format Metadata')).toBeInTheDocument();
      expect(screen.getByText('General File Attributes')).toBeInTheDocument();
      expect(screen.getByText('row_count:')).toBeInTheDocument();
      expect(screen.getByText('150')).toBeInTheDocument();
    });
  });
});
