import React, { createContext, useState, useEffect } from 'react';
import { authService } from '../services/authService';

export const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  // Restore authenticated session on page load
  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('neurodesk_token');
      if (token) {
        try {
          const meData = await authService.getMe();
          setUser(meData);
          setIsAuthenticated(true);
        } catch (err) {
          console.warn('Session restoration failed:', err);
          localStorage.removeItem('neurodesk_token');
          localStorage.removeItem('neurodesk_refresh_token');
          setUser(null);
          setIsAuthenticated(false);
        }
      }
      setLoading(false);
    };
    initAuth();
  }, []);

  const login = async (email, password) => {
    const data = await authService.login(email, password);
    setUser(data.user);
    setIsAuthenticated(true);
    return data;
  };

  const register = async (userData) => {
    return await authService.register(userData);
  };

  const logout = async () => {
    await authService.logout();
    setUser(null);
    setIsAuthenticated(false);
  };

  const updateProfile = async (profileData) => {
    const updatedUser = await authService.updateProfile(profileData);
    setUser(updatedUser);
    return updatedUser;
  };

  const changePassword = async (passwords) => {
    return await authService.changePassword(passwords);
  };

  const deleteAccount = async () => {
    await authService.deleteAccount();
    setUser(null);
    setIsAuthenticated(false);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated,
        loading,
        login,
        register,
        logout,
        updateProfile,
        changePassword,
        deleteAccount,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
