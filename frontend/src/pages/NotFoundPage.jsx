import React from 'react';
import { Button } from '../components/common/Button';
import { useNavigate } from 'react-router-dom';
import { AlertCircle } from 'lucide-react';

export const NotFoundPage = () => {
  const navigate = useNavigate();

  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] text-center p-6 space-y-4">
      <div className="p-4 rounded-2xl bg-zinc-900 border border-zinc-800 text-indigo-400">
        <AlertCircle size={36} />
      </div>
      <h1 className="text-3xl font-bold text-zinc-100">404 - Page Not Found</h1>
      <p className="text-xs text-zinc-400 max-w-sm leading-relaxed">
        The workspace route or resource you requested does not exist or has been moved.
      </p>
      <Button onClick={() => navigate('/')}>
        Return to Dashboard
      </Button>
    </div>
  );
};
