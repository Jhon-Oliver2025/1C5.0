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
    canInstall: false, // Detectar automaticamente
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

  // Verificar se PWA é instalável (versão simplificada)
  const checkPWAInstallability = useCallback((): boolean => {
    // Sempre permitir instalação - deixar o navegador decidir
    return true;
  }, []);

  // Inicializar capacidades (versão simplificada)
  useEffect(() => {
    const platform = detectPlatform();
    const isInstalled = checkIfInstalled();
    const isStandalone = checkIfStandalone();
    
    setCapabilities(prev => ({
       ...prev,
       platform,
       isInstalled,
       isStandalone,
       canInstall: true // Sempre permitir instalação
    }));
  }, [detectPlatform, checkIfInstalled, checkIfStandalone]);

  // Registrar Service Worker simples
  useEffect(() => {
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('/sw.js')
        .then(registration => {
          console.log('✅ Service Worker registrado:', registration);
        })
        .catch(error => {
          console.log('❌ Erro ao registrar Service Worker:', error);
        });
    }
  }, []);

  // Listener para evento de instalação
  useEffect(() => {
    const handleBeforeInstallPrompt = (e: Event) => {
      console.log('🎯 beforeinstallprompt event fired');
      e.preventDefault();
      setInstallPrompt(e as any);
      setCapabilities(prev => ({ ...prev, isInstallable: true }));
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    
    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
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

  // Adicionar à tela inicial (iOS) - movido para antes de showInstallPrompt
  const addToHomeScreen = useCallback((): void => {
    const userAgent = navigator.userAgent.toLowerCase();
    const isIOS = /iphone|ipad|ipod/.test(userAgent);
    const isAndroid = /android/.test(userAgent);
    const isChrome = /chrome/.test(userAgent);
    const isSafari = /safari/.test(userAgent) && !/chrome/.test(userAgent);
    
    let instructions = '';
    
    if (isIOS && isSafari) {
      instructions = 'Para instalar o 1Crypten no iOS:\n\n1. Toque no ícone de compartilhar (□↗) na barra inferior\n2. Role para baixo e toque em "Adicionar à Tela de Início"\n3. Toque em "Adicionar" para confirmar';
    } else if (isAndroid && isChrome) {
      instructions = 'Para instalar o 1Crypten no Android:\n\n1. Toque nos 3 pontos (⋮) no canto superior direito do Chrome\n2. Procure por "Instalar app" ou "Adicionar à tela inicial"\n3. Se não aparecer "Instalar app", selecione "Adicionar à tela inicial"\n4. Confirme a instalação\n\nNota: Aguarde alguns segundos na página para o Chrome reconhecer como app instalável.';
    } else if (isChrome) {
      instructions = 'Para instalar o 1Crypten:\n\n1. Procure o ícone de instalação na barra de endereços\n2. Ou toque nos 3 pontos e selecione "Instalar"\n3. Confirme a instalação';
    } else {
      instructions = 'Para instalar o 1Crypten:\n\n1. Procure a opção "Instalar app" no menu do navegador\n2. Ou "Adicionar à tela inicial"\n3. Confirme a instalação';
    }
    
    // Criar modal personalizado
    const modal = document.createElement('div');
    modal.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      background: rgba(0, 0, 0, 0.9);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 10000;
      padding: 20px;
      box-sizing: border-box;
    `;
    
    modal.innerHTML = `
      <div style="
        background: linear-gradient(135deg, #1a1a1a, #2d2d2d);
        border-radius: 16px;
        padding: 24px;
        max-width: 400px;
        width: 100%;
        color: white;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.1);
      ">
        <div style="text-align: center; margin-bottom: 20px;">
          <div style="font-size: 48px; margin-bottom: 12px;">📱</div>
          <h2 style="margin: 0; color: #64FFDA; font-size: 24px; font-weight: 700;">Instalar 1Crypten</h2>
        </div>
        <p style="margin: 16px 0; line-height: 1.6; white-space: pre-line; color: #e0e0e0; font-size: 14px;">${instructions}</p>
        <button onclick="this.parentElement.parentElement.remove()" style="
          background: linear-gradient(135deg, #646cff, #4ade80);
          color: white;
          border: none;
          padding: 12px 24px;
          border-radius: 8px;
          font-weight: 600;
          cursor: pointer;
          width: 100%;
          font-size: 16px;
          margin-top: 16px;
        ">Entendi</button>
      </div>
    `;
    
    document.body.appendChild(modal);
    
    // Remover modal ao clicar fora
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        modal.remove();
      }
    });
  }, []);

  // Mostrar prompt de instalação
  const showInstallPrompt = useCallback(async (): Promise<boolean> => {
    const platform = detectPlatform();
    
    if (installPrompt) {
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
        // Fallback para instruções manuais
        addToHomeScreen();
        return false;
      }
    } else {
      // Para Android, sempre mostrar instruções mesmo sem prompt nativo
      if (platform === 'android') {
        addToHomeScreen();
        return false;
      }
      
      // Para outras plataformas, mostrar instruções
      addToHomeScreen();
      return false;
    }
  }, [installPrompt, addToHomeScreen, detectPlatform]);

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
      requireInteraction: false,
      silent: false,
      ...options
    };

    new Notification(title, defaultOptions);
  }, [requestNotificationPermission]);

  // Função addToHomeScreen removida (duplicada)

  // Compartilhar conteúdo
  const shareContent = useCallback(async (data: ShareData): Promise<boolean> => {
    if (!('share' in navigator)) {
      // Fallback para clipboard
      if ('clipboard' in navigator && data.url) {
        try {
          await (navigator as any).clipboard.writeText(data.url);
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