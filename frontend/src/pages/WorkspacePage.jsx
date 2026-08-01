import React, { useEffect, useState } from 'react';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { Modal } from '../components/common/Modal';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { EmptyState } from '../components/common/EmptyState';
import { FolderKanban, Plus, FileText, Database, HardDrive, Trash2 } from 'lucide-react';
import { workspaceService } from '../services/workspaceService';
import { formatBytes, formatDate } from '../utils/formatters';

export const WorkspacePage = () => {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [formData, setFormData] = useState({ name: '', description: '', file_type: 'csv' });
  const [submitting, setSubmitting] = useState(false);

  const fetchItems = async () => {
    try {
      setLoading(true);
      const data = await workspaceService.getWorkspaceItems();
      setItems(data || []);
    } catch (err) {
      console.error('Failed to fetch workspace items:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchItems();
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      setSubmitting(true);
      await workspaceService.createWorkspaceItem(formData);
      setIsModalOpen(false);
      setFormData({ name: '', description: '', file_type: 'csv' });
      await fetchItems();
    } catch (err) {
      console.error('Failed to create workspace item:', err);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <LoadingSpinner label="Loading Workspace Assets..." />;

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-zinc-100">Workspace Management</h1>
          <p className="text-xs text-zinc-400 mt-1">Upload and manage datasets, document stores, and vector embeddings.</p>
        </div>
        <Button onClick={() => setIsModalOpen(true)}>
          <Plus size={16} className="mr-2" />
          Add Dataset / Document
        </Button>
      </div>

      {items.length === 0 ? (
        <EmptyState
          title="No items in Workspace"
          description="Upload structured CSV datasets or document stores to begin data analysis."
          icon={FolderKanban}
          actionLabel="Add First Dataset"
          onAction={() => setIsModalOpen(true)}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {items.map((item) => (
            <Card key={item.id} className="hover:border-zinc-700/80 transition-all">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2.5 rounded-lg bg-zinc-800 text-indigo-400 border border-zinc-700/50">
                    {item.file_type === 'pdf' ? <FileText size={20} /> : <Database size={20} />}
                  </div>
                  <div>
                    <h3 className="text-sm font-semibold text-zinc-100">{item.name}</h3>
                    <span className="text-[11px] font-mono text-zinc-500 uppercase">{item.file_type}</span>
                  </div>
                </div>
                <Badge variant="success">{item.status}</Badge>
              </div>

              <p className="text-xs text-zinc-400 mt-3 leading-relaxed">{item.description}</p>

              <div className="mt-4 pt-3 border-t border-zinc-800/80 flex items-center justify-between text-[11px] font-mono text-zinc-500">
                <span>Size: {formatBytes(item.file_size_bytes)}</span>
                <span>Created: {formatDate(item.created_at)}</span>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Add Workspace Item Modal */}
      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Upload Dataset or Document">
        <form onSubmit={handleCreate} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-zinc-300 mb-1">Name</label>
            <input
              type="text"
              required
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="e.g. Sales Q3 Telemetry"
              className="w-full px-3 py-2 bg-zinc-950 border border-zinc-800 rounded-lg text-xs text-zinc-100 focus:outline-none focus:border-indigo-500"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-zinc-300 mb-1">Description</label>
            <textarea
              rows={3}
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Brief summary of dataset schema or document contents..."
              className="w-full px-3 py-2 bg-zinc-950 border border-zinc-800 rounded-lg text-xs text-zinc-100 focus:outline-none focus:border-indigo-500"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-zinc-300 mb-1">Resource Type</label>
            <select
              value={formData.file_type}
              onChange={(e) => setFormData({ ...formData, file_type: e.target.value })}
              className="w-full px-3 py-2 bg-zinc-950 border border-zinc-800 rounded-lg text-xs text-zinc-100 focus:outline-none focus:border-indigo-500"
            >
              <option value="csv">Structured CSV Dataset</option>
              <option value="json">JSON Telemetry Stream</option>
              <option value="pdf">PDF Document Store</option>
              <option value="parquet">Apache Parquet Table</option>
            </select>
          </div>
          <div className="flex justify-end gap-2 mt-6 pt-4 border-t border-zinc-800">
            <Button type="button" variant="outline" size="sm" onClick={() => setIsModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" size="sm" isLoading={submitting}>
              Create Entry
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
