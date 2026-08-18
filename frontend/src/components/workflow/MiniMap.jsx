import React from 'react';

export const MiniMap = ({ nodes = [], edges = [] }) => {
  // Scale canvas bounds (assume 2000x2000 canvas mapped to 160x120 minimap)
  const scaleX = 160 / 2000;
  const scaleY = 120 / 2000;

  return (
    <div className="w-44 h-32 bg-slate-950/90 border border-slate-800 rounded-xl p-2 backdrop-blur-md shadow-2xl relative select-none overflow-hidden">
      <div className="text-[9px] font-bold text-slate-500 uppercase tracking-wider mb-1">
        Graph MiniMap
      </div>

      <svg className="w-full h-24 bg-slate-900/60 rounded border border-slate-800/60">
        {/* Render edges */}
        {edges.map((e) => {
          const sourceNode = nodes.find((n) => n.id === e.source);
          const targetNode = nodes.find((n) => n.id === e.target);
          if (!sourceNode || !targetNode) return null;

          const x1 = (sourceNode.position.x + 100) * scaleX;
          const y1 = (sourceNode.position.y + 50) * scaleY;
          const x2 = (targetNode.position.x + 100) * scaleX;
          const y2 = (targetNode.position.y + 50) * scaleY;

          return (
            <line
              key={e.id}
              x1={x1}
              y1={y1}
              x2={x2}
              y2={y2}
              stroke="#475569"
              strokeWidth={1}
            />
          );
        })}

        {/* Render nodes */}
        {nodes.map((n) => {
          const x = (n.position.x + 100) * scaleX;
          const y = (n.position.y + 50) * scaleY;

          return (
            <rect
              key={n.id}
              x={x}
              y={y}
              width={16}
              height={10}
              rx={2}
              fill={n.type === 'start' ? '#10b981' : n.type === 'end' ? '#f43f5e' : '#06b6d4'}
              opacity={0.8}
            />
          );
        })}
      </svg>
    </div>
  );
};
