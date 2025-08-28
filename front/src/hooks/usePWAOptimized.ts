import { useState, useEffect, useCallback } from 'react';
import { Workbox } from 'workbox-window';

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
  hasBeforeInstallPrompt: boolean;
}

interface PWAHookOptimized {
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
  workboxReady: boolean;
}

/**
 * Hook PWA otimizado com Workbox e melhores práticas
 * Baseado em pesquisa de frameworks e bibliotecas PWA 2024
 */
export const usePWAOptimized = (): PWAHookOptimized => {
  const [installPrompt, setInstallPrompt] = useState<PWAInstallPrompt | null>(null);
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [workboxReady, setWorkboxReady] = useState(false);
  const [capabilities, setCapabilities] = useState<PWACapabilities>({
    isInstallable: false,
    isInstalled: false,
    isStandalone: false,
    canInstall: false,
    platform: 'unknown',
    supportsNotifications: 'Notification' in window,
    supportsBackgroundSync: 'serviceWorker' in navigator && 'sync' in window.ServiceWorkerRegistration.prototype,
    supportsOffline: 'serviceWorker' in navigator,
    hasBeforeInstallPrompt: false
  });

  // Detectar plataforma com maior precisão
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

  // Verificar se está instalado com múltiplas verificações
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
    
    // Verificar se está rodando como TWA (Trusted Web Activity)
    if (document.referrer.startsWith('android-app://')) {
      return true;
    }
    
    return false;
  }, []);

  // Verificar se está em modo standalone
  const checkIfStandalone = useCallback((): boolean => {
    return window.matchMedia('(display-mode: standalone)').matches ||
           (window.navigator as any).standalone === true;
  }, []);

  // Verificar critérios PWA rigorosos baseados na pesquisa
  const checkPWAInstallability = useCallback(async (): Promise<boolean> => {
    try {
      // Verificar se Service Worker está registrado
      if (!('serviceWorker' in navigator)) {
        console.log('❌ Service Worker não suportado');
        return false;
      }
      
      const registration = await navigator.serviceWorker.getRegistration();
      if (!registration) {
        console.log('❌ Service Worker não registrado');
        return false;
      }
      
      // Verificar se manifest existe e é válido
      const manifestLink = document.querySelector('link[rel="manifest"]') as HTMLLinkElement;
      if (!manifestLink) {
        console.log('❌ Manifest não encontrado');
        return false;
      }
      
      try {
        const response = await fetch(manifestLink.href);
        const manifest = await response.json();
        
        // Verificar propriedades essenciais do manifest
        const requiredFields = ['name', 'start_url', 'display', 'icons'];
        const missingFields = requiredFields.filter(field => !manifest[field]);
        
        if (missingFields.length > 0) {
          console.log(`❌ Manifest inválido - campos faltando: ${missingFields.join(', ')}`);
          return false;
        }
        
        // Verificar se tem ícones adequados (192px e 512px obrigatórios)
        const hasValidIcons = manifest.icons.some((icon: any) => 
          icon.sizes && (icon.sizes.includes('192x192') || icon.sizes.includes('512x512'))
        );
        
        if (!hasValidIcons) {
          console.log('❌ Ícones PWA inválidos - necessário 192x192 e 512x512');
          return false;
        }
        
        console.log('✅ PWA critérios atendidos');
        return true;
      } catch (error) {
        console.log('❌ Erro ao validar manifest:', error);
        return false;
      }
    } catch (error) {
      console.log('❌ Erro na verificação PWA:', error);
      return false;
    }
  }, []);

  // Inicializar Workbox
  useEffect(() => {
    if ('serviceWorker' in navigator) {
      const wb = new Workbox('/sw.js');
      
      wb.addEventListener('installed', (event) => {
        console.log('✅ Workbox Service Worker instalado');
        setWorkboxReady(true);
      });
      
      wb.addEventListener('waiting', (event) => {
        console.log('🔄 Nova versão do Service Worker disponível');
        // Mostrar notificação de atualização
      });
      
      wb.addEventListener('controlling', (event) => {
        console.log('🎯 Service Worker assumiu controle');
        window.location.reload();
      });
      
      wb.register();
    }
  }, []);

  // Inicializar capacidades com verificações rigorosas
  useEffect(() => {
    const initializeCapabilities = async () => {
      const platform = detectPlatform();
      const isInstalled = checkIfInstalled();
      const isStandalone = checkIfStandalone();
      const isPWAInstallable = await checkPWAInstallability();
      
      setCapabilities(prev => ({
        ...prev,
        platform,
        isInstalled,
        isStandalone,
        canInstall: !isInstalled && isPWAInstallable
      }));
    };
    
    initializeCapabilities();
  }, [detectPlatform, checkIfInstalled, checkIfStandalone, checkPWAInstallability]);

  // Listener otimizado para beforeinstallprompt com timeout
  useEffect(() => {
    let timeoutId: NodeJS.Timeout;
    
    const handleBeforeInstallPrompt = (e: Event) => {
      console.log('🎯 beforeinstallprompt disparado!');
      e.preventDefault();
      setInstallPrompt(e as any);
      setCapabilities(prev => ({ 
        ...prev, 
        isInstallable: true, 
        canInstall: true,
        hasBeforeInstallPrompt: true
      }));
    };

    const handleAppInstalled = () => {
      console.log('✅ App instalado!');
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

    // Timeout para detectar se beforeinstallprompt não foi disparado
    timeoutId = setTimeout(() => {
      if (!capabilities.hasBeforeInstallPrompt) {
        console.log('⚠️ beforeinstallprompt não disparado após 10s - possível problema PWA');
        setCapabilities(prev => ({ 
          ...prev, 
          canInstall: prev.platform === 'android' // Forçar para Android
        }));
      }
    }, 10000);

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
      window.removeEventListener('appinstalled', handleAppInstalled);
      clearTimeout(timeoutId);
    };
  }, [capabilities.hasBeforeInstallPrompt]);

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

  // Função otimizada para mostrar prompt de instalação
  const showInstallPrompt = useCallback(async (): Promise<boolean> => {
    const platform = detectPlatform();
    
    if (installPrompt) {
      try {
        console.log('🚀 Disparando prompt nativo de instalação');
        await installPrompt.prompt();
        const choiceResult = await installPrompt.userChoice;
        
        if (choiceResult.outcome === 'accepted') {
          console.log('✅ Usuário aceitou instalação');
          setInstallPrompt(null);
          return true;
        } else {
          console.log('❌ Usuário rejeitou instalação');
        }
        
        return false;
      } catch (error) {
        console.error('❌ Erro ao mostrar prompt de instalação:', error);
        addToHomeScreen();
        return false;
      }
    } else {
      console.log('⚠️ Prompt nativo não disponível - usando fallback');
      addToHomeScreen();
      return false;
    }
  }, [installPrompt, detectPlatform]);

  // Função melhorada para adicionar à tela inicial
  const addToHomeScreen = useCallback((): void => {
    const userAgent = navigator.userAgent.toLowerCase();
    const isIOS = /iphone|ipad|ipod/.test(userAgent);
    const isAndroid = /android/.test(userAgent);
    const isChrome = /chrome/.test(userAgent);
    const isSafari = /safari/.test(userAgent) && !/chrome/.test(userAgent);
    
    let instructions = '';
    
    if (isIOS && isSafari) {
      instructions = `Para instalar o 1Crypten no iOS:

1. Toque no ícone de compartilhar (□↗) na barra inferior
2. Role para baixo e toque em "Adicionar à Tela de Início"
3. Toque em "Adicionar" para confirmar

✅ O app aparecerá como ícone nativo na sua tela inicial!`;
    } else if (isAndroid && isChrome) {
      instructions = `Para instalar o 1Crypten no Android:

1. Toque nos 3 pontos (⋮) no canto superior direito do Chrome
2. Procure por "Instalar app" (não "Adicionar à tela inicial")
3. Se aparecer "Instalar app", toque nele
4. Confirme a instalação

⚠️ Se só aparecer "Adicionar à tela inicial":
- Aguarde 30 segundos na página
- Recarregue a página
- Verifique se todos os critérios PWA estão atendidos

✅ O app aparecerá como ícone nativo no seu dispositivo!`;
    } else if (isChrome) {
      instructions = `Para instalar o 1Crypten:

1. Procure o ícone de instalação na barra de endereços
2. Ou toque nos 3 pontos e selecione "Instalar"
3. Confirme a instalação

✅ O app aparecerá como aplicativo nativo!`;
    } else {
      instructions = `Para instalar o 1Crypten:

1. Procure a opção "Instalar app" no menu do navegador
2. Ou "Adicionar à tela inicial"
3. Confirme a instalação

✅ O app aparecerá na sua tela inicial!`;
    }
    
    // Criar modal otimizado com melhor UX
    const modal = document.createElement('div');
    modal.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      background: rgba(0, 0, 0, 0.95);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 10000;
      padding: 20px;
      box-sizing: border-box;
      backdrop-filter: blur(10px);
    `;
    
    modal.innerHTML = `
      <div style="
        background: linear-gradient(135deg, #1a1a1a, #2d2d2d);
        border-radius: 20px;
        padding: 32px;
        max-width: 420px;
        width: 100%;
        color: white;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        box-shadow: 0 25px 80px rgba(0, 0, 0, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.1);
        text-align: center;
      ">
        <div style="font-size: 64px; margin-bottom: 16px;">📱</div>
        <h2 style="margin: 0 0 16px 0; color: #646cff; font-size: 28px; font-weight: 700;">Instalar 1Crypten</h2>
        <p style="margin: 0 0 24px 0; color: #ccc; font-size: 16px; line-height: 1.5;">Instale como app nativo para melhor experiência!</p>
        <div style="
          background: rgba(255, 255, 255, 0.05);
          border-radius: 12px;
          padding: 20px;
          margin-bottom: 24px;
          text-align: left;
          font-size: 14px;
          line-height: 1.6;
          white-space: pre-line;
        ">${instructions}</div>
        <button onclick="this.parentElement.parentElement.remove()" style="
          background: linear-gradient(135deg, #646cff, #4ade80);
          border: none;
          border-radius: 12px;
          color: white;
          padding: 16px 32px;
          font-size: 16px;
          font-weight: 600;
          cursor: pointer;
          width: 100%;
          transition: all 0.3s ease;
        " onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">Entendi</button>
      </div>
    `;
    
    document.body.appendChild(modal);
    
    // Auto-remover após 30 segundos
    setTimeout(() => {
      if (document.body.contains(modal)) {
        modal.remove();
      }
    }, 30000);
  }, []);

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

    const permission = await Notification.requestPermission();
    return permission;
  }, []);

  // Mostrar notificação
  const showNotification = useCallback(async (title: string, options?: NotificationOptions): Promise<void> => {
    const permission = await requestNotificationPermission();
    
    if (permission === 'granted') {
      const defaultOptions: NotificationOptions = {
        icon: '/icons/icon-192x192.png',
        badge: '/icons/icon-72x72.png',
        vibrate: [200, 100, 200],
        ...options
      };
      
      new Notification(title, defaultOptions);
    }
  }, [requestNotificationPermission]);

  // Compartilhar conteúdo
  const shareContent = useCallback(async (data: ShareData): Promise<boolean> => {
    if (navigator.share) {
      try {
        await navigator.share(data);
        return true;
      } catch (error) {
        console.error('Erro ao compartilhar:', error);
      }
    }
    
    // Fallback para clipboard
    if (navigator.clipboard && data.url) {
      try {
        await navigator.clipboard.writeText(data.url);
        await showNotification('Link copiado!', {
          body: 'O link foi copiado para a área de transferência'
        });
        return true;
      } catch (error) {
        console.error('Erro ao copiar para clipboard:', error);
      }
    }
    
    return false;
  }, [showNotification]);

  // Vibrar dispositivo
  const vibrate = useCallback((pattern: number | number[]): boolean => {
    if (navigator.vibrate) {
      navigator.vibrate(pattern);
      return true;
    }
    return false;
  }, []);

  // Definir estilo da barra de status
  const setStatusBarStyle = useCallback((style: 'default' | 'black' | 'black-translucent'): void => {
    const metaTag = document.querySelector('meta[name="apple-mobile-web-app-status-bar-style"]') as HTMLMetaElement;
    if (metaTag) {
      metaTag.content = style;
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
    setStatusBarStyle,
    workboxReady
  };
};

export default usePWAOptimized;