import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import React from 'react';
import AIStudioDashboard from '../components/studio/AIStudioDashboard';
import TechnologySelector from '../components/studio/TechnologySelector';
import FolderTreeViewer from '../components/studio/FolderTreeViewer';
import APIViewer from '../components/studio/APIViewer';

// Mock generatorService
vi.mock('../services/generatorService', () => ({
  generatorService: {
    getBlueprints: vi.fn().mockResolvedValue([
      {
        id: 'bp-1',
        name: 'Mock Telemedicine Platform',
        description: 'Healthcare app',
        project_type: 'web_app',
        version: 1,
        blueprint_json: {
          requirements: { problem_statement: 'Health inefficiencies', objectives: ['Fast service'] },
          tech_stack: { recommended_primary: { frontend: 'React', backend: 'FastAPI' } },
          architecture: { pattern: '4-Tier Layered Pattern', layers: [] },
          database_schema: { tables: [] },
          api_contracts: { base_url: '/api/v1', endpoints: [] },
          folder_tree: { name: 'root', type: 'directory', children: [] },
          roadmap: { sprints: [] },
        },
      },
    ]),
    getStarterTemplates: vi.fn().mockResolvedValue([]),
    getMetrics: vi.fn().mockResolvedValue({ total_blueprints: 1, total_versions_snapshot: 1 }),
    generateBlueprint: vi.fn().mockResolvedValue({
      id: 'bp-2',
      name: 'New Blueprint',
      description: 'Test prompt',
      project_type: 'web_app',
      version: 1,
      blueprint_json: {},
    }),
  },
}));

describe('AI Studio & Project Generator Suite', () => {
  it('renders TechnologySelector and toggles technologies', () => {
    const onChange = vi.fn();
    render(<TechnologySelector selected={['React']} onChange={onChange} />);

    expect(screen.getByText('React')).toBeDefined();
    fireEvent.click(screen.getByText('FastAPI'));
    expect(onChange).toHaveBeenCalledWith(['React', 'FastAPI']);
  });

  it('renders FolderTreeViewer component', () => {
    const tree = {
      name: 'root',
      type: 'directory',
      children: [{ name: 'backend', type: 'directory', children: [{ name: 'main.py', type: 'file' }] }],
    };
    render(<FolderTreeViewer tree={tree} />);
    expect(screen.getByText('root')).toBeDefined();
    expect(screen.getByText('backend')).toBeDefined();
  });

  it('renders APIViewer component', () => {
    const apiContracts = {
      base_url: '/api/v1',
      endpoints: [{ method: 'GET', path: '/api/v1/projects', summary: 'List user projects', auth_required: true }],
    };
    render(<APIViewer apiContracts={apiContracts} />);
    expect(screen.getByText('/api/v1/projects')).toBeDefined();
    expect(screen.getByText('GET')).toBeDefined();
  });

  it('renders AIStudioDashboard correctly', async () => {
    render(<AIStudioDashboard />);
    await waitFor(() => {
      expect(screen.getByText('AI Studio')).toBeDefined();
    });
    expect(screen.getAllByText('Mock Telemedicine Platform').length).toBeGreaterThan(0);
  });
});
