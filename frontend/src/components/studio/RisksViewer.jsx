import React from 'react';
import { AlertTriangle, ShieldCheck } from 'lucide-react';

export default function RisksViewer({ riskAssessment }) {
  const risks = riskAssessment?.risks || [
    {
      category: 'Security Risk',
      risk: 'Unauthorized data exposure across tenants.',
      severity: 'High',
      mitigation: 'Enforce tenant isolation middleware and RS256 JWT tokens.',
    },
    {
      category: 'Scaling Risk',
      risk: 'Database pool exhaustion under high concurrency.',
      severity: 'Medium',
      mitigation: 'Implement PgBouncer connection pooling and Redis caching.',
    },
  ];

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <AlertTriangle className="text-amber-400" size={18} />
        <h3 className="text-sm font-bold text-slate-100">Automated Risk Assessment & Mitigation Plan</h3>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {risks.map((item, idx) => (
          <div key={idx} className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-indigo-400">{item.category}</span>
              <span
                className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                  item.severity === 'High'
                    ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                    : 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                }`}
              >
                {item.severity} Risk
              </span>
            </div>
            <p className="text-xs text-slate-200 font-medium">{item.risk}</p>
            <div className="pt-2 border-t border-slate-800 flex items-start gap-1.5 text-xs text-emerald-400">
              <ShieldCheck size={14} className="shrink-0 mt-0.5" />
              <span>
                <strong>Mitigation:</strong> {item.mitigation}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
