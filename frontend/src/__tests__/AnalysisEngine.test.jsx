import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import React from 'react';
import { SummaryCard } from '../components/analysis/SummaryCard';
import { InsightCards } from '../components/analysis/InsightCards';
import { StatisticsPanel } from '../components/analysis/StatisticsPanel';
import { ComparisonViewer } from '../components/analysis/ComparisonViewer';

describe('AI Data Analyst & Document Intelligence Components', () => {
  it('renders SummaryCard with executive summary and key highlights', () => {
    render(
      <SummaryCard
        summary="Executive Summary of Financial Report."
        keyPoints={['Revenue increased 20%', 'Margins expanded']}
        keywords={['Revenue', 'Financial']}
      />
    );
    expect(screen.getByText('Executive Summary of Financial Report.')).toBeDefined();
    expect(screen.getByText('Revenue increased 20%')).toBeDefined();
  });

  it('renders InsightCards grid with confidence badges', () => {
    const insights = [
      {
        category: 'recommendation',
        title: 'Strategic Growth',
        description: 'Expand digital marketing channels.',
        confidence_score: 0.92,
      },
    ];

    render(<InsightCards insights={insights} />);
    expect(screen.getByText('Strategic Growth')).toBeDefined();
    expect(screen.getByText('92%')).toBeDefined();
  });

  it('renders StatisticsPanel with row and column aggregates', () => {
    const datasetReport = {
      total_rows: 150,
      total_columns: 6,
      missing_values_count: 3,
      duplicate_rows_count: 0,
      columns_summary: [
        {
          column_name: 'Revenue',
          data_type: 'numeric',
          null_percentage: 2.0,
          unique_count: 140,
          mean: 5400.0,
          min_value: 100.0,
          max_value: 12000.0,
        },
      ],
    };

    render(<StatisticsPanel datasetReport={datasetReport} />);
    expect(screen.getByText('150')).toBeDefined();
    expect(screen.getByText('Revenue')).toBeDefined();
  });

  it('renders ComparisonViewer matrix with similarity score', () => {
    const report = {
      asset_a_name: 'Q2_Report.pdf',
      asset_b_name: 'Q3_Report.pdf',
      similarity_score: 0.85,
      change_summary: 'Identified 5 added sections.',
      added_information: ['Growth Forecast'],
      removed_information: ['Legacy Outlets'],
    };

    render(<ComparisonViewer comparisonReport={report} />);
    expect(screen.getByText('85% Similarity')).toBeDefined();
    expect(screen.getByText('+ Growth Forecast')).toBeDefined();
  });
});
