import React, { useEffect, useState } from 'react';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { Modal } from '../components/common/Modal';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { EmptyState } from '../components/common/EmptyState';
import { GitFork, Plus, Play, Clock, Edit3 } from 'lucide-react';
import { workflowService } from '../services/workflowService';
import { WorkflowCanvas } from '../components/workflow/WorkflowCanvas';

export const WorkflowsPage = () => {
  const [workflows, setWorkflows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState('list'); // 'list' | 'canvas'
  const [activeWorkflowId, setActiveWorkflowId] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [formData, setFormData] = useState({ name: '', description: '' });
  const [submitting, setSubmitting] = useState(false);

  const fetchWorkflows = async () => {
    try {
      setLoading(true);
      const data = await workflowService.listWorkflows();
      setWorkflows(data || []);
    } catch (err) {
      console.error('Failed to fetch workflows:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWorkflows();
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      setSubmitting(true);
      const created = await workflowService.createWorkflow({
        name: formData.name,
        description: formData.description,
      });
      setIsModalOpen(false);
      setFormData({ name: '', description: '' });
      await fetchWorkflows();
      if (created?.id) {
        setActiveWorkflowId(created.id);
        setViewMode('canvas');
      }
    } catch (err) {
      console.error('Failed to create workflow:', err);
    } finally {
      setSubmitting(false);
    }
  };

  const handleExecuteQuick = async (e, wfId) => {
    e.stopPropagation();
    try {
      await workflowService.runWorkflow(wfId, { inputs: {} });
      await fetchWorkflows();
    } catch (err) {
      console.error('Failed to execute workflow:', err);
    }
  };

  if (viewMode === 'canvas') {
    return (
      <WorkflowCanvas
        workflowId={activeWorkflowId}
        onBack={() => {
          setActiveWorkflowId(null);
          setViewMode('list');
          fetchWorkflows();
        }}
      />
    );
  }

  if (loading) return <LoadingSpinner label="Loading Automation Workflows..." />;

  return (
    <div className="space-y-6 p-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-zinc-100">Automated Workflows</h1>
          <p className="text-xs text-zinc-400 mt-1">Orchestrate automated data ingestion, quality checks, and model evaluation triggers.</p>
        </div>
        <Button onClick={() => setIsModalOpen(true)}>
          <Plus size={16} className="mr-2" />
          Create Workflow
        </Button>
      </div>

      {workflows.length === 0 ? (
        <EmptyState
          title="No Workflows Defined"
          description="Build automated pipelines to process data and trigger models."
          icon={GitFork}
          actionLabel="Create Workflow"
          onAction={() => setIsModalOpen(true)}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {workflows.map((wf) => (
            <Card
              key={wf.id}
              onClick={() => {
                setActiveWorkflowId(wf.id);
                setViewMode('canvas');
              }}
              className="hover:border-indigo-500/50 cursor-pointer transition-all"
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2.5 rounded-lg bg-zinc-800 text-indigo-400 border border-zinc-700/50">
                    <GitFork size={20} />
                  </div>
                  <div>
                    <h3 className="text-sm font-semibold text-zinc-100">{wf.name}</h3>
                    <span className="text-[11px] font-mono text-zinc-500">
                      {wf.nodes?.length || 0} Pipeline Nodes • v{wf.version || 1}
                    </span>
                  </div>
                </div>
                <Badge variant={wf.status === 'ACTIVE' ? 'success' : 'neutral'}>
                  {wf.status || 'ACTIVE'}
                </Badge>
              </div>

              <p className="text-xs text-zinc-400 mt-3 leading-relaxed">{wf.description || 'Visual AI Workflow DAG Canvas'}</p>

              <div className="mt-4 pt-3 border-t border-zinc-800/80 flex items-center justify-between">
                <div className="flex items-center gap-1.5 text-[11px] font-mono text-zinc-500">
                  <Clock size={14} />
                  <span>Manual / Scheduled</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={(e) => {
                      e.stopPropagation();
                      setActiveWorkflowId(wf.id);
                      setViewMode('canvas');
                    }}
                  >
                    <Edit3 size={12} className="mr-1.5" /> Open Studio
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={(e) => handleExecuteQuick(e, wf.id)}
                  >
                    <Play size={12} className="mr-1.5" /> Execute
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Create Workflow Modal */}
      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Create Automation Workflow">
        <form onSubmit={handleCreate} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-zinc-300 mb-1">Workflow Name</label>
            <input
              type="text"
              required
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="e.g. S3 Telemetry Sync Pipeline"
              className="w-full px-3 py-2 bg-zinc-950 border border-zinc-800 rounded-lg text-xs text-zinc-100 focus:outline-none focus:border-indigo-500"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-zinc-300 mb-1">Description</label>
            <textarea
              rows={3}
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Summary of workflow trigger and action steps..."
              className="w-full px-3 py-2 bg-zinc-950 border border-zinc-800 rounded-lg text-xs text-zinc-100 focus:outline-none focus:border-indigo-500"
            />
          </div>
          <div className="flex justify-end gap-2 mt-6 pt-4 border-t border-zinc-800">
            <Button type="button" variant="outline" size="sm" onClick={() => setIsModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" size="sm" isLoading={submitting}>
              Save & Open Studio
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default WorkflowsPage;
