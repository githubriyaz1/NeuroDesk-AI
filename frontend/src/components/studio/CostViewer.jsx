import React from 'react';
import { DollarSign, Clock, Users, Server } from 'lucide-react';

export default function CostViewer({ costEstimation }) {
  const breakdown = costEstimation?.breakdown || {
    cloud_compute: '$120 / month',
    database_and_cache: '$80 / month',
    storage_cost: '$25 / month',
    ai_api_cost: '$150 / month',
    maintenance_cost: '$50 / month',
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2">
        <DollarSign className="text-emerald-400" size={18} />
        <h3 className="text-sm font-bold text-slate-100">Project Timeline & Cost Estimation</h3>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-1">
          <div className="flex items-center gap-1.5 text-xs text-slate-400 font-medium">
            <Clock size={14} className="text-cyan-400" /> Development Time
          </div>
          <p className="text-sm font-bold text-slate-100">{costEstimation?.development_time || '7 Weeks (4 Sprints)'}</p>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-1">
          <div className="flex items-center gap-1.5 text-xs text-slate-400 font-medium">
            <Users size={14} className="text-indigo-400" /> Team Allocation
          </div>
          <p className="text-sm font-bold text-slate-100">{costEstimation?.team_size || '4 Engineers'}</p>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-1">
          <div className="flex items-center gap-1.5 text-xs text-slate-400 font-medium">
            <Server size={14} className="text-emerald-400" /> Est. Monthly OpEx
          </div>
          <p className="text-sm font-bold text-emerald-400">{costEstimation?.total_monthly_estimated || '$425 / month'}</p>
        </div>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-3">
        <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Cloud & AI Cost Breakdown</h4>
        <div className="space-y-2 text-xs divide-y divide-slate-800">
          {Object.entries(breakdown).map(([key, val], idx) => (
            <div key={idx} className="pt-2 flex items-center justify-between text-slate-300">
              <span className="capitalize">{key.replace(/_/g, ' ')}</span>
              <span className="font-mono text-cyan-400 font-semibold">{val}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
