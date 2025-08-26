import { useEffect, useCallback, useRef } from 'react';

/**
 * Hook personalizado para gerenciar funcionalidades PWA
 * Resolve problemas de estado quando app volta do background,
 * gerencia reconexão automática e melhora a experiência do usuário
 */
export const usePWAManager = () => {
  const lastActiveTime = useRef<number>(Date.now());
  const reconnectAttempts = useRef<number>(0);
  const maxReconnectAttempts = 3;
  const reconnectDelay = 1000; // 1 segundo

  /**
   * Força atualização da página quando necessário
   */
  const forceRefresh = useCallback(() => {
    console.log('🔄 PWA: Forçando atualização da página...');
    window.location.reload();
  }, []);

  /**
   * Verifica se o token ainda é válido
   */
  const validateToken = useCallback(async (): Promise<boolean> => {
    try {
      const token = localStorage.getItem('token');
      if (!token) return false;

      const response = await fetch('/api/auth/verify-token', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ token })
      });

      if (!response.ok) {
        console.warn('🔐 PWA: Token inválido, removendo...');
        localStorage.removeItem('token');
        return false;
      }

      return true;
    } catch (error) {
      console.warn('🔐 PWA: Erro ao validar token:', error);
      return false;
    }
  }, []);

  /**
   * Tenta reconectar com o servidor
   */
  const attemptReconnect = useCallback(async (): Promise<boolean> => {
    if (reconnectAttempts.current >= maxReconnectAttempts) {
      console.warn('🌐 PWA: Máximo de tentativas de reconexão atingido');
      return false;
    }

    reconnectAttempts.current++;
    console.log(`🌐 PWA: Tentativa de reconexão ${reconnectAttempts.current}/${maxReconnectAttempts}`);

    try {
      const response = await fetch('/api/health', {
        method: 'GET',
        cache: 'no-cache'
      });

      if (response.ok) {
        console.log('✅ PWA: Reconexão bem-sucedida');
        reconnectAttempts.current = 0;
        return true;
      }
    } catch (error) {
      console.warn('🌐 PWA: Falha na reconexão:', error);
    }

    // Aguardar antes da próxima tentativa
    await new Promise(resolve => setTimeout(resolve, reconnectDelay * reconnectAttempts.current));
    return false;
  }, []);

  /**
   * Gerencia quando o app volta do background
   */
  const handleVisibilityChange = useCallback(async () => {
    if (document.visibilityState === 'visible') {
      const timeAway = Date.now() - lastActiveTime.current;
      console.log(`👁️ PWA: App voltou do background após ${Math.round(timeAway / 1000)}s`);

      // Se ficou mais de 30 segundos em background
      if (timeAway > 30000) {
        console.log('🔄 PWA: App ficou muito tempo em background, validando estado...');
        
        // Verificar conectividade
        if (navigator.onLine) {
          // Tentar reconectar
          const reconnected = await attemptReconnect();
          
          if (reconnected) {
            // Validar token se estiver logado
            const token = localStorage.getItem('token');
            if (token) {
              const tokenValid = await validateToken();
              if (!tokenValid) {
                console.log('🔐 PWA: Token expirado, redirecionando para login...');
                window.location.href = '/login';
                return;
              }
            }

            // Atualizar dados da página atual
            const event = new CustomEvent('pwa-refresh-data');
            window.dispatchEvent(event);
          } else {
            console.warn('🌐 PWA: Não foi possível reconectar, modo offline');
          }
        } else {
          console.warn('📱 PWA: Dispositivo offline');
        }
      }
    } else {
      lastActiveTime.current = Date.now();
      console.log('👁️ PWA: App foi para background');
    }
  }, [attemptReconnect, validateToken]);

  /**
   * Gerencia mudanças no status de conectividade
   */
  const handleOnlineStatusChange = useCallback(async () => {
    if (navigator.onLine) {
      console.log('🌐 PWA: Conectividade restaurada');
      
      // Tentar reconectar
      const reconnected = await attemptReconnect();
      if (reconnected) {
        // Disparar evento para atualizar dados
        const event = new CustomEvent('pwa-connectivity-restored');
        window.dispatchEvent(event);
      }
    } else {
      console.log('📱 PWA: Dispositivo ficou offline');
      reconnectAttempts.current = 0;
    }
  }, [attemptReconnect]);

  /**
   * Gerencia atualizações do Service Worker
   */
  const handleServiceWorkerUpdate = useCallback(() => {
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.addEventListener('controllerchange', () => {
        console.log('🔄 PWA: Service Worker atualizado, recarregando...');
        window.location.reload();
      });

      // Verificar por atualizações periodicamente
      setInterval(() => {
        navigator.serviceWorker.getRegistration().then(registration => {
          if (registration) {
            registration.update();
          }
        });
      }, 60000); // Verificar a cada minuto
    }
  }, []);

  /**
   * Inicializa o gerenciador PWA
   */
  useEffect(() => {
    console.log('🚀 PWA: Inicializando gerenciador PWA...');

    // Listeners para visibilidade
    document.addEventListener('visibilitychange', handleVisibilityChange);
    
    // Listeners para conectividade
    window.addEventListener('online', handleOnlineStatusChange);
    window.addEventListener('offline', handleOnlineStatusChange);

    // Gerenciar Service Worker
    handleServiceWorkerUpdate();

    // Cleanup
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('online', handleOnlineStatusChange);
      window.removeEventListener('offline', handleOnlineStatusChange);
    };
  }, [handleVisibilityChange, handleOnlineStatusChange, handleServiceWorkerUpdate]);

  return {
    forceRefresh,
    validateToken,
    isOnline: navigator.onLine,
    reconnectAttempts: reconnectAttempts.current
  };
};

export default usePWAManager;