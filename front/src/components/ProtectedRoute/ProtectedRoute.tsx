// Componente de rota protegida melhorado para evitar loops de redirecionamento
import React, { useEffect, useRef } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import NavigationFix from '../../utils/navigationFix';

interface ProtectedRouteProps {
  children: React.ReactNode;
  redirectTo?: string;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ 
  children, 
  redirectTo = '/login' 
}) => {
  const { isAuthenticated, loading } = useAuth();
  const location = useLocation();
  const hasRedirected = useRef(false);

  useEffect(() => {
    // Reset flag quando a localização muda
    hasRedirected.current = false;
    NavigationFix.reset();
  }, [location.pathname]);

  // Mostrar loading enquanto verifica autenticação
  if (loading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        fontSize: '18px'
      }}>
        ⏳ Verificando autenticação...
      </div>
    );
  }

  // Se não autenticado e ainda não redirecionou
  if (!isAuthenticated && !hasRedirected.current) {
    console.log(`🔒 ProtectedRoute: Usuário não autenticado, redirecionando para ${redirectTo}`);
    hasRedirected.current = true;
    
    return (
      <Navigate 
        to={redirectTo} 
        state={{ from: location.pathname }} 
        replace 
      />
    );
  }

  // Se autenticado, mostrar conteúdo
  if (isAuthenticated) {
    console.log('✅ ProtectedRoute: Usuário autenticado, mostrando conteúdo');
    return <>{children}</>;
  }

  // Fallback - não deveria chegar aqui
  return null;
};

export default ProtectedRoute;