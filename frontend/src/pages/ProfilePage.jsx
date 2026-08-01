import React, { useState } from 'react';
import { useAuth } from '../hooks/useAuth';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { Modal } from '../components/common/Modal';
import { User, Mail, Shield, Key, Trash2, LogOut, CheckCircle2, AlertCircle } from 'lucide-react';
import { formatDate } from '../utils/formatters';

export const ProfilePage = () => {
  const { user, updateProfile, changePassword, deleteAccount, logout } = useAuth();

  const [fullName, setFullName] = useState(user?.full_name || user?.fullName || '');
  const [profileMessage, setProfileMessage] = useState('');
  const [profileError, setProfileError] = useState('');
  const [profileLoading, setProfileLoading] = useState(false);

  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [passwordMessage, setPasswordMessage] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const [passwordLoading, setPasswordLoading] = useState(false);

  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [deleteLoading, setDeleteLoading] = useState(false);

  const handleUpdateProfile = async (e) => {
    e.preventDefault();
    if (!fullName.trim()) return;
    setProfileError('');
    setProfileMessage('');
    setProfileLoading(true);

    try {
      await updateProfile({ full_name: fullName });
      setProfileMessage('Profile updated successfully.');
    } catch (err) {
      setProfileError(err.message || 'Failed to update profile.');
    } finally {
      setProfileLoading(false);
    }
  };

  const handleChangePassword = async (e) => {
    e.preventDefault();
    if (!currentPassword || !newPassword) return;
    setPasswordError('');
    setPasswordMessage('');
    setPasswordLoading(true);

    try {
      await changePassword({ current_password: currentPassword, new_password: newPassword });
      setPasswordMessage('Password changed successfully! Active sessions revoked.');
      setCurrentPassword('');
      setNewPassword('');
    } catch (err) {
      setPasswordError(err.message || 'Failed to change password.');
    } finally {
      setPasswordLoading(false);
    }
  };

  const handleDeleteAccount = async () => {
    setDeleteLoading(true);
    try {
      await deleteAccount();
    } catch (err) {
      console.error('Failed to delete account:', err);
    } finally {
      setDeleteLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-zinc-100">User Profile & Account Settings</h1>
          <p className="text-xs text-zinc-400 mt-1">Manage personal details, security credentials, and active session tokens.</p>
        </div>
        <Button variant="danger" size="sm" onClick={logout}>
          <LogOut size={14} className="mr-2" /> Sign Out
        </Button>
      </div>

      {/* Account Overview Header */}
      <div className="bg-gradient-to-r from-zinc-900 via-indigo-950/30 to-zinc-900 border border-zinc-800 rounded-2xl p-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 rounded-2xl bg-indigo-600/20 border border-indigo-500/40 flex items-center justify-center text-indigo-300 font-bold text-xl">
            {user?.full_name ? user.full_name.charAt(0) : 'U'}
          </div>
          <div>
            <h2 className="text-base font-bold text-zinc-100">{user?.full_name || 'User'}</h2>
            <p className="text-xs text-zinc-400 font-mono mt-0.5">{user?.email}</p>
            <div className="flex items-center gap-2 mt-2">
              <Badge variant="info">{user?.role || 'user'}</Badge>
              <Badge variant="success">Active</Badge>
            </div>
          </div>
        </div>
        <div className="text-xs font-mono text-zinc-500 space-y-1 text-right">
          <div>Created: {formatDate(user?.created_at)}</div>
          <div>Last Login: {formatDate(user?.last_login || user?.created_at)}</div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Profile Editing Form */}
        <Card title="Personal Information" subtitle="Update display name details">
          {profileMessage && (
            <div className="flex items-center gap-2 p-3 mb-4 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs">
              <CheckCircle2 size={16} /> <span>{profileMessage}</span>
            </div>
          )}
          {profileError && (
            <div className="flex items-center gap-2 p-3 mb-4 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs">
              <AlertCircle size={16} /> <span>{profileError}</span>
            </div>
          )}
          <form onSubmit={handleUpdateProfile} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-zinc-400 mb-1">Full Name</label>
              <input
                type="text"
                required
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="w-full px-3 py-2 bg-zinc-950 border border-zinc-800 rounded-lg text-xs text-zinc-100 focus:outline-none focus:border-indigo-500"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-zinc-400 mb-1">Email Address (Read-only)</label>
              <input
                type="email"
                disabled
                value={user?.email || ''}
                className="w-full px-3 py-2 bg-zinc-950/60 border border-zinc-800/60 rounded-lg text-xs text-zinc-500 cursor-not-allowed font-mono"
              />
            </div>
            <Button type="submit" size="sm" isLoading={profileLoading}>
              Save Profile Changes
            </Button>
          </form>
        </Card>

        {/* Change Password Form */}
        <Card title="Security & Credentials" subtitle="Update account password">
          {passwordMessage && (
            <div className="flex items-center gap-2 p-3 mb-4 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs">
              <CheckCircle2 size={16} /> <span>{passwordMessage}</span>
            </div>
          )}
          {passwordError && (
            <div className="flex items-center gap-2 p-3 mb-4 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs">
              <AlertCircle size={16} /> <span>{passwordError}</span>
            </div>
          )}
          <form onSubmit={handleChangePassword} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-zinc-400 mb-1">Current Password</label>
              <input
                type="password"
                required
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
                placeholder="••••••••••••"
                className="w-full px-3 py-2 bg-zinc-950 border border-zinc-800 rounded-lg text-xs text-zinc-100 focus:outline-none focus:border-indigo-500"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-zinc-400 mb-1">New Password (min 8 chars)</label>
              <input
                type="password"
                required
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                placeholder="••••••••••••"
                className="w-full px-3 py-2 bg-zinc-950 border border-zinc-800 rounded-lg text-xs text-zinc-100 focus:outline-none focus:border-indigo-500"
              />
            </div>
            <Button type="submit" size="sm" isLoading={passwordLoading}>
              Update Password
            </Button>
          </form>
        </Card>
      </div>

      {/* Danger Zone: Delete Account */}
      <Card title="Danger Zone" className="border-rose-900/40 bg-rose-950/10">
        <div className="flex items-center justify-between">
          <div>
            <h4 className="text-xs font-semibold text-rose-300">Deactivate Workspace Account</h4>
            <p className="text-[11px] text-zinc-400 mt-0.5">
              Soft delete account identity and instantly revoke all active refresh tokens and workspace sessions.
            </p>
          </div>
          <Button variant="danger" size="sm" onClick={() => setIsDeleteModalOpen(true)}>
            <Trash2 size={14} className="mr-1.5" /> Deactivate Account
          </Button>
        </div>
      </Card>

      {/* Account Deletion Confirmation Modal */}
      <Modal isOpen={isDeleteModalOpen} onClose={() => setIsDeleteModalOpen(false)} title="Confirm Account Deactivation">
        <div className="space-y-4 text-xs">
          <p className="text-zinc-300 leading-relaxed">
            Are you sure you want to deactivate your NeuroDesk AI workspace account? This will revoke all active JWT refresh tokens and log you out immediately.
          </p>
          <div className="flex justify-end gap-2 pt-4 border-t border-zinc-800">
            <Button variant="outline" size="sm" onClick={() => setIsDeleteModalOpen(false)}>
              Cancel
            </Button>
            <Button variant="danger" size="sm" isLoading={deleteLoading} onClick={handleDeleteAccount}>
              Deactivate Now
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};
