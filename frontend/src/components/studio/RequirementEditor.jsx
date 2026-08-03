import React, { useState } from 'react';
import { Plus, Trash2, Edit3 } from 'lucide-react';

export default function RequirementEditor({ requirements, onUpdate }) {
  const [frList, setFrList] = useState(requirements?.functional_requirements || []);
  const [newTitle, setNewTitle] = useState('');
  const [newDesc, setNewDesc] = useState('');

  const addFR = () => {
    if (!newTitle.trim()) return;
    const newFr = {
      id: `FR-${100 + frList.length + 1}`,
      category: 'Custom',
      title: newTitle.trim(),
      description: newDesc.trim() || 'Custom functional requirement',
    };
    const updated = [...frList, newFr];
    setFrList(updated);
    setNewTitle('');
    setNewDesc('');
    if (onUpdate) onUpdate({ ...requirements, functional_requirements: updated });
  };

  const removeFR = (id) => {
    const updated = frList.filter((item) => item.id !== id);
    setFrList(updated);
    if (onUpdate) onUpdate({ ...requirements, functional_requirements: updated });
  };

  return (
    <div className="space-y-6">
      <div className="space-y-3">
        <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Functional Requirements</h4>
        <div className="space-y-2">
          {frList.map((fr) => (
            <div key={fr.id} className="bg-slate-900 border border-slate-800 rounded-xl p-3 flex items-start justify-between">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 font-bold">
                    {fr.id}
                  </span>
                  <h5 className="text-xs font-bold text-slate-100">{fr.title}</h5>
                </div>
                <p className="text-xs text-slate-400 pl-1">{fr.description}</p>
              </div>
              <button
                onClick={() => removeFR(fr.id)}
                className="text-slate-500 hover:text-rose-400 transition-colors p-1"
              >
                <Trash2 size={14} />
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Add New Requirement Form */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 space-y-3">
        <h4 className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
          <Plus size={14} className="text-cyan-400" /> Add Functional Requirement
        </h4>
        <div className="grid gap-2">
          <input
            type="text"
            placeholder="Requirement Title (e.g. Export Reports to PDF)"
            value={newTitle}
            onChange={(e) => setNewTitle(e.target.value)}
            className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500"
          />
          <input
            type="text"
            placeholder="Description details..."
            value={newDesc}
            onChange={(e) => setNewDesc(e.target.value)}
            className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500"
          />
          <button
            onClick={addFR}
            disabled={!newTitle.trim()}
            className="self-end px-4 py-2 bg-cyan-500 text-slate-950 font-semibold text-xs rounded-lg hover:bg-cyan-400 disabled:opacity-50 transition-colors"
          >
            Add Requirement
          </button>
        </div>
      </div>
    </div>
  );
}
