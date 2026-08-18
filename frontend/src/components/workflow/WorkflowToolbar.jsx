import React from 'react';
import {
  ArrowLeft,
  Play,
  Save,
  CheckCircle2,
  AlertTriangle,
  History,
  Terminal,
  Map,
  Copy,
  Download,
  Upload,
  Sparkles,
  Loader2,
} from 'lucide-react';

export const WorkflowToolbar = ({
  workflow,
  isValid,
  validationErrors,
  isRunning,
  templates = [],
  onRun,
  onSave,
  onExport,
  onImportFile,
  onLoadTemplate,
  onDuplicate,
  onToggleConsole,
  onToggleHistory,
  onToggleMiniMap,
  onBack,
  showConsole,
  showHistory,
  showMiniMap,
}) => {
  return (
    <div className="h-16 px-6 bg-slate-900/90 border-b border-slate-800 flex items-center justify-between backdrop-blur-md z-20">
      {/* Left Title & Status */}
      <div className="flex items-center space-x-4">
        {onBack && (
          <button
            type="button"
            onClick={onBack}
            className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-colors"
            title="Back to Workflows List"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
        )}
        <div>
          <div className="flex items-center space-x-2">
            <h2 className="text-base font-bold text-slate-100">{workflow?.name || 'Untitled Workflow'}</h2>
            <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
              v{workflow?.version || 1} • {workflow?.status || 'DRAFT'}
            </span>
          </div>
          <p className="text-xs text-slate-400 truncate max-w-sm">
            {workflow?.description || 'Visual AI Workflow DAG Canvas'}
          </p>
        </div>

        {/* Validation Status Badge */}
        <div className="flex items-center space-x-1.5 px-3 py-1 rounded-lg bg-slate-950 border border-slate-800 text-xs">
          {isValid ? (
            <>
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span className="text-emerald-400 font-medium">Valid DAG</span>
            </>
          ) : (
            <>
              <AlertTriangle className="w-4 h-4 text-rose-400" />
              <span className="text-rose-400 font-medium" title={validationErrors?.join(', ')}>
                Invalid Graph
              </span>
            </>
          )}
        </div>
      </div>

      {/* Middle Quick Starter Templates Selector */}
      <div className="flex items-center space-x-2">
        <Sparkles className="w-4 h-4 text-purple-400" />
        <select
          onChange={(e) => {
            if (e.target.value) onLoadTemplate(e.target.value);
          }}
          defaultValue=""
          className="bg-slate-950 text-slate-200 text-xs rounded-lg border border-slate-800 px-3 py-1.5 focus:border-purple-500 focus:outline-none"
        >
          <option value="" disabled>Load Starter Template...</option>
          {templates.map((tmpl) => (
            <option key={tmpl.id} value={tmpl.id}>
              {tmpl.name} ({tmpl.category})
            </option>
          ))}
        </select>
      </div>

      {/* Right Actions & Toggles */}
      <div className="flex items-center space-x-2.5">
        <button
          type="button"
          onClick={onExport}
          className="p-2 text-slate-400 hover:text-slate-200 rounded-lg hover:bg-slate-800 border border-slate-800 transition-colors"
          title="Export Workflow JSON"
        >
          <Download className="w-4 h-4" />
        </button>

        <label className="p-2 text-slate-400 hover:text-slate-200 rounded-lg hover:bg-slate-800 border border-slate-800 cursor-pointer transition-colors" title="Import Workflow JSON">
          <Upload className="w-4 h-4" />
          <input type="file" accept=".json" onChange={onImportFile} className="hidden" />
        </label>

        <button
          type="button"
          onClick={onDuplicate}
          className="p-2 text-slate-400 hover:text-slate-200 rounded-lg hover:bg-slate-800 border border-slate-800 transition-colors"
          title="Duplicate Workflow"
        >
          <Copy className="w-4 h-4" />
        </button>

        <button
          type="button"
          onClick={onSave}
          className="flex items-center space-x-1.5 px-3.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-medium transition-colors"
        >
          <Save className="w-4 h-4 text-cyan-400" />
          <span>Save</span>
        </button>

        <button
          type="button"
          onClick={onRun}
          disabled={!isValid || isRunning}
          className={`flex items-center space-x-1.5 px-4 py-1.5 rounded-lg text-xs font-semibold text-white shadow-lg transition-all ${
            !isValid || isRunning
              ? 'bg-slate-800 text-slate-500 border border-slate-700 cursor-not-allowed'
              : 'bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 border border-cyan-400/30 shadow-cyan-500/20'
          }`}
        >
          {isRunning ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Executing...</span>
            </>
          ) : (
            <>
              <Play className="w-4 h-4 fill-current" />
              <span>Run Execution</span>
            </>
          )}
        </button>

        <div className="h-6 w-[1px] bg-slate-800 mx-1" />

        {/* View Toggles */}
        <button
          type="button"
          onClick={onToggleConsole}
          className={`p-2 rounded-lg border transition-colors ${
            showConsole
              ? 'bg-cyan-500/20 text-cyan-400 border-cyan-500/40'
              : 'bg-slate-900 text-slate-400 border-slate-800 hover:bg-slate-800'
          }`}
          title="Toggle Execution Console"
        >
          <Terminal className="w-4 h-4" />
        </button>

        <button
          type="button"
          onClick={onToggleHistory}
          className={`p-2 rounded-lg border transition-colors ${
            showHistory
              ? 'bg-purple-500/20 text-purple-400 border-purple-500/40'
              : 'bg-slate-900 text-slate-400 border-slate-800 hover:bg-slate-800'
          }`}
          title="Toggle Execution History"
        >
          <History className="w-4 h-4" />
        </button>

        <button
          type="button"
          onClick={onToggleMiniMap}
          className={`p-2 rounded-lg border transition-colors ${
            showMiniMap
              ? 'bg-indigo-500/20 text-indigo-400 border-indigo-500/40'
              : 'bg-slate-900 text-slate-400 border-slate-800 hover:bg-slate-800'
          }`}
          title="Toggle MiniMap"
        >
          <Map className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
