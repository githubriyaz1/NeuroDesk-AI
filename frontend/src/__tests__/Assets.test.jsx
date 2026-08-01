import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { describe, it, expect, vi } from 'vitest';
import '@testing-library/jest-dom';
import { WorkspacePage } from '../pages/WorkspacePage';

// Mock assetService to prevent real network calls during Vitest execution
vi.mock('../services/assetService', () => ({
  assetService: {
    getAssets: vi.fn().mockResolvedValue({
      items: [
        {
          id: '11111111-1111-1111-1111-111111111111',
          name: 'Customer Churn Telemetry',
          original_filename: 'churn_v1.csv',
          asset_type: 'SPREADSHEET',
          mime_type: 'text/csv',
          extension: '.csv',
          file_size: 1048576,
          checksum: 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
          storage_provider: 'local',
          status: 'READY',
          version: 1,
          is_favorite: false,
          is_deleted: false,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
      ],
      total: 1,
      page: 1,
      page_size: 20,
      total_pages: 1,
    }),
    getStatistics: vi.fn().mockResolvedValue({
      total_assets: 1,
      total_storage_bytes: 1048576,
      favorite_count: 0,
      deleted_count: 0,
      assets_by_type: { SPREADSHEET: 1 },
      assets_by_status: { READY: 1 },
    }),
  },
}));

describe('DAMS Workspace Page & Asset Management', () => {
  it('renders DAMS Workspace header and statistics cards cleanly', async () => {
    render(
      <BrowserRouter>
        <WorkspacePage />
      </BrowserRouter>
    );

    expect(screen.getByText(/Digital Asset Management System/i)).toBeInTheDocument();
    expect(screen.getByText(/Upload Digital Asset/i)).toBeInTheDocument();
  });
});
