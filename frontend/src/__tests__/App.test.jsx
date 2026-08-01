import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import '@testing-library/jest-dom';
import React from 'react';
import App from '../App';

describe('NeuroDesk AI Frontend App', () => {
  it('renders application title without crashing', async () => {
    render(<App />);
    const headings = screen.getAllByText(/NeuroDesk AI/i);
    expect(headings.length).toBeGreaterThan(0);
    expect(headings[0]).toBeInTheDocument();
  });
});

