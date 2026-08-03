import React from 'react';
import { BarChart3, Database, AlertCircle, Layers } from 'lucide-react';

export const StatisticsPanel = ({ datasetReport }) => {
  if (!datasetReport) return null;

  const { total_rows, total_columns, missing_values_count, duplicate_rows_count, columns_summary = [] } = datasetReport;

  return (
    <div className="space-y-4">
      {/* Overview Stat Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
        <div className="bg-slate-800/80 p-3 rounded-xl border border-slate-700/60 text-center">
          <span className="text-[11px] text-slate-400 block">Total Rows</span>
          <span className="text-base font-bold text-slate-100">{total_rows}</span>
        </div>
        <div className="bg-slate-800/80 p-3 rounded-xl border border-slate-700/60 text-center">
          <span className="text-[11px] text-slate-400 block">Total Columns</span>
          <span className="text-base font-bold text-blue-400">{total_columns}</span>
        </div>
        <div className="bg-slate-800/80 p-3 rounded-xl border border-slate-700/60 text-center">
          <span className="text-[11px] text-slate-400 block">Missing Values</span>
          <span className={`text-base font-bold ${missing_values_count > 0 ? 'text-amber-400' : 'text-emerald-400'}`}>
            {missing_values_count}
          </span>
        </div>
        <div className="bg-slate-800/80 p-3 rounded-xl border border-slate-700/60 text-center">
          <span className="text-[11px] text-slate-400 block">Duplicates</span>
          <span className={`text-base font-bold ${duplicate_rows_count > 0 ? 'text-red-400' : 'text-emerald-400'}`}>
            {duplicate_rows_count}
          </span>
        </div>
      </div>

      {/* Column Details Table */}
      <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-3.5 space-y-3">
        <div className="flex items-center gap-2 text-xs font-semibold text-slate-200">
          <BarChart3 className="w-4 h-4 text-emerald-400" />
          <span>Column Statistics & Distributions</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-900/80 text-slate-400 uppercase text-[10px] font-semibold border-b border-slate-700">
              <tr>
                <th className="p-2">Column</th>
                <th className="p-2">Type</th>
                <th className="p-2">Null %</th>
                <th className="p-2">Unique</th>
                <th className="p-2">Mean / Mode</th>
                <th className="p-2">Min / Max</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {columns_summary.map((col, idx) => (
                <tr key={idx} className="hover:bg-slate-800/40">
                  <td className="p-2 font-medium text-slate-200">{col.column_name}</td>
                  <td className="p-2 font-mono text-[11px] text-indigo-300">{col.data_type}</td>
                  <td className="p-2 font-mono text-[11px]">{col.null_percentage}%</td>
                  <td className="p-2 font-mono text-[11px]">{col.unique_count}</td>
                  <td className="p-2 font-mono text-[11px]">{col.mean !== null ? col.mean : (col.mode || '-')}</td>
                  <td className="p-2 font-mono text-[11px]">
                    {col.min_value !== null ? `${col.min_value} / ${col.max_value}` : '-'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
