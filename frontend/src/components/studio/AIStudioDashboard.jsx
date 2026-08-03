import React, { useState, useEffect } from 'react';
import { Wand2, Plus, Sparkles, Folder, BarChart2, Layers } from 'lucide-react';
import ProjectGeneratorWizard from './ProjectGeneratorWizard';
import BlueprintViewer from './BlueprintViewer';
import { generatorService } from '../../services/generatorService';

export default function AIStudioDashboard() {
  const [blueprints, setBlueprints] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [activeBlueprint, setActiveBlueprint] = useState(null);
  const [showWizard, setShowWizard] = useState(false);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    setLoading(true);
    try {
      const [listRes, tmplRes, metRes] = await Promise.all([
        generatorService.getBlueprints(),
        generatorService.getStarterTemplates(),
        generatorService.getMetrics(),
      ]);
      setBlueprints(listRes || []);
      setTemplates(tmplRes || []);
      setMetrics(metRes || null);
      if (listRes && listRes.length > 0 && !activeBlueprint) {
        setActiveBlueprint(listRes[0]);
      }
    } catch (err) {
      console.error('Failed to load AI Studio data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleGenerated = (blueprint) => {
    setBlueprints([blueprint, ...blueprints]);
    setActiveBlueprint(blueprint);
    setShowWizard(false);
  };

  const handleClone = async () => {
    if (!activeBlueprint) return;
    try {
      const cloned = await generatorService.cloneBlueprint(activeBlueprint.id);
      setBlueprints([cloned, ...blueprints]);
      setActiveBlueprint(cloned);
    } catch (err) {
      alert(`Clone failed: ${err.message}`);
    }
  };

  const handleUpdate = async (updates) => {
    if (!activeBlueprint) return;
    try {
      const updated = await generatorService.updateBlueprint(activeBlueprint.id, updates);
      setActiveBlueprint(updated);
      setBlueprints(blueprints.map((b) => (b.id === updated.id ? updated : b)));
    } catch (err) {
      alert(`Update failed: ${err.message}`);
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <div className="flex items-center gap-2">
            <Wand2 size={24} className="text-cyan-400" />
            <h1 className="text-2xl font-bold text-slate-100">AI Studio</h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">Intelligent Software Blueprint & Architecture Generator</p>
        </div>

        <button
          onClick={() => {
            setShowWizard(true);
            setActiveBlueprint(null);
          }}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-cyan-500 text-slate-950 font-bold text-xs hover:bg-cyan-400 transition-colors shadow-lg shadow-cyan-500/20"
        >
          <Plus size={16} /> New Project Blueprint
        </button>
      </div>

      {/* Analytics Metric Badges */}
      {metrics && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-3.5 flex items-center justify-between">
            <div>
              <span className="text-[11px] text-slate-400 font-semibold uppercase">Total Blueprints</span>
              <div className="text-xl font-bold text-cyan-400 mt-0.5">{metrics.total_blueprints || 0}</div>
            </div>
            <Folder size={20} className="text-slate-600" />
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-xl p-3.5 flex items-center justify-between">
            <div>
              <span className="text-[11px] text-slate-400 font-semibold uppercase">Version Snapshots</span>
              <div className="text-xl font-bold text-emerald-400 mt-0.5">{metrics.total_versions_snapshot || 0}</div>
            </div>
            <Layers size={20} className="text-slate-600" />
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-xl p-3.5 flex items-center justify-between col-span-2">
            <div>
              <span className="text-[11px] text-slate-400 font-semibold uppercase">Top Recommended Tech</span>
              <div className="flex gap-2 mt-1">
                {(metrics.most_recommended_technologies || []).map((t, idx) => (
                  <span key={idx} className="px-2 py-0.5 bg-slate-950 border border-slate-800 rounded text-xs font-mono text-cyan-300">
                    {t.technology}
                  </span>
                ))}
              </div>
            </div>
            <BarChart2 size={20} className="text-slate-600" />
          </div>
        </div>
      )}

      {/* Main Studio View Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Left Sidebar: Saved Blueprints List */}
        <div className="lg:col-span-1 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Saved Blueprints</h3>
            <span className="text-xs font-mono text-cyan-400">{blueprints.length}</span>
          </div>

          <div className="space-y-2 max-h-[600px] overflow-y-auto pr-1">
            {blueprints.map((b) => {
              const isSelected = activeBlueprint?.id === b.id && !showWizard;
              return (
                <div
                  key={b.id}
                  onClick={() => {
                    setActiveBlueprint(b);
                    setShowWizard(false);
                  }}
                  className={`p-3 rounded-xl border text-left cursor-pointer transition-all ${
                    isSelected
                      ? 'bg-cyan-500/20 border-cyan-500/50 text-cyan-300 shadow-sm'
                      : 'bg-slate-900 border-slate-800 text-slate-300 hover:border-slate-700'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold truncate">{b.name}</span>
                    <span className="text-[10px] font-mono text-slate-500">v{b.version}</span>
                  </div>
                  <p className="text-[11px] text-slate-400 truncate mt-1">{b.description}</p>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Main Content Area */}
        <div className="lg:col-span-3">
          {showWizard ? (
            <ProjectGeneratorWizard onBlueprintGenerated={handleGenerated} />
          ) : activeBlueprint ? (
            <BlueprintViewer blueprint={activeBlueprint} onUpdate={handleUpdate} onClone={handleClone} />
          ) : (
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-12 text-center space-y-4">
              <Sparkles size={32} className="mx-auto text-cyan-400" />
              <h3 className="text-lg font-bold text-slate-200">No Blueprint Selected</h3>
              <p className="text-xs text-slate-400 max-w-sm mx-auto">Select a saved blueprint from the sidebar or click below to generate a new software project blueprint.</p>
              <button
                onClick={() => setShowWizard(true)}
                className="px-4 py-2 bg-cyan-500 text-slate-950 font-bold text-xs rounded-xl hover:bg-cyan-400 transition-colors"
              >
                Generate First Blueprint
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
