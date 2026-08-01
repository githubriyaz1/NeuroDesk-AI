import React from 'react';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { Settings, Shield, Server, Key, Terminal } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';

export const SettingsPage = () => {
  const { user } = useAuth();

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-xl font-bold text-zinc-100">System & Workspace Settings</h1>
        <p className="text-xs text-zinc-400 mt-1">Configure environment variables, API keys, database connections, and security credentials.</p>
      </div>

      <Card title="User Identity & Authentication" subtitle="Pluggable security architecture settings">
        <div className="space-y-4 text-xs">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-zinc-400 mb-1 font-mono">Full Name</label>
              <input
                type="text"
                readOnly
                value={user?.fullName || ''}
                className="w-full px-3 py-2 bg-zinc-950 border border-zinc-800 rounded-lg text-zinc-300 font-mono"
              />
            </div>
            <div>
              <label className="block text-zinc-400 mb-1 font-mono">Email Address</label>
              <input
                type="email"
                readOnly
                value={user?.email || ''}
                className="w-full px-3 py-2 bg-zinc-950 border border-zinc-800 rounded-lg text-zinc-300 font-mono"
              />
            </div>
          </div>
          <div className="flex items-center justify-between pt-2">
            <span className="text-zinc-400">Current Role</span>
            <Badge variant="info">{user?.role || 'admin'}</Badge>
          </div>
        </div>
      </Card>

      <Card title="Backend & Database Connectivity" subtitle="PostgreSQL and FastAPI environment status">
        <div className="space-y-3 text-xs">
          <div className="flex items-center justify-between p-3 rounded-lg bg-zinc-950/60 border border-zinc-800">
            <div className="flex items-center gap-2">
              <Server size={16} className="text-indigo-400" />
              <span>FastAPI Gateway Engine</span>
            </div>
            <span className="font-mono text-emerald-400">v1.0.0 Online</span>
          </div>
          <div className="flex items-center justify-between p-3 rounded-lg bg-zinc-950/60 border border-zinc-800">
            <div className="flex items-center gap-2">
              <Shield size={16} className="text-indigo-400" />
              <span>PostgreSQL SQLAlchemy 2.0 Async ORM</span>
            </div>
            <span className="font-mono text-emerald-400">Connected</span>
          </div>
        </div>
      </Card>
    </div>
  );
};
