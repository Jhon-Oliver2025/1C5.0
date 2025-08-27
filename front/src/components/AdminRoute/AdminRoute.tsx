import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useAdminCheck } from '../../hooks/useAdminCheck';

interface AdminRouteProps {
  children: React.ReactNode;
}

/**
 * Componente para proteger rotas que requerem privilégios de administrador
 * Redireciona para dashboard se o usuário não for admin
 */
const AdminRoute: React.FC<AdminRouteProps> = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  const { isAdmin, isLoading: adminLoading } = useAdminCheck();

  // Mostrar loading enquanto verifica autenticação e permissões de admin
  if (loading || adminLoading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        fontSize: '18px',
        color: '#666'
      }}>
        🔐 Verificando permissões de administrador...
      </div>
    );
  }

  // Se não estiver autenticado, redirecionar para login
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Se estiver autenticado mas não for admin, redirecionar para dashboard
  if (!isAdmin) {
    return <Navigate to="/dashboard" replace />;
  }

  // Se for admin, renderizar o conteúdo
  return <>{children}</>;
};

export default AdminRoute;