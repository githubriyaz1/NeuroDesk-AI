import React, { useState, useEffect } from 'react';
import { Wand2, Sparkles, FolderGit2, Download, ExternalLink, ArrowRight, Layers, LayoutGrid, CheckCircle2 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import ProjectGeneratorWizard from '../components/studio/ProjectGeneratorWizard';
import BlueprintViewer from '../components/studio/BlueprintViewer';
import { generatorService } from '../services/generatorService';

export const ProjectGeneratorPage = () => {
  const navigate = useNavigate();
  const [generatedBlueprint, setGeneratedBlueprint] = useState(null);
  const [starterTemplates, setStarterTemplates] = useState([]);
  const [recentBlueprints, setRecentBlueprints] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTemplatesAndHistory = async () => {
      setLoading(true);
      try {
        const [tmplRes, bpRes] = await Promise.all([
          generatorService.getStarterTemplates(),
          generatorService.getBlueprints({ limit: 5 }),
        ]);
        setStarterTemplates(tmplRes || []);
        setRecentBlueprints(bpRes || []);
      } catch (err) {
        console.error('Failed to load generator templates:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchTemplatesAndHistory();
  }, []);

  const handleGenerated = (blueprint) => {
    setGeneratedBlueprint(blueprint);
    setRecentBlueprints((prev) => [blueprint, ...prev]);
  };

  const handleSelectTemplate = (template) => {
    setGeneratedBlueprint(template);
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <div className="flex items-center gap-2.5">
            <div className="p-2 bg-cyan-500/10 border border-cyan-500/20 rounded-xl text-cyan-400">
              <Wand2 size={24} />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-slate-100">AI Project Generator</h1>
              <p className="text-xs text-slate-400 mt-0.5">Instant Enterprise Software Blueprint & Architecture Generator</p>
            </div>
          </div>
        </div>

        {generatedBlueprint && (
          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate('/ai-studio')}
              className="flex items-center gap-2 px-4 py-2 bg-slate-900 border border-slate-800 text-slate-300 rounded-xl hover:border-slate-700 text-xs font-semibold transition-colors"
            >
              <ExternalLink size={14} className="text-cyan-400" /> Open in AI Studio Workbench
            </button>
          </div>
        )}
      </div>

      {/* Starter Templates Quick Bar */}
      {starterTemplates.length > 0 && !generatedBlueprint && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-2">
              <LayoutGrid size={14} className="text-cyan-400" /> Starter Architecture Blueprints
            </h3>
            <span className="text-[11px] text-slate-500">Pick a template to instantly generate</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {starterTemplates.slice(0, 3).map((tmpl, idx) => (
              <div
                key={idx}
                onClick={() => handleSelectTemplate(tmpl)}
                className="p-4 bg-slate-900/80 border border-slate-800 rounded-xl hover:border-cyan-500/50 cursor-pointer transition-all space-y-2 group"
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-200 group-hover:text-cyan-300">{tmpl.name}</span>
                  <span className="px-2 py-0.5 bg-slate-950 border border-slate-800 text-[10px] font-mono text-cyan-400 rounded">
                    {tmpl.project_type || 'Full Stack'}
                  </span>
                </div>
                <p className="text-[11px] text-slate-400 line-clamp-2">{tmpl.description}</p>
                <div className="flex items-center gap-1 text-[11px] text-cyan-400 font-semibold pt-1">
                  Generate Blueprint <ArrowRight size={12} className="group-hover:translate-x-1 transition-transform" />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Main Grid: Generator Form on Left, Blueprint Preview on Right */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className={generatedBlueprint ? "lg:col-span-5 space-y-6" : "lg:col-span-8 lg:col-start-3 space-y-6"}>
          <ProjectGeneratorWizard onBlueprintGenerated={handleGenerated} />

          {recentBlueprints.length > 0 && (
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-3">
              <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-2">
                <FolderGit2 size={14} className="text-emerald-400" /> Recent Generated Projects
              </h4>
              <div className="space-y-2">
                {recentBlueprints.slice(0, 4).map((bp) => (
                  <div
                    key={bp.id}
                    onClick={() => setGeneratedBlueprint(bp)}
                    className={`p-3 rounded-xl border flex items-center justify-between cursor-pointer transition-all ${
                      generatedBlueprint?.id === bp.id
                        ? 'bg-cyan-500/20 border-cyan-500/50 text-cyan-300'
                        : 'bg-slate-950 border-slate-800/80 text-slate-300 hover:border-slate-700'
                    }`}
                  >
                    <div>
                      <div className="text-xs font-bold">{bp.name}</div>
                      <div className="text-[10px] text-slate-400">{bp.description}</div>
                    </div>
                    <span className="text-[10px] font-mono text-cyan-400">v{bp.version}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {generatedBlueprint && (
          <div className="lg:col-span-7 space-y-4">
            <div className="flex items-center justify-between bg-slate-900 border border-slate-800 px-4 py-2.5 rounded-xl">
              <span className="text-xs font-bold text-slate-200 flex items-center gap-2">
                <CheckCircle2 size={16} className="text-emerald-400" /> Active Generated Blueprint: {generatedBlueprint.name}
              </span>
              <button
                onClick={() => navigate('/ai-studio')}
                className="text-[11px] font-bold text-cyan-400 hover:underline flex items-center gap-1"
              >
                Inspect in Studio <ArrowRight size={12} />
              </button>
            </div>
            <BlueprintViewer blueprint={generatedBlueprint} />
          </div>
        )}
      </div>
    </div>
  );
};

export default ProjectGeneratorPage;
