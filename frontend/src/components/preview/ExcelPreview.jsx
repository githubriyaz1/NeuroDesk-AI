import React, { useState } from 'react';
import { Table, Sheet } from 'lucide-react';

export const ExcelPreview = ({ content }) => {
  const sheetNames = content?.sheet_names || [];
  const defaultSheet = content?.active_sheet || (sheetNames.length > 0 ? sheetNames[0] : 'Sheet1');
  const sheets = content?.sheets || {};

  const [activeSheet, setActiveSheet] = useState(defaultSheet);

  const currentSheetData = sheets[activeSheet] || { headers: [], rows: [] };
  const headers = currentSheetData.headers || [];
  const rows = currentSheetData.rows || [];

  return (
    <div className="space-y-3 text-xs">
      {/* Sheet Tabs */}
      <div className="flex items-center gap-1 border-b border-zinc-800 pb-2 overflow-x-auto">
        {sheetNames.map((sheet) => (
          <button
            key={sheet}
            onClick={() => setActiveSheet(sheet)}
            className={`px-3 py-1.5 rounded-lg text-xs font-mono transition-colors flex-shrink-0 ${
              activeSheet === sheet
                ? 'bg-emerald-600/20 text-emerald-400 border border-emerald-500/30 font-semibold'
                : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900'
            }`}
          >
            {sheet}
          </button>
        ))}
      </div>

      {/* Spreadsheet Table Container */}
      <div className="border border-zinc-800 rounded-xl overflow-hidden bg-zinc-950 max-h-80 overflow-y-auto overflow-x-auto">
        <table className="w-full text-left border-collapse text-[11px]">
          <thead className="bg-zinc-900/90 border-b border-zinc-800 sticky top-0 font-mono text-zinc-400">
            <tr>
              <th className="p-2.5 border-r border-zinc-800/60 w-10 text-center">#</th>
              {headers.map((col, idx) => (
                <th key={idx} className="p-2.5 border-r border-zinc-800/60 font-semibold whitespace-nowrap">
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-900 font-mono text-zinc-300">
            {rows.length === 0 ? (
              <tr>
                <td colSpan={headers.length + 1} className="p-4 text-center text-zinc-500">
                  Empty sheet or no row data.
                </td>
              </tr>
            ) : (
              rows.map((row, rIdx) => (
                <tr key={rIdx} className="hover:bg-zinc-900/50 transition-colors">
                  <td className="p-2 text-center text-zinc-500 border-r border-zinc-800/60">{rIdx + 1}</td>
                  {row.map((cell, cIdx) => (
                    <td key={cIdx} className="p-2 border-r border-zinc-800/60 whitespace-nowrap">
                      {String(cell ?? '')}
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
