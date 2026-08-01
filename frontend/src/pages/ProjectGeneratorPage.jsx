import React, { useState } from 'react';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { Sparkles, Layers, Database, Network, ListChecks, Calendar, Info } from 'lucide-react';
import { generatorService } from '../services/generatorService';

export const ProjectGeneratorPage = () => {
  const [formData, setFormData] = useState({
    title: '',
    idea_description: '',
    target_stack: 'React + Python FastAPI + PostgreSQL',
  });
  const [loading, setLoading] = useState(false);
  const [blueprint, setBlueprint] = useState(null);
  const [activeTab, setActiveTab] = useState('architecture');

  const handleGenerate = async (e) => {
    e.preventDefault();
    if (!formData.title || !formData.idea_description) return;
    try {
      setLoading(true);
      const result = await generatorService.generateBlueprint(formData);
      setBlueprint(result);
    } catch (err) {
      console.error('Failed to generate project blueprint:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <div className="flex items-center gap-2">
          <h1 className="text-xl font-bold text-zinc-100">AI Project Generator</h1>
          <Badge variant="info">Architectural Planner</Badge>
        </div>
        <p className="text-xs text-zinc-400 mt-1">
          Describe your software application idea to generate a complete enterprise blueprint (Architecture, DB Design, API Plan, Feature Breakdown, and Development Roadmap).
        </p>
      </div>

      {/* Idea Description Form */}
      <Card title="Describe Software Concept">
        <form onSubmit={handleGenerate} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-zinc-300 mb-1">Project Name</label>
              <input
                type="text"
                required
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                placeholder="e.g. Distributed Telemetry Platform"
                className="w-full px-3 py-2 bg-zinc-950 border border-zinc-800 rounded-lg text-xs text-zinc-100 focus:outline-none focus:border-indigo-500"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-zinc-300 mb-1">Target Tech Stack</label>
              <input
                type="text"
                value={formData.target_stack}
                onChange={(e) => setFormData({ ...formData, target_stack: e.target.value })}
                placeholder="e.g. React + FastAPI + PostgreSQL"
                className="w-full px-3 py-2 bg-zinc-950 border border-zinc-800 rounded-lg text-xs text-zinc-100 focus:outline-none focus:border-indigo-500"
              />
            </div>
          </div>
          <div>
            <label className="block text-xs font-medium text-zinc-300 mb-1">Project Idea & Core Functional Requirements</label>
            <textarea
              rows={4}
              required
              value={formData.idea_description}
              onChange={(e) => setFormData({ ...formData, idea_description: e.target.value })}
              placeholder="Describe the application features, intended users, data flows, and scalability requirements..."
              className="w-full px-3 py-2 bg-zinc-950 border border-zinc-800 rounded-lg text-xs text-zinc-100 focus:outline-none focus:border-indigo-500 leading-relaxed"
            />
          </div>

          <div className="flex items-center justify-between pt-2">
            <div className="flex items-center gap-1.5 text-[11px] text-zinc-500">
              <Info size={14} className="text-zinc-400" />
              <span>Planning & Blueprint generation only. No raw source code generated.</span>
            </div>
            <Button type="submit" isLoading={loading}>
              <Sparkles size={14} className="mr-2" />
              Generate Architecture Blueprint
            </Button>
          </div>
        </form>
      </Card>

      {/* Generated Blueprint View */}
      {loading && <LoadingSpinner label="Analyzing requirements and crafting system architecture blueprint..." />}

      {blueprint && !loading && (
        <Card title={`Architectural Blueprint: ${blueprint.title}`}>
          {/* Navigation Tabs */}
          <div className="flex flex-wrap gap-2 mb-6 pb-3 border-b border-zinc-800">
            {[
              { id: 'architecture', label: 'Architecture', icon: Layers },
              { id: 'database', label: 'Database Design', icon: Database },
              { id: 'api', label: 'API Plan', icon: Network },
              { id: 'features', label: 'Feature Breakdown', icon: ListChecks },
              { id: 'roadmap', label: 'Roadmap', icon: Calendar },
            ].map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                    isActive
                      ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/40'
                      : 'text-zinc-400 hover:bg-zinc-800/60 hover:text-zinc-200'
                  }`}
                >
                  <Icon size={14} />
                  {tab.label}
                </button>
              );
            })}
          </div>

          {/* Tab Content */}
          <div className="space-y-4">
            {/* Architecture Tab */}
            {activeTab === 'architecture' && (
              <div className="space-y-4">
                <div className="p-4 rounded-xl bg-zinc-950/80 border border-zinc-800 text-xs leading-relaxed text-zinc-300">
                  <h4 className="text-sm font-semibold text-zinc-100 mb-2">System Overview</h4>
                  <p>{blueprint.architecture_overview}</p>
                </div>
              </div>
            )}

            {/* Database Design Tab */}
            {activeTab === 'database' && (
              <div className="space-y-4">
                <h4 className="text-xs font-mono text-indigo-400 uppercase">Engine: {blueprint.database_design.database_type}</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {blueprint.database_design.tables?.map((tbl, i) => (
                    <div key={i} className="p-4 rounded-xl bg-zinc-950/80 border border-zinc-800 space-y-3">
                      <div className="flex items-center gap-2 border-b border-zinc-800 pb-2">
                        <Database size={14} className="text-indigo-400" />
                        <span className="text-xs font-bold font-mono text-zinc-100">{tbl.table_name}</span>
                      </div>
                      <div className="space-y-1">
                        {tbl.columns.map((col, idx) => (
                          <div key={idx} className="flex justify-between text-[11px] font-mono text-zinc-400">
                            <span>{col.name}</span>
                            <span className="text-zinc-600">{col.type}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* API Plan Tab */}
            {activeTab === 'api' && (
              <div className="space-y-2">
                {blueprint.api_plan.endpoints?.map((ep, idx) => (
                  <div key={idx} className="flex items-center justify-between p-3 rounded-lg bg-zinc-950/80 border border-zinc-800/80 font-mono text-xs">
                    <div className="flex items-center gap-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${ep.method === 'GET' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-indigo-500/20 text-indigo-400'}`}>
                        {ep.method}
                      </span>
                      <span className="text-zinc-200">{ep.endpoint}</span>
                    </div>
                    <span className="text-zinc-500 text-[11px] font-sans">{ep.summary}</span>
                  </div>
                ))}
              </div>
            )}

            {/* Feature Breakdown Tab */}
            {activeTab === 'features' && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {blueprint.feature_breakdown?.map((mod, idx) => (
                  <div key={idx} className="p-4 rounded-xl bg-zinc-950/80 border border-zinc-800 space-y-3">
                    <div className="flex justify-between items-center">
                      <h4 className="text-xs font-bold text-zinc-100">{mod.module}</h4>
                      <Badge variant="info">{mod.complexity}</Badge>
                    </div>
                    <ul className="space-y-1.5 text-xs text-zinc-400">
                      {mod.features.map((feat, fIdx) => (
                        <li key={fIdx} className="flex items-center gap-2">
                          <span className="w-1.5 h-1.5 rounded-full bg-indigo-500" />
                          {feat}
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            )}

            {/* Roadmap Tab */}
            {activeTab === 'roadmap' && (
              <div className="space-y-3">
                {blueprint.roadmap?.map((rm, idx) => (
                  <div key={idx} className="flex items-center justify-between p-4 rounded-xl bg-zinc-950/80 border border-zinc-800">
                    <div className="flex items-center gap-4">
                      <span className="px-2.5 py-1 rounded bg-zinc-800 font-mono text-xs text-indigo-400 font-semibold">{rm.phase}</span>
                      <div>
                        <h4 className="text-xs font-semibold text-zinc-200">{rm.title}</h4>
                        <span className="text-[11px] text-zinc-500">Estimated Duration: {rm.duration}</span>
                      </div>
                    </div>
                    <Badge variant="neutral">{rm.status}</Badge>
                  </div>
                ))}
              </div>
            )}
          </div>
        </Card>
      )}
    </div>
  );
};
