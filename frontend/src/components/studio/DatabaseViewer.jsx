import React, { useState } from 'react';
import { Database, Key, Table as TableIcon, Copy, Check } from 'lucide-react';

export default function DatabaseViewer({ databaseSchema }) {
  const [copied, setCopied] = useState(false);

  if (!databaseSchema) {
    return <div className="text-slate-500 text-xs">No database schema available.</div>;
  }

  const handleCopy = () => {
    if (databaseSchema.sql_ddl) {
      navigator.clipboard.writeText(databaseSchema.sql_ddl);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="space-y-6">
      {/* Table Entity Cards */}
      <div className="grid gap-4 md:grid-cols-2">
        {(databaseSchema.tables || []).map((tbl, idx) => (
          <div key={idx} className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-3">
            <div className="flex items-center gap-2 text-cyan-400 font-semibold text-sm">
              <TableIcon size={16} />
              <span>{tbl.name}</span>
            </div>
            <p className="text-xs text-slate-400">{tbl.description}</p>

            <div className="border border-slate-800/80 rounded-lg overflow-hidden">
              <table className="w-full text-xs text-left text-slate-300">
                <thead className="bg-slate-800/50 text-[11px] text-slate-400 uppercase tracking-wider">
                  <tr>
                    <th className="p-2">Column</th>
                    <th className="p-2">Type</th>
                    <th className="p-2">Key</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/50">
                  {tbl.columns.map((col, cIdx) => (
                    <tr key={cIdx} className="hover:bg-slate-800/30">
                      <td className="p-2 font-mono font-medium text-slate-200">{col.name}</td>
                      <td className="p-2 font-mono text-cyan-400/90 text-[11px]">{col.type}</td>
                      <td className="p-2">
                        {col.primary_key && (
                          <span className="flex items-center gap-1 text-[10px] font-bold text-amber-400">
                            <Key size={10} /> PK
                          </span>
                        )}
                        {col.foreign_key && (
                          <span className="text-[10px] text-sky-400">FK → {col.foreign_key}</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ))}
      </div>

      {/* SQL DDL Preview */}
      {databaseSchema.sql_ddl && (
        <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 flex items-center gap-1.5">
              <Database size={14} className="text-cyan-400" /> Generated SQL DDL Schema
            </span>
            <button
              onClick={handleCopy}
              className="flex items-center gap-1 text-xs text-cyan-400 hover:text-cyan-300 bg-slate-900 border border-slate-800 px-2.5 py-1 rounded-md transition-colors"
            >
              {copied ? <Check size={12} className="text-emerald-400" /> : <Copy size={12} />}
              {copied ? 'Copied DDL' : 'Copy DDL'}
            </button>
          </div>
          <pre className="p-3 bg-slate-900 rounded-lg text-xs font-mono text-slate-300 overflow-x-auto border border-slate-800">
            {databaseSchema.sql_ddl}
          </pre>
        </div>
      )}
    </div>
  );
}
