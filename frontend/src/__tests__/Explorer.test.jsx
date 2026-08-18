import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import '@testing-library/jest-dom';
import { ExplorerSidebar } from '../components/explorer/ExplorerSidebar';
import { ExplorerToolbar } from '../components/explorer/ExplorerToolbar';
import { AssetProvider } from '../contexts/AssetContext';

// Mock asset service API
vi.mock('../services/assetService', () => ({
  assetService: {
    getAssets: vi.fn().mockResolvedValue({
      items: [
        {
          id: 'asset-1',
          name: 'Test Dataset',
          original_filename: 'dataset.csv',
          asset_type: 'DATASET',
          mime_type: 'text/csv',
          extension: '.csv',
          file_size: 1024,
          status: 'READY',
          is_favorite: false,
          is_deleted: false,
          updated_at: '2026-08-01T00:00:00Z',
        },
      ],
      total: 1,
      total_pages: 1,
    }),
    getStatistics: vi.fn().mockResolvedValue({
      total_assets: 1,
      favorite_assets: 0,
      deleted_assets: 0,
      asset_count_by_type: { DATASET: 1 },
      assets_by_status: { READY: 1 },
    }),
  },
}));

describe('Sprint 3.3 Enterprise Asset Explorer Frontend Components', () => {
  it('renders ExplorerSidebar with category options', async () => {
    render(
      <AssetProvider>
        <ExplorerSidebar />
      </AssetProvider>
    );

    expect(screen.getByText('All Assets')).toBeInTheDocument();
    expect(screen.getByText('Recent')).toBeInTheDocument();
    expect(screen.getByText('Favorites')).toBeInTheDocument();
    expect(screen.getByText('Documents')).toBeInTheDocument();
    expect(screen.getByText('Images')).toBeInTheDocument();
    expect(screen.getByText('Datasets')).toBeInTheDocument();
    expect(screen.getByText('Archived')).toBeInTheDocument();
    expect(screen.getByText('Trash')).toBeInTheDocument();
  });

  it('renders ExplorerToolbar with search input and controls', async () => {
    render(
      <AssetProvider>
        <ExplorerToolbar />
      </AssetProvider>
    );

    expect(screen.getByPlaceholderText(/Search assets/i)).toBeInTheDocument();
    expect(screen.getByText('Upload Asset')).toBeInTheDocument();
  });
});
