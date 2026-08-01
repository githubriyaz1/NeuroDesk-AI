import React, { useEffect, useState } from 'react';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { Modal } from '../components/common/Modal';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { EmptyState } from '../components/common/EmptyState';
import { GitFork, Plus, Play, CheckCircle2, Clock } from 'lucide-react';
import { workflowService } from '../services/workflowService';

export const WorkflowsPage = () => {
  const [workflows, setWorkflows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [formData, setFormData] = useState({ name: '', description: '' });
  const [submitting, setSubmitting] = useState(false);

  const fetchWorkflows = async () => {
    try {
      setLoading(true);
      const data = await workflowService.getWorkflows();
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
      await workflowService.createWorkflow({
        name: formData.name,
        description: formData.description,
        definition: { trigger: 'manual', steps: [] },
      });
      setIsModalOpen(false);
      setFormData({ name: '', description: '' });
      await fetchWorkflows();
    } catch (err) {
      console.error('Failed to create workflow:', err);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <LoadingSpinner label="Loading Automation Workflows..." />;

  return (
    <div className="space-y-6">
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
            <Card key={wf.id} className="hover:border-zinc-700/80 transition-all">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2.5 rounded-lg bg-zinc-800 text-indigo-400 border border-zinc-700/50">
                    <GitFork size={20} />
                  </div>
                  <div>
                    <h3 className="text-sm font-semibold text-zinc-100">{wf.name}</h3>
                    <span className="text-[11px] font-mono text-zinc-500">
                      {wf.definition?.steps?.length || 3} Pipeline Steps
                    </span>
                  </div>
                </div>
                <Badge variant={wf.is_enabled ? 'success' : 'neutral'}>
                  {wf.is_enabled ? 'Active' : 'Disabled'}
                </Badge>
              </div>

              <p className="text-xs text-zinc-400 mt-3 leading-relaxed">{wf.description}</p>

              <div className="mt-4 pt-3 border-t border-zinc-800/80 flex items-center justify-between">
                <div className="flex items-center gap-1.5 text-[11px] font-mono text-zinc-500">
                  <Clock size={14} />
                  <span>Scheduled Nightly</span>
                </div>
                <Button variant="outline" size="sm">
                  <Play size={12} className="mr-1.5" /> Execute Now
                </Button>
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
              Save Workflow
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
