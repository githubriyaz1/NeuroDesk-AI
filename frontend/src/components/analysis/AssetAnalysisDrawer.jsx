import React, { useState, useEffect } from 'react';
import { Brain, X, Download, RefreshCw, BarChart3, FileText, Lightbulb } from 'lucide-react';
import analysisService from '../../services/analysisService';
import { SummaryCard } from './SummaryCard';
import { InsightCards } from './InsightCards';
import { StatisticsPanel } from './StatisticsPanel';

export const AssetAnalysisDrawer = ({ isOpen, onClose, asset }) => {
  const [docReport, setDocReport] = useState(null);
  const [datasetReport, setDatasetReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('summary');

  const runAnalysis = async () => {
    if (!asset) return;
    try {
      setLoading(true);
      const isTabular = asset.mime_type?.includes('csv') || asset.mime_type?.includes('excel');

      if (isTabular) {
        const res = await analysisService.analyzeDataset(asset.id);
        setDatasetReport(res);
        setActiveTab('statistics');
      } else {
        const res = await analysisService.analyzeDocument(asset.id);
        setDocReport(res);
        setActiveTab('summary');
      }
    } catch (err) {
      console.error('Failed to analyze asset:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen && asset) {
      runAnalysis();
    }
  }, [isOpen, asset]);

  const handleExport = async (format = 'markdown') => {
    try {
      const payload = {
        title: `Analysis Report - ${asset?.filename || 'Asset'}`,
        format: format,
        summary: docReport?.executive_summary || datasetReport?.executive_summary || 'Asset Analysis',
        insights: docReport?.insights || [],
      };
      const exported = await analysisService.exportReport(payload);

      // Download trigger
      const blob = new Blob([exported.content], { type: 'text/plain;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `Analysis_Report_${asset?.filename || 'Export'}.${format === 'json' ? 'json' : 'md'}`;
      link.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Failed to export report:', err);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-y-0 right-0 w-[440px] bg-slate-900 border-l border-slate-800 shadow-2xl z-50 flex flex-col backdrop-blur-2xl">
      {/* Drawer Header */}
      <div className="p-4 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-2 text-slate-100 font-semibold text-sm">
          <Brain className="w-5 h-5 text-indigo-400" />
          <span className="truncate">AI Data Analyst — {asset?.filename}</span>
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={() => handleExport('markdown')}
            className="p-1.5 text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-700 rounded-lg text-xs flex items-center gap-1 border border-slate-700"
          >
            <Download className="w-3.5 h-3.5" /> Export
          </button>
          <button onClick={onClose} className="p-1.5 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded-lg">
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex border-b border-slate-800 bg-slate-900/80 px-4">
        <button
          onClick={() => setActiveTab('summary')}
          className={`flex items-center gap-1.5 px-3 py-2.5 text-xs font-medium border-b-2 transition-colors ${
            activeTab === 'summary' ? 'border-blue-500 text-blue-400' : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <FileText className="w-3.5 h-3.5" /> Summary
        </button>
        {datasetReport && (
          <button
            onClick={() => setActiveTab('statistics')}
            className={`flex items-center gap-1.5 px-3 py-2.5 text-xs font-medium border-b-2 transition-colors ${
              activeTab === 'statistics' ? 'border-blue-500 text-blue-400' : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <BarChart3 className="w-3.5 h-3.5" /> Statistics
          </button>
        )}
        <button
          onClick={() => setActiveTab('insights')}
          className={`flex items-center gap-1.5 px-3 py-2.5 text-xs font-medium border-b-2 transition-colors ${
            activeTab === 'insights' ? 'border-blue-500 text-blue-400' : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Lightbulb className="w-3.5 h-3.5" /> AI Insights
        </button>
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar">
        {loading ? (
          <div className="flex items-center justify-center py-12 text-slate-400 text-xs gap-2">
            <RefreshCw className="w-4 h-4 animate-spin text-blue-400" />
            <span>Analyzing document structure & statistics...</span>
          </div>
        ) : (
          <>
            {activeTab === 'summary' && (
              <SummaryCard
                summary={docReport?.executive_summary || datasetReport?.executive_summary}
                keyPoints={docReport?.key_points || datasetReport?.key_insights}
                keywords={docReport?.keywords || []}
              />
            )}

            {activeTab === 'statistics' && datasetReport && (
              <StatisticsPanel datasetReport={datasetReport} />
            )}

            {activeTab === 'insights' && (
              <InsightCards insights={docReport?.insights || []} />
            )}
          </>
        )}
      </div>
    </div>
  );
};
