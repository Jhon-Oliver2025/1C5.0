import { useState, useEffect, useCallback } from 'react';

interface PWAInstallPrompt {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>;
}

interface PWACapabilities {
  isInstallable: boolean;
  isInstalled: boolean;
  isStandalone: boolean;
  canInstall: boolean;
  platform: 'ios' | 'android' | 'desktop' | 'unknown';
  supportsNotifications: boolean;
  supportsBackgroundSync: boolean;
  supportsOffline: boolean;
}

interface PWAHook {
  capabilities: PWACapabilities;
  installPrompt: PWAInstallPrompt | null;
  showInstallPrompt: () => Promise<boolean>;
  isOnline: boolean;
  requestNotificationPermission: () => Promise<NotificationPermission>;
  showNotification: (title: string, options?: NotificationOptions) => Promise<void>;
  addToHomeScreen: () => void;
  shareContent: (data: ShareData) => Promise<boolean>;
  vibrate: (pattern: number | number[]) => boolean;
  setStatusBarStyle: (style: 'default' | 'black' | 'black-translucent') => void;
}

/**
 * Hook personalizado para funcionalidades PWA nativas
 * Gerencia instalação, notificações, compartilhamento e outras APIs nativas
 */
export const usePWA = (): PWAHook => {
  const [installPrompt, setInstallPrompt] = useState<PWAInstallPrompt | null>(null);
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [capabilities, setCapabilities] = useState<PWACapabilities>({
    isInstallable: false,
    isInstalled: false,
    isStandalone: false,
    canInstall: false,
    platform: 'unknown',
    supportsNotifications: 'Notification' in window,
    supportsBackgroundSync: 'serviceWorker' in navigator && 'sync' in window.ServiceWorkerRegistration.prototype,
    supportsOffline: 'serviceWorker' in navigator
  });

  // Detectar plataforma
  const detectPlatform = useCallback((): 'ios' | 'android' | 'desktop' | 'unknown' => {
    const userAgent = navigator.userAgent.toLowerCase();
    
    if (/iphone|ipad|ipod/.test(userAgent)) {
      return 'ios';
    }
    
    if (/android/.test(userAgent)) {
      return 'android';
    }
    
    if (/windows|macintosh|linux/.test(userAgent)) {
      return 'desktop';
    }
    
    return 'unknown';
  }, []);

  // Verificar se está instalado
  const checkIfInstalled = useCallback((): boolean => {
    // Verificar display mode
    if (window.matchMedia('(display-mode: standalone)').matches) {
      return true;
    }
    
    // Verificar se está no iOS Safari em modo standalone
    if ((window.navigator as any).standalone === true) {
      return true;
    }
    
    // Verificar se foi adicionado à tela inicial no Android
    if (window.matchMedia('(display-mode: minimal-ui)').matches) {
      return true;
    }
    
    return false;
  }, []);

  // Verificar se está em modo standalone
  const checkIfStandalone = useCallback((): boolean => {
    return window.matchMedia('(display-mode: standalone)').matches ||
           (window.navigator as any).standalone === true;
  }, []);

  // Inicializar capacidades
  useEffect(() => {
    const platform = detectPlatform();
    const isInstalled = checkIfInstalled();
    const isStandalone = checkIfStandalone();
    
    setCapabilities(prev => ({
      ...prev,
      platform,
      isInstalled,
      isStandalone,
      canInstall: !isInstalled && platform !== 'unknown'
    }));
  }, [detectPlatform, checkIfInstalled, checkIfStandalone]);

  // Listener para evento de instalação
  useEffect(() => {
    const handleBeforeInstallPrompt = (e: Event) => {
      e.preventDefault();
      setInstallPrompt(e as any);
      setCapabilities(prev => ({ ...prev, isInstallable: true, canInstall: true }));
    };

    const handleAppInstalled = () => {
      setInstallPrompt(null);
      setCapabilities(prev => ({ 
        ...prev, 
        isInstalled: true, 
        isInstallable: false,
        canInstall: false 
      }));
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    window.addEventListener('appinstalled', handleAppInstalled);

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
      window.removeEventListener('appinstalled', handleAppInstalled);
    };
  }, []);

  // Listener para status online/offline
  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // Mostrar prompt de instalação
  const showInstallPrompt = useCallback(async (): Promise<boolean> => {
    if (!installPrompt) {
      return false;
    }

    try {
      await installPrompt.prompt();
      const choiceResult = await installPrompt.userChoice;
      
      if (choiceResult.outcome === 'accepted') {
        setInstallPrompt(null);
        return true;
      }
      
      return false;
    } catch (error) {
      console.error('Erro ao mostrar prompt de instalação:', error);
      return false;
    }
  }, [installPrompt]);

  // Solicitar permissão para notificações
  const requestNotificationPermission = useCallback(async (): Promise<NotificationPermission> => {
    if (!('Notification' in window)) {
      return 'denied';
    }

    if (Notification.permission === 'granted') {
      return 'granted';
    }

    if (Notification.permission === 'denied') {
      return 'denied';
    }

    try {
      const permission = await Notification.requestPermission();
      return permission;
    } catch (error) {
      console.error('Erro ao solicitar permissão de notificação:', error);
      return 'denied';
    }
  }, []);

  // Mostrar notificação
  const showNotification = useCallback(async (title: string, options?: NotificationOptions): Promise<void> => {
    if (!('Notification' in window)) {
      throw new Error('Notificações não são suportadas');
    }

    if (Notification.permission !== 'granted') {
      const permission = await requestNotificationPermission();
      if (permission !== 'granted') {
        throw new Error('Permissão de notificação negada');
      }
    }

    const defaultOptions: NotificationOptions = {
      icon: '/logo3.png',
      badge: '/icons/icon-96x96.png',
      tag: '1crypten-notification',
      renotify: true,
      requireInteraction: false,
      silent: false,
      ...options
    };

    new Notification(title, defaultOptions);
  }, [requestNotificationPermission]);

  // Adicionar à tela inicial (iOS)
  const addToHomeScreen = useCallback((): void => {
    if (capabilities.platform === 'ios' && !capabilities.isInstalled) {
      // Para iOS, mostrar instruções
      alert('Para instalar o app:\n1. Toque no ícone de compartilhar\n2. Selecione "Adicionar à Tela de Início"');
    } else if (installPrompt) {
      showInstallPrompt();
    }
  }, [capabilities.platform, capabilities.isInstalled, installPrompt, showInstallPrompt]);

  // Compartilhar conteúdo
  const shareContent = useCallback(async (data: ShareData): Promise<boolean> => {
    if (!('share' in navigator)) {
      // Fallback para clipboard
      if ('clipboard' in navigator && data.url) {
        try {
          await navigator.clipboard.writeText(data.url);
          return true;
        } catch (error) {
          console.error('Erro ao copiar para clipboard:', error);
          return false;
        }
      }
      return false;
    }

    try {
      await (navigator as any).share(data);
      return true;
    } catch (error) {
      console.error('Erro ao compartilhar:', error);
      return false;
    }
  }, []);

  // Vibrar dispositivo
  const vibrate = useCallback((pattern: number | number[]): boolean => {
    if (!('vibrate' in navigator)) {
      return false;
    }

    try {
      navigator.vibrate(pattern);
      return true;
    } catch (error) {
      console.error('Erro ao vibrar:', error);
      return false;
    }
  }, []);

  // Definir estilo da barra de status (iOS)
  const setStatusBarStyle = useCallback((style: 'default' | 'black' | 'black-translucent'): void => {
    const metaTag = document.querySelector('meta[name="apple-mobile-web-app-status-bar-style"]');
    if (metaTag) {
      metaTag.setAttribute('content', style);
    }
  }, []);

  return {
    capabilities,
    installPrompt,
    showInstallPrompt,
    isOnline,
    requestNotificationPermission,
    showNotification,
    addToHomeScreen,
    shareContent,
    vibrate,
    setStatusBarStyle
  };
};

export default usePWA;