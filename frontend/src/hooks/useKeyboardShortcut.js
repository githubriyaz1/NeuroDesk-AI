import { useEffect } from 'react';

/**
 * Custom hook binding keydown shortcut handlers with modifier keys.
 */
export const useKeyboardShortcut = (targetKey, callback, modifierKey = 'ctrlKey') => {
  useEffect(() => {
    const handleKeyDown = (event) => {
      const isModifierActive = modifierKey ? event[modifierKey] || event.metaKey : true;
      if (isModifierActive && event.key.toLowerCase() === targetKey.toLowerCase()) {
        event.preventDefault();
        callback(event);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [targetKey, callback, modifierKey]);
};
