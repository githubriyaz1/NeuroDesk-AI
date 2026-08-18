import React from 'react';
import { X } from 'lucide-react';

export const WorkflowEdge = ({
  edge,
  sourceNode,
  targetNode,
  isSelected,
  isExecuting,
  onSelect,
  onDelete,
}) => {
  if (!sourceNode || !targetNode) return null;

  // Node dimensions & port offsets: Output anchor is right center (+256px), Input anchor is left center (+0px)
  const sourceX = sourceNode.position.x + 256;
  const sourceY = sourceNode.position.y + 44;
  const targetX = targetNode.position.x;
  const targetY = targetNode.position.y + 44;

  const dx = Math.abs(targetX - sourceX) * 0.5;
  const controlX1 = sourceX + Math.max(dx, 50);
  const controlX2 = targetX - Math.max(dx, 50);

  const pathString = `M ${sourceX} ${sourceY} C ${controlX1} ${sourceY}, ${controlX2} ${targetY}, ${targetX} ${targetY}`;

  const midX = (sourceX + targetX) / 2;
  const midY = (sourceY + targetY) / 2;

  return (
    <g className="group cursor-pointer" onClick={() => onSelect(edge)}>
      {/* Background thicker invisible path for easier hover selection */}
      <path
        d={pathString}
        fill="none"
        stroke="transparent"
        strokeWidth={16}
      />

      {/* Main Connection Curve Path */}
      <path
        d={pathString}
        fill="none"
        stroke={isSelected ? '#22d3ee' : '#475569'}
        strokeWidth={isSelected ? 3 : 2}
        strokeDasharray={edge.data?.animated || isExecuting ? '6 6' : undefined}
        className={`transition-all duration-200 group-hover:stroke-cyan-400 ${
          isExecuting ? 'animate-pulse stroke-cyan-400' : ''
        }`}
      />

      {/* Edge Delete Button Handle at Center Point */}
      <foreignObject
        x={midX - 10}
        y={midY - 10}
        width={20}
        height={20}
        className="opacity-0 group-hover:opacity-100 transition-opacity"
      >
        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation();
            onDelete(edge.id);
          }}
          className="w-5 h-5 rounded-full bg-slate-900 border border-rose-500 text-rose-400 flex items-center justify-center hover:scale-110 hover:bg-rose-500 hover:text-white transition-all shadow-lg"
          title="Delete Connection"
        >
          <X className="w-3 h-3" />
        </button>
      </foreignObject>
    </g>
  );
};
