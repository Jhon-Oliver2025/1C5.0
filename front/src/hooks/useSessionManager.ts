import { useState, useEffect, useCallback } from 'react';
import { useAuthManager } from './useAuthManager';

export const useSessionManager = () => {
  const [isAuth, setIsAuth] = useState<boolean | null>(null);
  const authManager = useAuthManager();

  const checkAuth = useCallback(async () => {
    const token = authManager.getToken();
    if (token) {
      const isValid = await authManager.validateToken();
      setIsAuth(isValid);
    } else {
      setIsAuth(false);
    }
  }, [authManager]);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  const login = async (email: string, password: string) => {
    const success = await authManager.login(email, password);
    setIsAuth(success);
    return success;
  };

  const logout = async () => {
    await authManager.logout();
    setIsAuth(false);
  };

  return { isAuth, login, logout, checkAuth };
};