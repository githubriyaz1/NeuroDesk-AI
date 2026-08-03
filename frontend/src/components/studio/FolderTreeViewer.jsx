import React, { useState } from 'react';
import { Folder, FileText, ChevronRight, ChevronDown } from 'lucide-react';

const TreeNode = ({ item, depth = 0 }) => {
  const [expanded, setExpanded] = useState(true);
  const isDir = item.type === 'directory' || Boolean(item.children);

  return (
    <div className="select-none text-xs font-mono">
      <div
        onClick={() => isDir && setExpanded(!expanded)}
        style={{ paddingLeft: `${depth * 16}px` }}
        className={`flex items-center gap-2 py-1 px-2 rounded hover:bg-slate-800/60 cursor-pointer ${
          isDir ? 'text-cyan-400 font-semibold' : 'text-slate-300'
        }`}
      >
        {isDir ? (
          <>
            {expanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
            <Folder size={14} className="text-cyan-400" />
          </>
        ) : (
          <>
            <span className="w-3.5" />
            <FileText size={14} className="text-slate-400" />
          </>
        )}
        <span>{item.name}</span>
        {item.description && (
          <span className="text-[10px] text-slate-500 font-sans italic ml-2">
            // {item.description}
          </span>
        )}
      </div>

      {isDir && expanded && item.children && (
        <div>
          {item.children.map((child, idx) => (
            <TreeNode key={idx} item={child} depth={depth + 1} />
          ))}
        </div>
      )}
    </div>
  );
};

export default function FolderTreeViewer({ tree }) {
  if (!tree) return <div className="text-slate-500 text-xs">No folder tree generated.</div>;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 overflow-x-auto">
      <TreeNode item={tree} />
    </div>
  );
}
