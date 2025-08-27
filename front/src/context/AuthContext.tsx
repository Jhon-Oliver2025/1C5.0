// Correção para AuthContext - Persistência de Token
// Este arquivo contém as correções necessárias para resolver o problema de logout automático

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface User {
  id: string;
  email: string;
  name?: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  loading: boolean;
  login: (email: string, password: string) => Promise<{ success: boolean; error?: string }>;
  logout: () => void;
  apiCall: (url: string, options?: RequestInit) => Promise<Response>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  // Função para salvar dados de autenticação
  const saveAuthData = (tokenData: string, userData: User) => {
    try {
      localStorage.setItem('auth_token', tokenData);
      localStorage.setItem('user_data', JSON.stringify(userData));
      localStorage.setItem('auth_timestamp', Date.now().toString());
      
      setToken(tokenData);
      setUser(userData);
      setIsAuthenticated(true);
      
      console.log('✅ Auth: Dados salvos no localStorage');
    } catch (error) {
      console.error('❌ Auth: Erro ao salvar dados:', error);
    }
  };

  // Função para limpar dados de autenticação
  const clearAuthData = () => {
    try {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user_data');
      localStorage.removeItem('auth_timestamp');
      
      setToken(null);
      setUser(null);
      setIsAuthenticated(false);
      
      console.log('🔐 Auth: Logout realizado');
    } catch (error) {
      console.error('❌ Auth: Erro ao limpar dados:', error);
    }
  };

  // Função para verificar se o token ainda é válido (24 horas)
  const isTokenValid = () => {
    try {
      const timestamp = localStorage.getItem('auth_timestamp');
      if (!timestamp) return false;
      
      const tokenAge = Date.now() - parseInt(timestamp);
      const maxAge = 24 * 60 * 60 * 1000; // 24 horas
      
      return tokenAge < maxAge;
    } catch {
      return false;
    }
  };

  // Função de login
  const login = async (email: string, password: string): Promise<{ success: boolean; error?: string }> => {
    try {
      console.log('🔐 Auth: Iniciando login...');
      
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      if (response.ok) {
        const data = await response.json();
        console.log('📥 Auth: Resposta do login:', data);
        
        // Verificar se recebemos um token
        const receivedToken = data.token || data.access_token;
        
        if (receivedToken) {
          // Criar objeto de usuário
          const userData: User = {
            id: data.user?.id || 'unknown',
            email: data.user?.email || email,
            name: data.user?.name || data.user?.email?.split('@')[0]
          };
          
          // Salvar dados de autenticação
          saveAuthData(receivedToken, userData);
          
          console.log('✅ Auth: Login realizado com sucesso');
          return { success: true };
        } else {
          console.error('❌ Auth: Token não encontrado na resposta');
          return { success: false, error: 'Token não recebido do servidor' };
        }
      } else {
        const errorData = await response.json().catch(() => ({ error: 'Erro desconhecido' }));
        console.error('❌ Auth: Erro no login:', errorData);
        return { success: false, error: errorData.error || 'Credenciais inválidas' };
      }
    } catch (error) {
      console.error('❌ Auth: Erro de conexão:', error);
      return { success: false, error: 'Erro de conexão com o servidor' };
    }
  };

  // Função de logout
  const logout = () => {
    clearAuthData();
  };

  // Função para fazer chamadas à API com token automático
  const apiCall = async (url: string, options: RequestInit = {}): Promise<Response> => {
    const currentToken = localStorage.getItem('auth_token');
    
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };
    
    if (currentToken && isTokenValid()) {
      headers['Authorization'] = `Bearer ${currentToken}`;
    }
    
    const response = await fetch(url, {
      ...options,
      headers,
    });
    
    // Se recebemos 401, o token pode ter expirado
    if (response.status === 401) {
      console.warn('⚠️ Auth: Token expirado, fazendo logout');
      logout();
    }
    
    return response;
  };

  // Carregar dados salvos na inicialização
  useEffect(() => {
    const loadSavedAuth = () => {
      try {
        const savedToken = localStorage.getItem('auth_token');
        const savedUser = localStorage.getItem('user_data');
        
        if (savedToken && savedUser && isTokenValid()) {
          const userData = JSON.parse(savedUser);
          
          setToken(savedToken);
          setUser(userData);
          setIsAuthenticated(true);
          
          console.log('✅ Auth: Dados restaurados do localStorage');
        } else {
          // Limpar dados inválidos ou expirados
          clearAuthData();
          console.log('🔄 Auth: Dados expirados ou inválidos removidos');
        }
      } catch (error) {
        console.error('❌ Auth: Erro ao carregar dados salvos:', error);
        clearAuthData();
      } finally {
        setLoading(false);
      }
    };

    loadSavedAuth();
  }, []);

  // Verificar periodicamente se o token ainda é válido
  useEffect(() => {
    if (!isAuthenticated) return;
    
    const interval = setInterval(() => {
      if (!isTokenValid()) {
        console.warn('⚠️ Auth: Token expirado, fazendo logout automático');
        logout();
      }
    }, 60000); // Verificar a cada minuto
    
    return () => clearInterval(interval);
  }, [isAuthenticated]);

  const value: AuthContextType = {
    user,
    token,
    isAuthenticated,
    loading,
    login,
    logout,
    apiCall,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthProvider;