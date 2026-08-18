import React from 'react';
import { Calendar, CheckCircle2 } from 'lucide-react';

export default function RoadmapViewer({ roadmap }) {
  if (!roadmap || !roadmap.sprints) {
    return <div className="text-slate-500 text-xs">No roadmap timeline available.</div>;
  }

  return (
    <div className="space-y-4">
      <div className="grid gap-4 md:grid-cols-2">
        {roadmap.sprints.map((s, idx) => (
          <div key={idx} className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-3 relative overflow-hidden">
            <div className="flex items-center justify-between">
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                Sprint {s.sprint_number}
              </span>
              <span className="flex items-center gap-1 text-xs text-slate-400 font-mono">
                <Calendar size={12} /> {s.duration}
              </span>
            </div>

            <h4 className="text-sm font-semibold text-slate-100">{s.title}</h4>

            <div className="space-y-1.5 pt-1">
              {s.deliverables.map((item, dIdx) => (
                <div key={dIdx} className="flex items-start gap-2 text-xs text-slate-300">
                  <CheckCircle2 size={14} className="text-emerald-400 shrink-0 mt-0.5" />
                  <span>{item}</span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
