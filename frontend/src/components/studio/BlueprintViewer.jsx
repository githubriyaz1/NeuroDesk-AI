import React, { useState } from 'react';
import {
  Layers,
  Database,
  Code,
  FolderTree,
  Calendar,
  FileText,
  Download,
  Copy,
  Terminal,
  AlertTriangle,
  DollarSign,
} from 'lucide-react';

import ArchitectureViewer from './ArchitectureViewer';
import DatabaseViewer from './DatabaseViewer';
import APIViewer from './APIViewer';
import FolderTreeViewer from './FolderTreeViewer';
import RoadmapViewer from './RoadmapViewer';
import RequirementEditor from './RequirementEditor';
import BlueprintHistoryPanel from './BlueprintHistoryPanel';
import ExportDialog from './ExportDialog';
import RisksViewer from './RisksViewer';
import CostViewer from './CostViewer';

const TABS = [
  { id: 'overview', label: 'Overview', icon: FileText },
  { id: 'requirements', label: 'Requirements', icon: FileText },
  { id: 'architecture', label: 'Architecture', icon: Layers },
  { id: 'database', label: 'Database', icon: Database },
  { id: 'api', label: 'API', icon: Code },
  { id: 'roadmap', label: 'Roadmap', icon: Calendar },
  { id: 'risks', label: 'Risks', icon: AlertTriangle },
  { id: 'cost', label: 'Cost', icon: DollarSign },
  { id: 'exports', label: 'Exports', icon: Download },
];

export default function BlueprintViewer({ blueprint, onUpdate, onClone }) {
  const [activeTab, setActiveTab] = useState('overview');
  const [showExport, setShowExport] = useState(false);

  if (!blueprint) return <div className="text-slate-500 text-xs p-4">Select or generate a blueprint to view.</div>;

  const data = blueprint.blueprint_json || blueprint;

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
              v{blueprint.version || 1} {blueprint.project_type}
            </span>
            <h2 className="text-xl font-bold text-slate-100">{blueprint.name}</h2>
          </div>
          <p className="text-xs text-slate-400 mt-1 max-w-2xl">{blueprint.description}</p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowExport(true)}
            className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 font-semibold text-xs hover:bg-cyan-500/20 transition-colors"
          >
            <Download size={14} /> Export Spec
          </button>
          <button
            onClick={onClone}
            className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-slate-800 border border-slate-700 text-slate-300 font-semibold text-xs hover:bg-slate-700 transition-colors"
          >
            <Copy size={14} /> Clone
          </button>
        </div>
      </div>

      {/* Tabs Bar */}
      <div className="flex overflow-x-auto gap-1 border-b border-slate-800 pb-2">
        {TABS.map((t) => {
          const Icon = t.icon;
          const isActive = activeTab === t.id;
          return (
            <button
              key={t.id}
              onClick={() => setActiveTab(t.id)}
              className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-colors ${
                isActive
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
              }`}
            >
              <Icon size={14} />
              {t.label}
            </button>
          );
        })}
      </div>

      {/* Tab Panels */}
      <div className="space-y-6">
        {activeTab === 'overview' && (
          <div className="space-y-6">
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-2">
              <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Executive Summary</h4>
              <p className="text-xs text-slate-300">
                {data.summary?.executive_summary || data.requirements?.problem_statement || blueprint.description}
              </p>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-2">
                <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Project Objectives</h4>
                <ul className="space-y-1 text-xs text-slate-300 list-disc list-inside">
                  {(data.requirements?.objectives || []).map((obj, i) => (
                    <li key={i}>{obj}</li>
                  ))}
                </ul>
              </div>

              <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-2">
                <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Primary Tech Stack</h4>
                <div className="space-y-1 text-xs text-slate-300 font-mono">
                  <div>Frontend: <span className="text-cyan-400">{data.tech_stack?.recommended_primary?.frontend}</span></div>
                  <div>Backend: <span className="text-cyan-400">{data.tech_stack?.recommended_primary?.backend}</span></div>
                  <div>Database: <span className="text-cyan-400">{data.tech_stack?.recommended_primary?.database}</span></div>
                  <div>DevOps: <span className="text-cyan-400">{data.tech_stack?.recommended_primary?.devops}</span></div>
                </div>
              </div>
            </div>

            <BlueprintHistoryPanel
              versions={blueprint.versions || []}
              currentVersion={blueprint.version || 1}
              onClone={onClone}
            />
          </div>
        )}

        {activeTab === 'requirements' && (
          <RequirementEditor
            requirements={data.requirements}
            onUpdate={(updatedReqs) => onUpdate({ requirements: updatedReqs })}
          />
        )}

        {activeTab === 'architecture' && <ArchitectureViewer architecture={data.architecture} />}

        {activeTab === 'database' && <DatabaseViewer databaseSchema={data.database_schema} />}

        {activeTab === 'api' && <APIViewer apiContracts={data.api_contracts} />}

        {activeTab === 'roadmap' && <RoadmapViewer roadmap={data.roadmap} />}

        {activeTab === 'risks' && <RisksViewer riskAssessment={data.risk_assessment} />}

        {activeTab === 'cost' && <CostViewer costEstimation={data.cost_estimation} />}

        {activeTab === 'exports' && (
          <div className="p-6 bg-slate-900 border border-slate-800 rounded-xl text-center space-y-4">
            <h3 className="text-sm font-bold text-slate-100">Export Blueprint Package</h3>
            <p className="text-xs text-slate-400 max-w-md mx-auto">
              Download your complete architectural blueprint specification in Markdown, JSON, YAML, or HTML format.
            </p>
            <button
              onClick={() => setShowExport(true)}
              className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white font-semibold text-xs rounded-xl shadow-lg shadow-cyan-500/25 transition-all"
            >
              Configure Export Options
            </button>
          </div>
        )}
      </div>

      {showExport && (
        <ExportDialog blueprintId={blueprint.id} onClose={() => setShowExport(false)} />
      )}
    </div>
  );
}
