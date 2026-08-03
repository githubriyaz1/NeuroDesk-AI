import React, { useState } from 'react';
import { Wand2, Sparkles, Code2, Server, Database as DbIcon, Shield } from 'lucide-react';
import TechnologySelector from './TechnologySelector';
import { generatorService } from '../../services/generatorService';

const PROJECT_TYPES = [
  { id: 'web_app', label: 'Web Application', icon: Code2 },
  { id: 'mobile_app', label: 'Mobile Application', icon: Sparkles },
  { id: 'desktop_app', label: 'Desktop Application', icon: Server },
  { id: 'rest_api', label: 'REST API Service', icon: Code2 },
  { id: 'microservices', label: 'Microservices Platform', icon: Server },
  { id: 'ai_app', label: 'AI & RAG Application', icon: Wand2 },
  { id: 'saas_platform', label: 'Enterprise SaaS Platform', icon: Shield },
];

export default function ProjectGeneratorWizard({ onBlueprintGenerated }) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [projectType, setProjectType] = useState('web_app');
  const [selectedTech, setSelectedTech] = useState(['React', 'FastAPI', 'PostgreSQL']);
  const [includeKnowledge, setIncludeKnowledge] = useState(true);
  const [generating, setGenerating] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!title.trim() || !description.trim()) return;

    setGenerating(true);
    try {
      const blueprint = await generatorService.generateBlueprint({
        title: title.trim(),
        description: description.trim(),
        project_type: projectType,
        preferred_tech_stack: selectedTech,
        include_knowledge_context: includeKnowledge,
      });
      if (onBlueprintGenerated) onBlueprintGenerated(blueprint);
    } catch (err) {
      alert(`Generation failed: ${err.message}`);
    } finally {
      setGenerating(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-6">
      <div className="space-y-1">
        <h3 className="text-lg font-bold text-slate-100 flex items-center gap-2">
          <Wand2 size={20} className="text-cyan-400" /> Intelligent Project Generator
        </h3>
        <p className="text-xs text-slate-400">Describe your software idea in plain English. NeuroDesk will generate a complete 4-tier blueprint.</p>
      </div>

      <div className="space-y-4">
        {/* Title */}
        <div>
          <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1.5">
            Project Title
          </label>
          <input
            type="text"
            required
            placeholder="e.g. Healthcare Telemedicine Portal"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500"
          />
        </div>

        {/* Description */}
        <div>
          <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1.5">
            Software Idea Description (Plain English)
          </label>
          <textarea
            required
            rows={4}
            placeholder="Describe features, target users, security needs, and core workflow..."
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500"
          />
        </div>

        {/* Project Type */}
        <div>
          <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
            Project Type
          </label>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
            {PROJECT_TYPES.map((pt) => {
              const Icon = pt.icon;
              const isSelected = projectType === pt.id;
              return (
                <button
                  key={pt.id}
                  type="button"
                  onClick={() => setProjectType(pt.id)}
                  className={`p-3 rounded-xl border text-left flex items-center gap-2.5 transition-all ${
                    isSelected
                      ? 'bg-cyan-500/20 border-cyan-500/50 text-cyan-300 shadow-sm'
                      : 'bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-700'
                  }`}
                >
                  <Icon size={16} className={isSelected ? 'text-cyan-400' : 'text-slate-500'} />
                  <span className="text-xs font-medium">{pt.label}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Tech Selector */}
        <TechnologySelector selected={selectedTech} onChange={setSelectedTech} />

        {/* Knowledge Context Checkbox */}
        <div className="flex items-center gap-2 pt-2">
          <input
            type="checkbox"
            id="knowledgeCheck"
            checked={includeKnowledge}
            onChange={(e) => setIncludeKnowledge(e.target.checked)}
            className="rounded bg-slate-950 border-slate-800 text-cyan-500 focus:ring-cyan-500"
          />
          <label htmlFor="knowledgeCheck" className="text-xs text-slate-300">
            Include Knowledge Engine context from uploaded workspace documents & assets
          </label>
        </div>
      </div>

      <button
        type="submit"
        disabled={generating || !title.trim() || !description.trim()}
        className="w-full py-3 bg-cyan-500 text-slate-950 font-bold text-xs rounded-xl hover:bg-cyan-400 disabled:opacity-50 transition-colors flex items-center justify-center gap-2"
      >
        <Sparkles size={16} />
        {generating ? 'Generating Enterprise Blueprint...' : 'Generate Project Blueprint'}
      </button>
    </form>
  );
}
