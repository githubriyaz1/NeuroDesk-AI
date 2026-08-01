import React, { useEffect, useState } from 'react';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { Modal } from '../components/common/Modal';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { EmptyState } from '../components/common/EmptyState';
import { Cpu, Plus, Play, CheckCircle2, Sliders } from 'lucide-react';
import { aiStudioService } from '../services/aiStudioService';

export const AIStudioPage = () => {
  const [models, setModels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [formData, setFormData] = useState({ name: '', model_type: 'Classification', framework: 'PyTorch' });
  const [submitting, setSubmitting] = useState(false);

  const fetchModels = async () => {
    try {
      setLoading(true);
      const data = await aiStudioService.getModels();
      setModels(data || []);
    } catch (err) {
      console.error('Failed to fetch AI Studio models:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchModels();
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      setSubmitting(true);
      await aiStudioService.createModel(formData);
      setIsModalOpen(false);
      setFormData({ name: '', model_type: 'Classification', framework: 'PyTorch' });
      await fetchModels();
    } catch (err) {
      console.error('Failed to register model in AI Studio:', err);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <LoadingSpinner label="Initializing AI Studio Machine Learning Models..." />;

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-zinc-100">AI Studio</h1>
          <p className="text-xs text-zinc-400 mt-1">Register, train, tune hyperparameters, and deploy machine learning models.</p>
        </div>
        <Button onClick={() => setIsModalOpen(true)}>
          <Plus size={16} className="mr-2" />
          Register New Model
        </Button>
      </div>

      {models.length === 0 ? (
        <EmptyState
          title="No Models in AI Studio"
          description="Create your first machine learning or LLM model pipeline."
          icon={Cpu}
          actionLabel="Register Model"
          onAction={() => setIsModalOpen(true)}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {models.map((model) => (
            <Card key={model.id} className="hover:border-zinc-700/80 transition-all">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2.5 rounded-lg bg-zinc-800 text-indigo-400 border border-zinc-700/50">
                    <Cpu size={20} />
                  </div>
                  <div>
                    <h3 className="text-sm font-semibold text-zinc-100">{model.name}</h3>
                    <span className="text-[11px] font-mono text-indigo-400">{model.framework}</span>
                  </div>
                </div>
                <Badge variant={model.status === 'deployed' ? 'success' : 'warning'}>{model.status}</Badge>
              </div>

              <div className="mt-4 grid grid-cols-2 gap-2 p-3 rounded-lg bg-zinc-950/60 border border-zinc-800/80 text-xs">
                <div>
                  <span className="text-[10px] uppercase font-mono text-zinc-500 block">Model Type</span>
                  <span className="font-medium text-zinc-200">{model.model_type}</span>
                </div>
                <div>
                  <span className="text-[10px] uppercase font-mono text-zinc-500 block">Accuracy Score</span>
                  <span className="font-semibold text-emerald-400">{(model.accuracy_score * 100).toFixed(1)}%</span>
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-zinc-800/80 flex items-center justify-between">
                <div className="flex items-center gap-1.5 text-[11px] text-zinc-400">
                  <Sliders size={14} className="text-zinc-500" />
                  <span>Hyperparameters Configured</span>
                </div>
                <Button variant="outline" size="sm">
                  <Play size={12} className="mr-1.5" /> Run Training
                </Button>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Register Model Modal */}
      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Register AI Studio Model">
        <form onSubmit={handleCreate} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-zinc-300 mb-1">Model Name</label>
            <input
              type="text"
              required
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="e.g. Demand Forecaster v2"
              className="w-full px-3 py-2 bg-zinc-950 border border-zinc-800 rounded-lg text-xs text-zinc-100 focus:outline-none focus:border-indigo-500"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-zinc-300 mb-1">Model Type</label>
            <select
              value={formData.model_type}
              onChange={(e) => setFormData({ ...formData, model_type: e.target.value })}
              className="w-full px-3 py-2 bg-zinc-950 border border-zinc-800 rounded-lg text-xs text-zinc-100 focus:outline-none focus:border-indigo-500"
            >
              <option value="Classification">Classification</option>
              <option value="Regression">Regression</option>
              <option value="Time Series Forecasting">Time Series Forecasting</option>
              <option value="Generative LLM">Generative LLM</option>
            </select>
          </div>
          <div>
            <label className="block text-xs font-medium text-zinc-300 mb-1">Framework</label>
            <input
              type="text"
              required
              value={formData.framework}
              onChange={(e) => setFormData({ ...formData, framework: e.target.value })}
              placeholder="e.g. PyTorch / XGBoost / HuggingFace"
              className="w-full px-3 py-2 bg-zinc-950 border border-zinc-800 rounded-lg text-xs text-zinc-100 focus:outline-none focus:border-indigo-500"
            />
          </div>
          <div className="flex justify-end gap-2 mt-6 pt-4 border-t border-zinc-800">
            <Button type="button" variant="outline" size="sm" onClick={() => setIsModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" size="sm" isLoading={submitting}>
              Register Model
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
