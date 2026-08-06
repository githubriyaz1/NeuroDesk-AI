import React from 'react';
import {
  Play,
  Square,
  Bot,
  BookOpen,
  FileText,
  Database,
  GitBranch,
  Variable,
  Clock,
  Globe,
  Code2,
  Share2,
  Bell,
  CheckCircle2,
  XCircle,
  Loader2,
  Trash2,
  Settings,
} from 'lucide-react';

const NODE_ICONS = {
  start: Play,
  end: Square,
  llm_prompt: Bot,
  knowledge_query: BookOpen,
  document_analysis: FileText,
  dataset_analysis: Database,
  conditional: GitBranch,
  variable: Variable,
  delay: Clock,
  http_request: Globe,
  python_script: Code2,
  export: Share2,
  notification: Bell,
};

const NODE_COLORS = {
  start: 'from-emerald-500/20 to-teal-500/20 border-emerald-500/50 text-emerald-400',
  end: 'from-rose-500/20 to-pink-500/20 border-rose-500/50 text-rose-400',
  llm_prompt: 'from-purple-500/20 to-indigo-500/20 border-purple-500/50 text-purple-400',
  knowledge_query: 'from-cyan-500/20 to-blue-500/20 border-cyan-500/50 text-cyan-400',
  document_analysis: 'from-blue-500/20 to-indigo-500/20 border-blue-500/50 text-blue-400',
  dataset_analysis: 'from-amber-500/20 to-orange-500/20 border-amber-500/50 text-amber-400',
  conditional: 'from-violet-500/20 to-fuchsia-500/20 border-violet-500/50 text-violet-400',
  variable: 'from-sky-500/20 to-teal-500/20 border-sky-500/50 text-sky-400',
  delay: 'from-slate-500/20 to-zinc-500/20 border-slate-500/50 text-slate-400',
  http_request: 'from-indigo-500/20 to-cyan-500/20 border-indigo-500/50 text-indigo-400',
  python_script: 'from-lime-500/20 to-emerald-500/20 border-lime-500/50 text-lime-400',
  export: 'from-pink-500/20 to-rose-500/20 border-pink-500/50 text-pink-400',
  notification: 'from-amber-500/20 to-yellow-500/20 border-amber-500/50 text-amber-400',
};

export const WorkflowNode = ({
  node,
  isSelected,
  executionState,
  onSelect,
  onDelete,
  onConfigure,
  onStartConnect,
  onEndConnect,
  onNodeMove,
}) => {
  const IconComponent = NODE_ICONS[node.type] || Bot;
  const colorClass = NODE_COLORS[node.type] || 'from-slate-500/20 to-zinc-500/20 border-slate-500/50 text-slate-400';

  const isRunning = executionState?.status === 'RUNNING';
  const isSuccess = executionState?.status === 'SUCCESS';
  const isFailed = executionState?.status === 'FAILED';

  const handleMouseDown = (e) => {
    if (e.button !== 0) return;
    if (e.target.closest('button')) return;

    onSelect(node);

    const startX = e.clientX;
    const startY = e.clientY;
    const initialPos = { x: node.position?.x || 0, y: node.position?.y || 0 };

    const handleMouseMove = (moveEvent) => {
      const deltaX = moveEvent.clientX - startX;
      const deltaY = moveEvent.clientY - startY;
      const newPos = {
        x: Math.max(0, Math.round(initialPos.x + deltaX)),
        y: Math.max(0, Math.round(initialPos.y + deltaY)),
      };
      if (onNodeMove) {
        onNodeMove(node.id, newPos);
      }
    };

    const handleMouseUp = () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    };

    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mouseup', handleMouseUp);
  };

  return (
    <div
      onMouseDown={handleMouseDown}
      onClick={(e) => {
        e.stopPropagation();
        onSelect(node);
      }}
      style={{
        transform: `translate(${node.position?.x || 0}px, ${node.position?.y || 0}px)`,
      }}
      className={`absolute w-64 rounded-xl border backdrop-blur-md transition-all duration-75 cursor-move select-none shadow-xl bg-slate-900/90 ${
        isSelected
          ? 'border-cyan-400 ring-2 ring-cyan-500/30 shadow-cyan-500/20 z-10'
          : 'border-slate-800 hover:border-slate-700'
      }`}
    >
      {/* Input Port Anchor */}
      {node.type !== 'start' && (
        <button
          type="button"
          aria-label="Input Connection Anchor"
          onClick={(e) => {
            e.stopPropagation();
            onEndConnect(node);
          }}
          className="absolute -left-3 top-1/2 -translate-y-1/2 w-6 h-6 rounded-full bg-slate-800 border-2 border-cyan-400 flex items-center justify-center hover:scale-125 transition-transform cursor-crosshair shadow-md group"
          title="Connect Input Here"
        >
          <span className="w-2 h-2 rounded-full bg-cyan-400 group-hover:bg-white" />
        </button>
      )}

      {/* Output Port Anchor */}
      {node.type !== 'end' && (
        <button
          type="button"
          aria-label="Output Connection Anchor"
          onClick={(e) => {
            e.stopPropagation();
            onStartConnect(node);
          }}
          className="absolute -right-3 top-1/2 -translate-y-1/2 w-6 h-6 rounded-full bg-slate-800 border-2 border-cyan-400 flex items-center justify-center hover:scale-125 transition-transform cursor-crosshair shadow-md group"
          title="Drag Output Connection"
        >
          <span className="w-2 h-2 rounded-full bg-cyan-400 group-hover:bg-white" />
        </button>
      )}

      {/* Header Banner */}
      <div className={`px-4 py-3 rounded-t-xl bg-gradient-to-r ${colorClass} flex items-center justify-between border-b border-white/5`}>
        <div className="flex items-center space-x-2.5 min-w-0">
          <div className="p-1.5 rounded-lg bg-slate-950/40 border border-white/10">
            <IconComponent className="w-4 h-4" />
          </div>
          <span className="font-semibold text-sm text-slate-100 truncate">
            {node.label || node.id}
          </span>
        </div>

        {/* Status indicator or Action controls */}
        <div className="flex items-center space-x-1">
          {isRunning && <Loader2 className="w-4 h-4 text-cyan-400 animate-spin" />}
          {isSuccess && <CheckCircle2 className="w-4 h-4 text-emerald-400" />}
          {isFailed && <XCircle className="w-4 h-4 text-rose-400" />}
          
          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              onConfigure(node);
            }}
            className="p-1 text-slate-400 hover:text-cyan-400 rounded-md hover:bg-slate-800/60 transition-colors"
            title="Configure Properties"
          >
            <Settings className="w-3.5 h-3.5" />
          </button>
          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              onDelete(node.id);
            }}
            className="p-1 text-slate-400 hover:text-rose-400 rounded-md hover:bg-slate-800/60 transition-colors"
            title="Delete Node"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Body Content Details */}
      <div className="p-3 space-y-2 text-xs text-slate-300">
        <div className="flex justify-between items-center text-slate-400">
          <span>Type:</span>
          <span className="font-mono text-slate-300 capitalize">{node.type.replace('_', ' ')}</span>
        </div>

        {/* Node specific summary previews */}
        {node.data?.prompt && (
          <div className="p-2 rounded bg-slate-950/50 font-mono text-[10px] text-slate-400 truncate border border-slate-800">
            {node.data.prompt}
          </div>
        )}
        {node.data?.query && (
          <div className="p-2 rounded bg-slate-950/50 font-mono text-[10px] text-cyan-400 truncate border border-slate-800">
            Query: {node.data.query}
          </div>
        )}

        {/* Execution Output Latency Badge */}
        {executionState?.latency_ms !== undefined && (
          <div className="pt-1 border-t border-slate-800/80 flex justify-between items-center text-[10px]">
            <span className="text-slate-400">Execution Latency:</span>
            <span className="font-mono text-emerald-400">{executionState.latency_ms} ms</span>
          </div>
        )}
      </div>
    </div>
  );
};
