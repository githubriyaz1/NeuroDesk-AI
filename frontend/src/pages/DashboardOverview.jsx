import React, { useEffect, useState } from 'react';
import { StatCard } from '../components/common/StatCard';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { FolderKanban, Cpu, Sparkles, GitFork, ArrowUpRight, Activity, Clock, Star, Bell, BarChart2 } from 'lucide-react';
import { workspaceService } from '../services/workspaceService';
import { aiStudioService } from '../services/aiStudioService';
import { useNavigate } from 'react-router-dom';
import { useActivity } from '../contexts/ActivityContext';

export const DashboardOverview = () => {
  const [loading, setLoading] = useState(true);
  const [workspaces, setWorkspaces] = useState([]);
  const [models, setModels] = useState([]);
  const navigate = useNavigate();
  const { recentlyOpened, favorites, notifications, activities } = useActivity();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [wsData, modelData] = await Promise.all([
          workspaceService.getWorkspaceItems(),
          aiStudioService.getModels(),
        ]);
        setWorkspaces(wsData || []);
        setModels(modelData || []);
      } catch (err) {
        console.error('Failed to load dashboard statistics:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return <LoadingSpinner label="Initializing NeuroDesk AI Workspace..." />;
  }

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-zinc-900 via-indigo-950/40 to-zinc-900 border border-zinc-800 p-6 md:p-8">
        <div className="relative z-10 max-w-2xl">
          <Badge variant="info" className="mb-3">
            NeuroDesk v1.0.0 — Productivity Studio
          </Badge>
          <h1 className="text-2xl md:text-3xl font-bold text-white tracking-tight">
            Intelligent AI Workspace Overview
          </h1>
          <p className="text-sm text-zinc-400 mt-2 leading-relaxed">
            Welcome back. Continue working on your project blueprints, dataset analysis pipelines, and automated AI workflows.
          </p>
          <div className="flex flex-wrap gap-3 mt-6">
            <Button onClick={() => navigate('/project-generator')} size="sm">
              <Sparkles size={14} className="mr-2" />
              AI Project Generator
            </Button>
            <Button onClick={() => navigate('/workspace')} variant="outline" size="sm">
              <FolderKanban size={14} className="mr-2" />
              Manage Workspace
            </Button>
          </div>
        </div>
        <div className="absolute right-6 bottom-6 opacity-10 hidden md:block">
          <Activity size={180} className="text-indigo-400" />
        </div>
      </div>

      {/* Quick Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Active Datasets" value={workspaces.length} change="+12% this week" icon={FolderKanban} />
        <StatCard title="AI Studio Models" value={models.length} change="94.2% Avg Accuracy" icon={Cpu} />
        <StatCard title="Project Blueprints" value="3 Generated" change="100% Ready" icon={Sparkles} />
        <StatCard title="Active Workflows" value="4 Scheduled" change="Operational" icon={GitFork} />
      </div>

      {/* Continue Working & Favorites Bar */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Continue Working */}
        <Card title="Continue Working" subtitle="Recently opened items and quick resume">
          <div className="space-y-2">
            {recentlyOpened.length === 0 ? (
              <div className="p-4 text-xs text-zinc-500 text-center">No recent activity yet. Click any item to track.</div>
            ) : (
              recentlyOpened.slice(0, 4).map((item, idx) => (
                <div
                  key={idx}
                  onClick={() => navigate(item.path)}
                  className="flex items-center justify-between p-3 rounded-lg bg-zinc-950/60 border border-zinc-800/80 hover:border-cyan-500/40 cursor-pointer transition-all"
                >
                  <div className="flex items-center gap-2.5">
                    <Clock size={14} className="text-cyan-400 shrink-0" />
                    <span className="text-xs font-medium text-zinc-200">{item.title}</span>
                  </div>
                  <span className="text-[10px] font-mono text-zinc-500 uppercase">{item.type}</span>
                </div>
              ))
            )}
          </div>
        </Card>

        {/* Favorite Workflows & Projects */}
        <Card title="Favorite Items" subtitle="Pinned projects, workflows, and chats">
          <div className="space-y-2">
            {favorites.length === 0 ? (
              <div className="p-4 text-xs text-zinc-500 text-center">No favorite items pinned yet.</div>
            ) : (
              favorites.map((fav, idx) => (
                <div
                  key={idx}
                  onClick={() => navigate(fav.path)}
                  className="flex items-center justify-between p-3 rounded-lg bg-zinc-950/60 border border-zinc-800/80 hover:border-amber-500/40 cursor-pointer transition-all"
                >
                  <div className="flex items-center gap-2.5">
                    <Star size={14} className="text-amber-400 fill-amber-400 shrink-0" />
                    <span className="text-xs font-medium text-zinc-200">{fav.name}</span>
                  </div>
                  <span className="text-[10px] font-mono text-amber-400 uppercase">{fav.type}</span>
                </div>
              ))
            )}
          </div>
        </Card>
      </div>

      {/* Two Column Grid: Workspace & Notifications */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Workspace Datasets Card */}
        <Card
          title="Recent Workspace Datasets"
          subtitle="Active data files and document vectors"
          action={
            <Button variant="ghost" size="sm" onClick={() => navigate('/workspace')}>
              View All <ArrowUpRight size={14} className="ml-1" />
            </Button>
          }
        >
          <div className="space-y-3">
            {workspaces.slice(0, 3).map((item) => (
              <div key={item.id} className="flex items-center justify-between p-3 rounded-lg bg-zinc-950/60 border border-zinc-800/80">
                <div>
                  <h4 className="text-xs font-semibold text-zinc-200">{item.name}</h4>
                  <p className="text-[11px] text-zinc-400 mt-0.5">{item.description}</p>
                </div>
                <Badge variant="success">{item.status}</Badge>
              </div>
            ))}
          </div>
        </Card>

        {/* Recent Notifications & Activity */}
        <Card
          title="Recent Activity & Notifications"
          subtitle="Latest system execution events and alerts"
        >
          <div className="space-y-2">
            {notifications.slice(0, 3).map((n) => (
              <div key={n.id} className="p-3 rounded-lg bg-zinc-950/60 border border-zinc-800/80 flex items-start gap-2.5">
                <Bell size={14} className="text-cyan-400 shrink-0 mt-0.5" />
                <div className="min-w-0 flex-1">
                  <div className="flex items-center justify-between">
                    <h5 className="text-xs font-bold text-zinc-200">{n.title}</h5>
                    <span className="text-[10px] font-mono text-zinc-500">{n.time}</span>
                  </div>
                  <p className="text-[11px] text-zinc-400 mt-0.5 truncate">{n.message}</p>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
};
