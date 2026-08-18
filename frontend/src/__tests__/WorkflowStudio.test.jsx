import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import React from 'react';
import { WorkflowNode } from '../components/workflow/WorkflowNode';
import { WorkflowEdge } from '../components/workflow/WorkflowEdge';
import { WorkflowToolbar } from '../components/workflow/WorkflowToolbar';
import { WorkflowSidebar } from '../components/workflow/WorkflowSidebar';
import { NodePropertiesPanel } from '../components/workflow/NodePropertiesPanel';
import { ExecutionConsole } from '../components/workflow/ExecutionConsole';
import { ExecutionHistoryPanel } from '../components/workflow/ExecutionHistoryPanel';
import { WorkflowCanvas } from '../components/workflow/WorkflowCanvas';
import { workflowService } from '../services/workflowService';

vi.mock('../services/workflowService', () => ({
  workflowService: {
    listWorkflows: vi.fn().mockResolvedValue([]),
    getWorkflow: vi.fn().mockResolvedValue({ id: 'wf-1', name: 'Test Workflow', nodes: [], edges: [] }),
    createWorkflow: vi.fn().mockResolvedValue({ id: 'wf-1', name: 'New AI Workflow' }),
    updateWorkflow: vi.fn().mockResolvedValue({ id: 'wf-1' }),
    runWorkflow: vi.fn().mockResolvedValue({
      id: 'exec-1',
      status: 'SUCCESS',
      total_latency_ms: 45.2,
      trigger_source: 'manual',
      outputs: { message: 'Completed' },
      nodes: [
        { node_id: 'n1', node_type: 'start', status: 'SUCCESS', latency_ms: 1.2 },
        { node_id: 'n2', node_type: 'end', status: 'SUCCESS', latency_ms: 0.8 },
      ],
      logs: [{ timestamp: '2026-08-02T00:00:00Z', log_level: 'INFO', message: 'Workflow DAG finished' }],
    }),
    getStarterTemplates: vi.fn().mockResolvedValue([
      { id: 't1', name: 'RAG Audit Pipeline', category: 'Knowledge', nodes: [], edges: [] },
    ]),
    getMetrics: vi.fn().mockResolvedValue({ total_workflows: 5, total_executions: 12 }),
  },
}));

describe('AI Workflow Automation Studio Frontend Components', () => {
  it('renders WorkflowNode with status badges and port anchors', () => {
    const node = {
      id: 'llm_1',
      type: 'llm_prompt',
      label: 'Summarize Document',
      position: { x: 100, y: 100 },
      data: { prompt: 'Summarize input: {input}' },
    };

    render(
      <WorkflowNode
        node={node}
        isSelected={true}
        executionState={{ status: 'SUCCESS', latency_ms: 12.5 }}
        onSelect={() => {}}
        onDelete={() => {}}
        onConfigure={() => {}}
        onStartConnect={() => {}}
        onEndConnect={() => {}}
      />
    );

    expect(screen.getByText('Summarize Document')).toBeDefined();
    expect(screen.getByText('Type:')).toBeDefined();
    expect(screen.getByText('12.5 ms')).toBeDefined();
  });

  it('renders WorkflowToolbar with status controls and run button', () => {
    render(
      <WorkflowToolbar
        workflow={{ name: 'Financial Audit Workflow', version: 2, status: 'ACTIVE' }}
        isValid={true}
        validationErrors={[]}
        isRunning={false}
        templates={[{ id: 't1', name: 'RAG Audit', category: 'Knowledge' }]}
        onRun={() => {}}
        onSave={() => {}}
        onLoadTemplate={() => {}}
        onDuplicate={() => {}}
        onToggleConsole={() => {}}
        onToggleHistory={() => {}}
        onToggleMiniMap={() => {}}
        showConsole={false}
        showHistory={false}
        showMiniMap={true}
      />
    );

    expect(screen.getByText('Financial Audit Workflow')).toBeDefined();
    expect(screen.getByText('Valid DAG')).toBeDefined();
    expect(screen.getByText('Run Execution')).toBeDefined();
  });

  it('renders WorkflowSidebar catalog categories', () => {
    render(<WorkflowSidebar onAddNode={() => {}} />);
    expect(screen.getByText('AI Node Palette')).toBeDefined();
    expect(screen.getByText('Triggers & Flow')).toBeDefined();
    expect(screen.getByText('AI & Knowledge')).toBeDefined();
    expect(screen.getByText('Data & Analytics')).toBeDefined();
  });

  it('renders NodePropertiesPanel drawer and handles property update', () => {
    const node = {
      id: 'llm_1',
      type: 'llm_prompt',
      label: 'LLM Step',
      data: { prompt: 'Test Prompt' },
    };

    const handleUpdate = vi.fn();

    render(
      <NodePropertiesPanel
        node={node}
        onUpdateNode={handleUpdate}
        onClose={() => {}}
      />
    );

    expect(screen.getByText('Node Properties')).toBeDefined();
    expect(screen.getByText('Prompt Template')).toBeDefined();

    const saveBtn = screen.getByText('Apply Changes');
    fireEvent.click(saveBtn);
    expect(handleUpdate).toHaveBeenCalledWith('llm_1', expect.objectContaining({ label: 'LLM Step' }));
  });

  it('renders ExecutionConsole trace tabs and output details', () => {
    const execution = {
      id: 'exec-100',
      status: 'SUCCESS',
      total_latency_ms: 32.1,
      trigger_source: 'manual',
      outputs: { final_result: 'Passed' },
      nodes: [{ id: 'n1', node_id: 'start_1', node_type: 'start', status: 'SUCCESS', latency_ms: 2.1 }],
      logs: [{ timestamp: '2026-08-02T00:00:00Z', log_level: 'INFO', message: 'Compilation complete' }],
    };

    render(<ExecutionConsole execution={execution} onClose={() => {}} />);
    expect(screen.getByText('Execution Console')).toBeDefined();
    expect(screen.getByText('32.1 ms')).toBeDefined();
  });

  it('renders ExecutionHistoryPanel drawer with status list', () => {
    const executions = [
      { id: 'exec-1', status: 'SUCCESS', total_latency_ms: 22.4, created_at: '2026-08-02T00:00:00Z' },
      { id: 'exec-2', status: 'FAILED', total_latency_ms: 10.1, created_at: '2026-08-02T00:01:00Z' },
    ];

    render(
      <ExecutionHistoryPanel
        executions={executions}
        onSelectExecution={() => {}}
        onClose={() => {}}
      />
    );

    expect(screen.getByText('Execution History')).toBeDefined();
    expect(screen.getByText('22.4 ms')).toBeDefined();
    expect(screen.getByText('10.1 ms')).toBeDefined();
  });

  it('renders WorkflowCanvas studio application', async () => {
    render(<WorkflowCanvas />);
    expect(screen.getByText('New AI Workflow')).toBeDefined();
    expect(screen.getAllByText('Start Entry').length).toBeGreaterThan(0);
    expect(screen.getAllByText('LLM Prompt').length).toBeGreaterThan(0);
    expect(screen.getAllByText('End Output').length).toBeGreaterThan(0);
  });
});
