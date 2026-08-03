import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import '@testing-library/jest-dom';
import { GlobalSearchBar } from '../components/search/GlobalSearchBar';
import { AdvancedFilterPanel } from '../components/search/AdvancedFilterPanel';
import { DiscoveryDashboard } from '../components/search/DiscoveryDashboard';
import { SavedViewsModal } from '../components/search/SavedViewsModal';

// Mock discoveryService
vi.mock('../services/discoveryService', () => ({
  discoveryService: {
    getRecent: vi.fn().mockResolvedValue([{ id: '1', name: 'Recent.pdf', asset_type: 'REPORT', file_size: 1024 }]),
    getFavorites: vi.fn().mockResolvedValue([{ id: '2', name: 'Fav.csv', asset_type: 'SPREADSHEET', file_size: 2048 }]),
    getLargest: vi.fn().mockResolvedValue([{ id: '3', name: 'Large.bin', asset_type: 'DATASET', file_size: 10485760 }]),
    getNewest: vi.fn().mockResolvedValue([{ id: '4', name: 'New.png', asset_type: 'IMAGE', file_size: 512 }]),
  },
}));

// Mock searchService
vi.mock('../services/searchService', () => ({
  searchService: {
    getSuggestions: vi.fn().mockResolvedValue({
      suggestions: [{ text: 'search_test.csv', type: 'filename' }],
    }),
  },
}));

describe('Sprint 3.5 Search & Discovery Platform Frontend Components', () => {
  it('renders GlobalSearchBar with Ctrl+K shortcut badge', () => {
    const setSearchQuery = vi.fn();
    render(<GlobalSearchBar searchQuery="" setSearchQuery={setSearchQuery} />);

    expect(screen.getByPlaceholderText(/Search assets/i)).toBeInTheDocument();
    expect(screen.getByText('Ctrl')).toBeInTheDocument();
    expect(screen.getByText('K')).toBeInTheDocument();
  });

  it('renders AdvancedFilterPanel with quick syntax chips', () => {
    const setSearchQuery = vi.fn();
    render(
      <AdvancedFilterPanel
        searchQuery=""
        setSearchQuery={setSearchQuery}
        onApply={vi.fn()}
      />
    );

    expect(screen.getByText(/PDF Documents/i)).toBeInTheDocument();
    expect(screen.getByText(/Spreadsheets/i)).toBeInTheDocument();
    expect(screen.getByText(/Favorites/i)).toBeInTheDocument();

    fireEvent.click(screen.getByText(/PDF Documents/i));
    expect(setSearchQuery).toHaveBeenCalledWith('type:pdf');
  });

  it('renders DiscoveryDashboard with curated smart collection sections', async () => {
    render(<DiscoveryDashboard />);

    await waitFor(() => {
      expect(screen.getByText('Recent Assets')).toBeInTheDocument();
      expect(screen.getByText('Favorites')).toBeInTheDocument();
      expect(screen.getByText('Largest Files')).toBeInTheDocument();
      expect(screen.getByText('Newest Assets')).toBeInTheDocument();
    });
  });

  it('renders SavedViewsModal and opens smoothly', () => {
    render(
      <SavedViewsModal
        isOpen={true}
        onClose={vi.fn()}
        currentQuery="type:pdf"
        onSelectQuery={vi.fn()}
      />
    );

    expect(screen.getByText('Saved Search Views')).toBeInTheDocument();
    expect(screen.getByText('type:pdf')).toBeInTheDocument();
  });
});
