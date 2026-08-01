import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import '@testing-library/jest-dom';

import { PdfPreview } from '../components/preview/PdfPreview';
import { CsvPreview } from '../components/preview/CsvPreview';
import { ExcelPreview } from '../components/preview/ExcelPreview';
import { ImagePreview } from '../components/preview/ImagePreview';
import { UnsupportedPreview } from '../components/preview/UnsupportedPreview';

describe('Universal Preview Engine (UPE) Components', () => {
  it('renders PDF preview header and text extract', () => {
    const content = { title: 'Q3 Financial Analysis', author: 'NeuroDesk AI', page_count: 5, sample_text: 'Sample PDF Extract' };
    render(<PdfPreview content={content} metadata={{ file_size: 1048576 }} />);

    expect(screen.getByText('Q3 Financial Analysis')).toBeInTheDocument();
    expect(screen.getByText('5 Pages')).toBeInTheDocument();
    expect(screen.getByText('Sample PDF Extract')).toBeInTheDocument();
  });

  it('renders CSV preview table headers and row counts', () => {
    const content = {
      columns: ['id', 'name', 'salary'],
      rows: [{ id: '1', name: 'Alice', salary: '120000' }],
      column_count: 3,
      total_rows: 1,
    };
    render(<CsvPreview content={content} />);

    expect(screen.getByText('3 Columns')).toBeInTheDocument();
    expect(screen.getByText('Alice')).toBeInTheDocument();
  });

  it('renders Excel preview with sheet tabs', () => {
    const content = {
      sheet_names: ['Sheet1', 'Summary'],
      active_sheet: 'Sheet1',
      sheets: { Sheet1: { headers: ['Product', 'Price'], rows: [['Widget A', '$50']] } },
    };
    render(<ExcelPreview content={content} />);

    expect(screen.getByText('Sheet1')).toBeInTheDocument();
    expect(screen.getByText('Summary')).toBeInTheDocument();
    expect(screen.getByText('Widget A')).toBeInTheDocument();
  });

  it('renders Image preview dimensions and format controls', () => {
    const asset = { id: '11111111-1111-1111-1111-111111111111', name: 'Banner.png' };
    const content = { dimensions: { width: 1920, height: 1080 }, format: 'PNG' };
    render(<ImagePreview asset={asset} content={content} />);

    expect(screen.getByText('1920 × 1080 px')).toBeInTheDocument();
  });

  it('renders UnsupportedPreview graceful fallback screen', () => {
    const asset = { id: '11111111-1111-1111-1111-111111111111', extension: '.bin', file_size: 2048 };
    const content = { message: 'In-browser preview is currently unavailable for .bin files.' };
    const onDownload = vi.fn();
    render(<UnsupportedPreview asset={asset} content={content} onDownload={onDownload} />);

    expect(screen.getByText(/No Preview Available Screen/i)).toBeInTheDocument();
    expect(screen.getByText(/In-browser preview is currently unavailable for .bin files/i)).toBeInTheDocument();
  });
});
