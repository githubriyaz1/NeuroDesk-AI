import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';

export const ActivityContext = createContext();

const STORAGE_KEYS = {
  ACTIVITIES: 'neurodesk_recent_activities',
  FAVORITES: 'neurodesk_favorites',
  RECENTLY_OPENED: 'neurodesk_recently_opened',
  NOTIFICATIONS: 'neurodesk_notifications',
};

const DEFAULT_NOTIFICATIONS = [
  { id: '1', title: 'Workflow Executed', message: 'Document Summarizer pipeline completed.', type: 'success', read: false, time: '10m ago' },
  { id: '2', title: 'Project Blueprint Ready', message: 'Smart Logistics Platform blueprint generated.', type: 'success', read: false, time: '30m ago' },
  { id: '3', title: 'Analysis Completed', message: 'Dataset distribution analysis finished.', type: 'info', read: true, time: '2h ago' },
];

export const ActivityProvider = ({ children }) => {
  const [activities, setActivities] = useState(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEYS.ACTIVITIES);
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });

  const [favorites, setFavorites] = useState(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEYS.FAVORITES);
      return saved ? JSON.parse(saved) : [
        { id: 'fav-1', name: 'Smart Logistics Blueprint', type: 'project', path: '/ai-studio' },
        { id: 'fav-2', name: 'Document Analysis Pipeline', type: 'workflow', path: '/workflows' },
      ];
    } catch {
      return [];
    }
  });

  const [recentlyOpened, setRecentlyOpened] = useState(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEYS.RECENTLY_OPENED);
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });

  const [notifications, setNotifications] = useState(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEYS.NOTIFICATIONS);
      return saved ? JSON.parse(saved) : DEFAULT_NOTIFICATIONS;
    } catch {
      return DEFAULT_NOTIFICATIONS;
    }
  });

  const [isCommandPaletteOpen, setIsCommandPaletteOpen] = useState(false);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEYS.ACTIVITIES, JSON.stringify(activities.slice(0, 50)));
  }, [activities]);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEYS.FAVORITES, JSON.stringify(favorites));
  }, [favorites]);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEYS.RECENTLY_OPENED, JSON.stringify(recentlyOpened.slice(0, 20)));
  }, [recentlyOpened]);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEYS.NOTIFICATIONS, JSON.stringify(notifications));
  }, [notifications]);

  // Handle Ctrl+Shift+P / Cmd+K keyboard shortcut
  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.ctrlKey && e.shiftKey && e.key.toLowerCase() === 'p') || (e.metaKey && e.key.toLowerCase() === 'k') || (e.ctrlKey && e.key.toLowerCase() === 'k')) {
        e.preventDefault();
        setIsCommandPaletteOpen((prev) => !prev);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const trackActivity = useCallback((type, title, path, metadata = {}) => {
    const item = {
      id: Date.now().toString(),
      type,
      title,
      path,
      timestamp: new Date().toISOString(),
      metadata,
    };

    setActivities((prev) => [item, ...prev.filter((a) => a.title !== title)].slice(0, 50));
    setRecentlyOpened((prev) => [item, ...prev.filter((a) => a.title !== title)].slice(0, 20));
  }, []);

  const toggleFavorite = useCallback((item) => {
    setFavorites((prev) => {
      const exists = prev.some((f) => f.name === item.name);
      if (exists) {
        return prev.filter((f) => f.name !== item.name);
      }
      return [{ id: Date.now().toString(), ...item }, ...prev];
    });
  }, []);

  const addNotification = useCallback((title, message, type = 'info') => {
    const notif = {
      id: Date.now().toString(),
      title,
      message,
      type,
      read: false,
      time: 'Just now',
    };
    setNotifications((prev) => [notif, ...prev]);
  }, []);

  const markAllNotificationsRead = useCallback(() => {
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
  }, []);

  const unreadCount = notifications.filter((n) => !n.read).length;

  return (
    <ActivityContext.Provider
      value={{
        activities,
        favorites,
        recentlyOpened,
        notifications,
        unreadCount,
        isCommandPaletteOpen,
        setIsCommandPaletteOpen,
        trackActivity,
        toggleFavorite,
        addNotification,
        markAllNotificationsRead,
      }}
    >
      {children}
    </ActivityContext.Provider>
  );
};

export const useActivity = () => {
  const ctx = useContext(ActivityContext);
  if (!ctx) {
    return {
      activities: [],
      favorites: [],
      recentlyOpened: [],
      notifications: [],
      unreadCount: 0,
      isCommandPaletteOpen: false,
      setIsCommandPaletteOpen: () => {},
      trackActivity: () => {},
      toggleFavorite: () => {},
      addNotification: () => {},
      markAllNotificationsRead: () => {},
    };
  }
  return ctx;
};
