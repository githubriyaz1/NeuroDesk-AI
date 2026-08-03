import React, { useState, useEffect } from 'react';
import { X, Settings, Check, Sliders } from 'lucide-react';

export const NodePropertiesPanel = ({ node, onUpdateNode, onClose }) => {
  const [label, setLabel] = useState(node?.label || '');
  const [data, setData] = useState(node?.data || {});

  useEffect(() => {
    if (node) {
      setLabel(node.label || '');
      setData(node.data || {});
    }
  }, [node]);

  if (!node) return null;

  const handleSave = () => {
    onUpdateNode(node.id, { label, data });
  };

  const updateDataField = (key, val) => {
    setData((prev) => ({ ...prev, [key]: val }));
  };

  return (
    <aside className="w-80 bg-slate-900/95 border-l border-slate-800 flex flex-col backdrop-blur-md z-20 shadow-2xl">
      {/* Header */}
      <div className="p-4 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Settings className="w-4 h-4 text-cyan-400" />
          <h3 className="text-sm font-bold text-slate-100">Node Properties</h3>
        </div>
        <button
          type="button"
          onClick={onClose}
          className="p-1 text-slate-400 hover:text-slate-200 rounded-md hover:bg-slate-800 transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Property Forms */}
      <div className="flex-1 overflow-y-auto p-4 space-y-5 text-xs text-slate-200">
        {/* Node Label */}
        <div>
          <label className="block text-slate-400 font-medium mb-1.5">Node Label</label>
          <input
            type="text"
            value={label}
            onChange={(e) => setLabel(e.target.value)}
            className="w-full bg-slate-950 text-slate-100 rounded-lg px-3 py-2 border border-slate-800 focus:border-cyan-500 focus:outline-none"
          />
        </div>

        {/* Node Type Info */}
        <div className="p-3 rounded-lg bg-slate-950 border border-slate-800/80 space-y-1">
          <div className="flex justify-between text-[11px]">
            <span className="text-slate-400">Node ID:</span>
            <span className="font-mono text-cyan-400">{node.id}</span>
          </div>
          <div className="flex justify-between text-[11px]">
            <span className="text-slate-400">Type:</span>
            <span className="font-mono text-purple-400 capitalize">{node.type}</span>
          </div>
        </div>

        {/* Dynamic Fields Based on Node Type */}
        {node.type === 'llm_prompt' && (
          <>
            <div>
              <label className="block text-slate-400 font-medium mb-1.5">Provider</label>
              <select
                value={data.provider || 'mock'}
                onChange={(e) => updateDataField('provider', e.target.value)}
                className="w-full bg-slate-950 text-slate-100 rounded-lg px-3 py-2 border border-slate-800 focus:border-cyan-500 focus:outline-none"
              >
                <option value="google">Google Gemini</option>
                <option value="openai">OpenAI GPT-4</option>
                <option value="anthropic">Anthropic Claude</option>
                <option value="mock">NeuroDesk Mock LLM</option>
              </select>
            </div>
            <div>
              <label className="block text-slate-400 font-medium mb-1.5">Model</label>
              <input
                type="text"
                value={data.model || 'neurodesk-mock-v1'}
                onChange={(e) => updateDataField('model', e.target.value)}
                className="w-full bg-slate-950 text-slate-100 rounded-lg px-3 py-2 border border-slate-800 focus:border-cyan-500 focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-slate-400 font-medium mb-1.5">Prompt Template</label>
              <textarea
                rows={4}
                value={data.prompt || 'Analyze input: {input}'}
                onChange={(e) => updateDataField('prompt', e.target.value)}
                placeholder="Use {input} or {variable_name}"
                className="w-full bg-slate-950 text-slate-100 font-mono text-[11px] rounded-lg p-3 border border-slate-800 focus:border-cyan-500 focus:outline-none"
              />
            </div>
          </>
        )}

        {node.type === 'knowledge_query' && (
          <>
            <div>
              <label className="block text-slate-400 font-medium mb-1.5">Search Query</label>
              <input
                type="text"
                value={data.query || ''}
                onChange={(e) => updateDataField('query', e.target.value)}
                placeholder="e.g. Enterprise security compliance policy"
                className="w-full bg-slate-950 text-slate-100 rounded-lg px-3 py-2 border border-slate-800 focus:border-cyan-500 focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-slate-400 font-medium mb-1.5">
                Retrieved Documents Limit: {data.limit || 5}
              </label>
              <input
                type="range"
                min={1}
                max={20}
                value={data.limit || 5}
                onChange={(e) => updateDataField('limit', parseInt(e.target.value, 10))}
                className="w-full accent-cyan-500"
              />
            </div>
          </>
        )}

        {node.type === 'conditional' && (
          <div>
            <label className="block text-slate-400 font-medium mb-1.5">Condition Expression</label>
            <input
              type="text"
              value={data.condition || 'True'}
              onChange={(e) => updateDataField('condition', e.target.value)}
              placeholder="e.g. True or False"
              className="w-full bg-slate-950 font-mono text-[11px] text-purple-400 rounded-lg px-3 py-2 border border-slate-800 focus:border-cyan-500 focus:outline-none"
            />
          </div>
        )}

        {node.type === 'variable' && (
          <>
            <div>
              <label className="block text-slate-400 font-medium mb-1.5">Variable Name</label>
              <input
                type="text"
                value={data.var_name || 'temp_var'}
                onChange={(e) => updateDataField('var_name', e.target.value)}
                className="w-full bg-slate-950 text-slate-100 rounded-lg px-3 py-2 border border-slate-800 focus:border-cyan-500 focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-slate-400 font-medium mb-1.5">Variable Value</label>
              <input
                type="text"
                value={data.var_value || ''}
                onChange={(e) => updateDataField('var_value', e.target.value)}
                className="w-full bg-slate-950 text-slate-100 rounded-lg px-3 py-2 border border-slate-800 focus:border-cyan-500 focus:outline-none"
              />
            </div>
          </>
        )}

        {node.type === 'delay' && (
          <div>
            <label className="block text-slate-400 font-medium mb-1.5">Delay Duration (Seconds)</label>
            <input
              type="number"
              min={1}
              max={5}
              value={data.seconds || 1}
              onChange={(e) => updateDataField('seconds', parseFloat(e.target.value))}
              className="w-full bg-slate-950 text-slate-100 rounded-lg px-3 py-2 border border-slate-800 focus:border-cyan-500 focus:outline-none"
            />
          </div>
        )}

        {node.type === 'http_request' && (
          <>
            <div>
              <label className="block text-slate-400 font-medium mb-1.5">Target URL</label>
              <input
                type="text"
                value={data.url || 'https://api.example.com/status'}
                onChange={(e) => updateDataField('url', e.target.value)}
                className="w-full bg-slate-950 text-slate-100 rounded-lg px-3 py-2 border border-slate-800 focus:border-cyan-500 focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-slate-400 font-medium mb-1.5">HTTP Method</label>
              <select
                value={data.method || 'GET'}
                onChange={(e) => updateDataField('method', e.target.value)}
                className="w-full bg-slate-950 text-slate-100 rounded-lg px-3 py-2 border border-slate-800 focus:border-cyan-500 focus:outline-none"
              >
                <option value="GET">GET</option>
                <option value="POST">POST</option>
                <option value="PUT">PUT</option>
                <option value="DELETE">DELETE</option>
              </select>
            </div>
          </>
        )}

        {node.type === 'python_script' && (
          <div>
            <label className="block text-slate-400 font-medium mb-1.5">Python Code Snippet</label>
            <textarea
              rows={5}
              value={data.code || 'result = 42'}
              onChange={(e) => updateDataField('code', e.target.value)}
              className="w-full bg-slate-950 text-lime-400 font-mono text-[11px] rounded-lg p-3 border border-slate-800 focus:border-cyan-500 focus:outline-none"
            />
          </div>
        )}

        {node.type === 'export' && (
          <div>
            <label className="block text-slate-400 font-medium mb-1.5">Export Format</label>
            <select
              value={data.format || 'markdown'}
              onChange={(e) => updateDataField('format', e.target.value)}
              className="w-full bg-slate-950 text-slate-100 rounded-lg px-3 py-2 border border-slate-800 focus:border-cyan-500 focus:outline-none"
            >
              <option value="markdown">Markdown (.md)</option>
              <option value="json">JSON (.json)</option>
              <option value="pdf">PDF Document (.pdf)</option>
            </select>
          </div>
        )}

        {node.type === 'notification' && (
          <div>
            <label className="block text-slate-400 font-medium mb-1.5">Alert Message</label>
            <input
              type="text"
              value={data.message || 'Workflow step completed'}
              onChange={(e) => updateDataField('message', e.target.value)}
              className="w-full bg-slate-950 text-slate-100 rounded-lg px-3 py-2 border border-slate-800 focus:border-cyan-500 focus:outline-none"
            />
          </div>
        )}
      </div>

      {/* Action Footer */}
      <div className="p-4 border-t border-slate-800">
        <button
          type="button"
          onClick={handleSave}
          className="w-full py-2 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-semibold text-xs transition-colors flex items-center justify-center space-x-1.5"
        >
          <Check className="w-4 h-4" />
          <span>Apply Changes</span>
        </button>
      </div>
    </aside>
  );
};
