import React, { useState } from 'react';
import { Database, Search } from 'lucide-react';
import { Badge } from '../common/Badge';

export const CsvPreview = ({ content }) => {
  const columns = content?.columns || [];
  const rows = content?.rows || [];
  const totalRows = content?.total_rows || rows.length;
  const columnCount = content?.column_count || columns.length;

  const [searchTerm, setSearchTerm] = useState('');

  const filteredRows = rows.filter((row) =>
    Object.values(row).some((val) =>
      String(val).toLowerCase().includes(searchTerm.toLowerCase())
    )
  );

  return (
    <div className="space-y-3 text-xs">
      {/* Specs & Search Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-3 rounded-xl bg-zinc-900/90 border border-zinc-800">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-lg bg-emerald-600/10 text-emerald-400 border border-emerald-500/20">
            <Database size={16} />
          </div>
          <div>
            <span className="font-bold text-zinc-100">{columnCount} Columns</span>
            <span className="text-zinc-500 text-[11px] font-mono ml-2">({totalRows} total rows)</span>
          </div>
        </div>

        <div className="relative">
          <Search className="absolute left-2.5 top-2 text-zinc-500" size={13} />
          <input
            type="text"
            placeholder="Filter table rows..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-8 pr-3 py-1 bg-zinc-950 border border-zinc-800 rounded-lg text-[11px] text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-indigo-500"
          />
        </div>
      </div>

      {/* Table Container */}
      <div className="border border-zinc-800 rounded-xl overflow-hidden bg-zinc-950 max-h-80 overflow-y-auto overflow-x-auto">
        <table className="w-full text-left border-collapse text-[11px]">
          <thead className="bg-zinc-900/90 border-b border-zinc-800 sticky top-0 font-mono text-zinc-400">
            <tr>
              <th className="p-2.5 border-r border-zinc-800/60 w-10 text-center">#</th>
              {columns.map((col, idx) => (
                <th key={idx} className="p-2.5 border-r border-zinc-800/60 font-semibold whitespace-nowrap">
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-900 font-mono text-zinc-300">
            {filteredRows.length === 0 ? (
              <tr>
                <td colSpan={columns.length + 1} className="p-4 text-center text-zinc-500">
                  No matching rows found.
                </td>
              </tr>
            ) : (
              filteredRows.map((row, rIdx) => (
                <tr key={rIdx} className="hover:bg-zinc-900/50 transition-colors">
                  <td className="p-2 text-center text-zinc-500 border-r border-zinc-800/60">{rIdx + 1}</td>
                  {columns.map((col, cIdx) => (
                    <td key={cIdx} className="p-2 border-r border-zinc-800/60 whitespace-nowrap">
                      {String(row[col] ?? '')}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
