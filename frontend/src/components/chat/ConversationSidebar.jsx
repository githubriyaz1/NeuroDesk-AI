import React, { useState } from 'react';
import {
  Plus,
  Search,
  Pin,
  Star,
  Archive,
  Trash2,
  Copy,
  MoreVertical,
  MessageSquare,
} from 'lucide-react';
import { useChat } from '../../contexts/ChatContext';

export const ConversationSidebar = () => {
  const {
    conversations,
    activeConversation,
    selectConversation,
    createNewConversation,
    searchQuery,
    setSearchQuery,
    filterMode,
    setFilterMode,
    togglePin,
    toggleFavorite,
    archiveConversation,
    duplicateConversation,
    deleteConversation,
  } = useChat();

  const [menuOpenId, setMenuOpenId] = useState(null);

  const pinnedConversations = conversations.filter((c) => c.is_pinned && !c.is_archived);
  const unpinnedConversations = conversations.filter((c) => !c.is_pinned && !c.is_archived);

  return (
    <div className="w-80 border-r border-slate-700/60 bg-slate-900/60 backdrop-blur-md flex flex-col h-full select-none">
      {/* Sidebar Header */}
      <div className="p-4 border-b border-slate-700/50 flex flex-col gap-3">
        <button
          onClick={() => createNewConversation()}
          className="w-full flex items-center justify-center gap-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-medium px-4 py-2.5 rounded-xl shadow-lg shadow-blue-500/20 transition-all active:scale-[0.98]"
        >
          <Plus className="w-5 h-5" />
          <span>New Conversation</span>
        </button>

        {/* Search */}
        <div className="relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search conversations..."
            className="w-full pl-9 pr-3 py-2 bg-slate-800/80 border border-slate-700/60 rounded-lg text-sm text-slate-200 placeholder-slate-400 focus:outline-none focus:border-blue-500 transition-colors"
          />
        </div>

        {/* Filter Pills */}
        <div className="flex items-center gap-1 bg-slate-800/40 p-1 rounded-lg border border-slate-700/40 text-xs">
          {[
            { id: 'all', label: 'All' },
            { id: 'pinned', label: 'Pinned' },
            { id: 'favorites', label: 'Starred' },
            { id: 'archived', label: 'Archive' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setFilterMode(tab.id)}
              className={`flex-1 py-1 rounded-md transition-all font-medium ${
                filterMode === tab.id
                  ? 'bg-slate-700 text-blue-400 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Conversation List */}
      <div className="flex-1 overflow-y-auto p-2 space-y-4 custom-scrollbar">
        {/* Pinned Section */}
        {pinnedConversations.length > 0 && filterMode === 'all' && (
          <div>
            <div className="px-3 py-1.5 text-[11px] font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
              <Pin className="w-3.5 h-3.5 text-blue-400" />
              <span>Pinned Sessions</span>
            </div>
            <div className="space-y-1 mt-1">
              {pinnedConversations.map((conv) => (
                <ConversationItem
                  key={conv.id}
                  conversation={conv}
                  isActive={activeConversation?.id === conv.id}
                  onSelect={() => selectConversation(conv.id)}
                  onPin={() => togglePin(conv.id)}
                  onFavorite={() => toggleFavorite(conv.id)}
                  onArchive={() => archiveConversation(conv.id)}
                  onDuplicate={() => duplicateConversation(conv.id)}
                  onDelete={() => deleteConversation(conv.id)}
                  menuOpen={menuOpenId === conv.id}
                  setMenuOpen={(val) => setMenuOpenId(val ? conv.id : null)}
                />
              ))}
            </div>
          </div>
        )}

        {/* All / Unpinned Section */}
        <div>
          {pinnedConversations.length > 0 && filterMode === 'all' && (
            <div className="px-3 py-1.5 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
              Recent Conversations
            </div>
          )}
          <div className="space-y-1 mt-1">
            {unpinnedConversations.length === 0 && pinnedConversations.length === 0 ? (
              <div className="text-center py-8 px-4 text-slate-500 text-sm">
                <MessageSquare className="w-8 h-8 mx-auto mb-2 opacity-40" />
                <p>No conversations found</p>
              </div>
            ) : (
              unpinnedConversations.map((conv) => (
                <ConversationItem
                  key={conv.id}
                  conversation={conv}
                  isActive={activeConversation?.id === conv.id}
                  onSelect={() => selectConversation(conv.id)}
                  onPin={() => togglePin(conv.id)}
                  onFavorite={() => toggleFavorite(conv.id)}
                  onArchive={() => archiveConversation(conv.id)}
                  onDuplicate={() => duplicateConversation(conv.id)}
                  onDelete={() => deleteConversation(conv.id)}
                  menuOpen={menuOpenId === conv.id}
                  setMenuOpen={(val) => setMenuOpenId(val ? conv.id : null)}
                />
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

const ConversationItem = ({
  conversation,
  isActive,
  onSelect,
  onPin,
  onFavorite,
  onArchive,
  onDuplicate,
  onDelete,
  menuOpen,
  setMenuOpen,
}) => {
  return (
    <div
      onClick={onSelect}
      className={`group relative flex items-center justify-between p-2.5 rounded-xl cursor-pointer transition-all border ${
        isActive
          ? 'bg-blue-600/15 border-blue-500/30 text-blue-100 shadow-sm'
          : 'border-transparent hover:bg-slate-800/60 text-slate-300 hover:text-slate-100'
      }`}
    >
      <div className="flex items-center gap-2.5 min-w-0 flex-1 pr-2">
        <MessageSquare
          className={`w-4 h-4 flex-shrink-0 ${isActive ? 'text-blue-400' : 'text-slate-400'}`}
        />
        <div className="min-w-0 flex-1">
          <p className="text-sm font-medium truncate">{conversation.title}</p>
          <span className="text-[11px] text-slate-400 block truncate">
            {conversation.message_count} messages
          </span>
        </div>
      </div>

      {/* Badges & Actions */}
      <div className="flex items-center gap-1 opacity-80 group-hover:opacity-100">
        {conversation.is_favorite && (
          <Star className="w-3.5 h-3.5 text-amber-400 fill-amber-400" />
        )}
        <div className="relative">
          <button
            onClick={(e) => {
              e.stopPropagation();
              setMenuOpen(!menuOpen);
            }}
            className="p-1 rounded-md text-slate-400 hover:text-slate-200 hover:bg-slate-700/50"
          >
            <MoreVertical className="w-4 h-4" />
          </button>

          {/* Context Dropdown */}
          {menuOpen && (
            <div
              onClick={(e) => e.stopPropagation()}
              className="absolute right-0 top-6 w-44 bg-slate-800 border border-slate-700/80 rounded-xl shadow-2xl z-50 py-1.5 text-xs text-slate-200 animate-in fade-in zoom-in-95 duration-100"
            >
              <button
                onClick={() => { setMenuOpen(false); onPin(); }}
                className="w-full px-3 py-1.5 flex items-center gap-2 hover:bg-slate-700/70"
              >
                <Pin className="w-3.5 h-3.5 text-blue-400" />
                <span>{conversation.is_pinned ? 'Unpin Session' : 'Pin to Top'}</span>
              </button>

              <button
                onClick={() => { setMenuOpen(false); onFavorite(); }}
                className="w-full px-3 py-1.5 flex items-center gap-2 hover:bg-slate-700/70"
              >
                <Star className="w-3.5 h-3.5 text-amber-400" />
                <span>{conversation.is_favorite ? 'Unstar Session' : 'Add to Starred'}</span>
              </button>

              <button
                onClick={() => { setMenuOpen(false); onDuplicate(); }}
                className="w-full px-3 py-1.5 flex items-center gap-2 hover:bg-slate-700/70"
              >
                <Copy className="w-3.5 h-3.5 text-slate-400" />
                <span>Duplicate Session</span>
              </button>

              <button
                onClick={() => { setMenuOpen(false); onArchive(); }}
                className="w-full px-3 py-1.5 flex items-center gap-2 hover:bg-slate-700/70 text-slate-300"
              >
                <Archive className="w-3.5 h-3.5 text-slate-400" />
                <span>{conversation.is_archived ? 'Restore Session' : 'Archive Session'}</span>
              </button>

              <div className="my-1 border-t border-slate-700/60" />

              <button
                onClick={() => { setMenuOpen(false); onDelete(); }}
                className="w-full px-3 py-1.5 flex items-center gap-2 hover:bg-red-500/20 text-red-400"
              >
                <Trash2 className="w-3.5 h-3.5 text-red-400" />
                <span>Delete Session</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
