import React, { useState } from 'react';
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
  Search,
  Plus,
} from 'lucide-react';

const NODE_CATALOG = [
  {
    category: 'Triggers & Flow',
    nodes: [
      { type: 'start', label: 'Start Entry', icon: Play, desc: 'Workflow entry point and input parameters' },
      { type: 'end', label: 'End Output', icon: Square, desc: 'Workflow exit point and final output payload' },
    ],
  },
  {
    category: 'AI & Knowledge',
    nodes: [
      { type: 'llm_prompt', label: 'LLM Prompt', icon: Bot, desc: 'Execute AI prompt with provider/model selection' },
      { type: 'knowledge_query', label: 'Knowledge Query', icon: BookOpen, desc: 'RAG search against indexed knowledge base' },
    ],
  },
  {
    category: 'Data & Analytics',
    nodes: [
      { type: 'document_analysis', label: 'Document Analysis', icon: FileText, desc: 'Analyze text, PDFs, structured document assets' },
      { type: 'dataset_analysis', label: 'Dataset Analysis', icon: Database, desc: 'Profile CSV/Excel tabular data and statistics' },
    ],
  },
  {
    category: 'Logic & Utility',
    nodes: [
      { type: 'conditional', label: 'Conditional Branch', icon: GitBranch, desc: 'Evaluates boolean condition expression' },
      { type: 'variable', label: 'Variable Assignment', icon: Variable, desc: 'Set or update workflow context variable' },
      { type: 'delay', label: 'Delay Timer', icon: Clock, desc: 'Pause workflow execution for specified seconds' },
      { type: 'http_request', label: 'HTTP Request', icon: Globe, desc: 'Execute REST API HTTP request' },
      { type: 'python_script', label: 'Python Script', icon: Code2, desc: 'Execute custom Python logic snippet' },
    ],
  },
  {
    category: 'Actions & Outputs',
    nodes: [
      { type: 'export', label: 'Export Report', icon: Share2, desc: 'Generate JSON/Markdown/PDF export document' },
      { type: 'notification', label: 'Send Notification', icon: Bell, desc: 'Trigger system notification or alert' },
    ],
  },
];

export const WorkflowSidebar = ({ onAddNode }) => {
  const [searchTerm, setSearchTerm] = useState('');

  const filteredCatalog = NODE_CATALOG.map((cat) => ({
    ...cat,
    nodes: cat.nodes.filter(
      (n) =>
        n.label.toLowerCase().includes(searchTerm.toLowerCase()) ||
        n.desc.toLowerCase().includes(searchTerm.toLowerCase())
    ),
  })).filter((cat) => cat.nodes.length > 0);

  return (
    <aside className="w-72 bg-slate-900/95 border-r border-slate-800 flex flex-col backdrop-blur-md z-10 select-none">
      {/* Search Header */}
      <div className="p-4 border-b border-slate-800">
        <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">AI Node Palette</h3>
        <div className="relative">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
          <input
            type="text"
            placeholder="Search AI blocks..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-slate-950 text-slate-200 text-xs rounded-lg pl-9 pr-3 py-2 border border-slate-800 focus:border-cyan-500 focus:outline-none"
          />
        </div>
      </div>

      {/* Node Catalog List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        {filteredCatalog.map((cat) => (
          <div key={cat.category} className="space-y-2">
            <h4 className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider px-1">
              {cat.category}
            </h4>
            <div className="space-y-2">
              {cat.nodes.map((node) => {
                const Icon = node.icon;
                return (
                  <div
                    key={node.type}
                    onClick={() => onAddNode(node.type, node.label)}
                    draggable
                    onDragStart={(e) => {
                      const payload = JSON.stringify({ type: node.type, label: node.label });
                      e.dataTransfer.setData('text/plain', payload);
                      e.dataTransfer.setData('application/neurodesk-node', payload);
                      e.dataTransfer.effectAllowed = 'copy';
                    }}
                    className="group p-3 rounded-xl bg-slate-950/60 hover:bg-slate-800/80 border border-slate-800/80 hover:border-cyan-500/40 cursor-grab active:cursor-grabbing transition-all duration-150 flex items-start space-x-3 shadow-sm hover:shadow-cyan-500/10"
                  >
                    <div className="p-2 rounded-lg bg-slate-900 border border-slate-800 text-cyan-400 group-hover:border-cyan-500/30 group-hover:text-cyan-300">
                      <Icon className="w-4 h-4" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-semibold text-slate-200 group-hover:text-cyan-300">
                          {node.label}
                        </span>
                        <Plus className="w-3.5 h-3.5 text-slate-500 opacity-0 group-hover:opacity-100 transition-opacity" />
                      </div>
                      <p className="text-[10px] text-slate-400 mt-0.5 line-clamp-2 leading-relaxed">
                        {node.desc}
                      </p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </aside>
  );
};
