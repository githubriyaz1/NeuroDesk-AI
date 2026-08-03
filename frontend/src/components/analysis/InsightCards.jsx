import React from 'react';
import { Lightbulb, AlertTriangle, TrendingUp, CheckSquare, ShieldCheck, Zap } from 'lucide-react';

export const InsightCards = ({ insights = [] }) => {
  const getCategoryTheme = (category) => {
    switch (category?.toLowerCase()) {
      case 'risk':
        return { icon: <AlertTriangle className="w-4 h-4 text-red-400" />, border: 'border-red-500/30', bg: 'bg-red-500/10', titleColor: 'text-red-300' };
      case 'opportunity':
        return { icon: <Zap className="w-4 h-4 text-amber-400" />, border: 'border-amber-500/30', bg: 'bg-amber-500/10', titleColor: 'text-amber-300' };
      case 'recommendation':
        return { icon: <TrendingUp className="w-4 h-4 text-emerald-400" />, border: 'border-emerald-500/30', bg: 'bg-emerald-500/10', titleColor: 'text-emerald-300' };
      case 'next_step':
        return { icon: <CheckSquare className="w-4 h-4 text-indigo-400" />, border: 'border-indigo-500/30', bg: 'bg-indigo-500/10', titleColor: 'text-indigo-300' };
      default:
        return { icon: <Lightbulb className="w-4 h-4 text-blue-400" />, border: 'border-blue-500/30', bg: 'bg-blue-500/10', titleColor: 'text-blue-300' };
    }
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
      {insights.map((item, idx) => {
        const theme = getCategoryTheme(item.category);
        const confidencePct = Math.round((item.confidence_score || 0.85) * 100);

        return (
          <div key={idx} className={`p-3.5 border ${theme.border} ${theme.bg} rounded-xl space-y-2 backdrop-blur-md`}>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 font-semibold text-xs">
                {theme.icon}
                <span className={theme.titleColor}>{item.title}</span>
              </div>
              <span className="flex items-center gap-1 text-[10px] font-mono bg-slate-900/60 text-slate-300 px-2 py-0.5 rounded-full border border-slate-700">
                <ShieldCheck className="w-3 h-3 text-blue-400" /> {confidencePct}%
              </span>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed font-sans">{item.description}</p>
          </div>
        );
      })}
    </div>
  );
};
