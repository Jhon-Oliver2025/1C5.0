import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { debugPWAInstallability, checkDeviceSupport } from '../../utils/pwaChecker';

/**
 * Interface para o evento beforeinstallprompt
 */
interface BeforeInstallPromptEvent extends Event {
  prompt(): Promise<void>;
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>;
}

/**
 * Componente de botão para instalação do PWA
 * Implementa o fluxo completo de instalação personalizada
 */
const PWAInstallButton: React.FC = () => {
  const [deferredPrompt, setDeferredPrompt] = useState<BeforeInstallPromptEvent | null>(null);
  const [isInstallable, setIsInstallable] = useState(false);
  const [isInstalled, setIsInstalled] = useState(false);

  /**
   * Verifica se o PWA já está instalado
   */
  const checkIfInstalled = () => {
    // Verifica se está rodando como PWA
    const isStandalone = window.matchMedia('(display-mode: standalone)').matches;
    const isInWebAppiOS = (window.navigator as any).standalone === true;
    const isInWebAppChrome = window.matchMedia('(display-mode: minimal-ui)').matches;
    
    return isStandalone || isInWebAppiOS || isInWebAppChrome;
  };

  useEffect(() => {
    // Verificar se já está instalado
    setIsInstalled(checkIfInstalled());

    // Diagnosticar PWA
    const initPWACheck = async () => {
      const deviceSupport = checkDeviceSupport();
      console.log('📱 Device Support:', deviceSupport);
      
      // Executar diagnóstico completo
      await debugPWAInstallability();
    };
    
    initPWACheck();

    /**
     * Captura o evento beforeinstallprompt
     */
    const handleBeforeInstallPrompt = (e: Event) => {
      console.log('📱 PWA: Evento beforeinstallprompt capturado');
      e.preventDefault();
      setDeferredPrompt(e as BeforeInstallPromptEvent);
      setIsInstallable(true);
    };

    /**
     * Detecta quando o PWA foi instalado
     */
    const handleAppInstalled = () => {
      console.log('✅ PWA: Aplicativo instalado com sucesso!');
      setIsInstalled(true);
      setIsInstallable(false);
      setDeferredPrompt(null);
    };

    // Adicionar listeners
    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    window.addEventListener('appinstalled', handleAppInstalled);

    // Timeout para mostrar botão mesmo sem evento (fallback)
    const fallbackTimer = setTimeout(() => {
      if (!deferredPrompt && !isInstalled) {
        console.log('⚠️ PWA: Evento beforeinstallprompt não capturado, usando fallback');
        setIsInstallable(true);
      }
    }, 3000);

    // Cleanup
    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
      window.removeEventListener('appinstalled', handleAppInstalled);
      clearTimeout(fallbackTimer);
    };
  }, []);

  /**
   * Função para instalar o PWA
   */
  const handleInstallClick = async () => {
    if (!deferredPrompt) {
      console.warn('⚠️ PWA: Prompt de instalação não disponível');
      return;
    }

    try {
      // Mostrar o prompt de instalação
      await deferredPrompt.prompt();
      
      // Aguardar a escolha do usuário
      const { outcome } = await deferredPrompt.userChoice;
      
      console.log(`🎯 PWA: Usuário ${outcome === 'accepted' ? 'aceitou' : 'rejeitou'} a instalação`);
      
      if (outcome === 'accepted') {
        setIsInstalled(true);
      }
      
      // Limpar o prompt
      setDeferredPrompt(null);
      setIsInstallable(false);
    } catch (error) {
      console.error('❌ PWA: Erro ao instalar:', error);
    }
  };

  // Não mostrar se já estiver instalado
  if (isInstalled) {
    return (
      <InstalledMessage>
        ✅ App instalado com sucesso!
      </InstalledMessage>
    );
  }

  // Não mostrar se não for instalável
  if (!isInstallable) {
    return null;
  }

  return (
    <InstallContainer>
      <InstallButton onClick={handleInstallClick}>
        <InstallIcon>📱</InstallIcon>
        <InstallText>
          <InstallTitle>Instalar 1Crypten</InstallTitle>
          <InstallSubtitle>Acesso rápido como app nativo</InstallSubtitle>
        </InstallText>
      </InstallButton>
    </InstallContainer>
  );
};

// Styled Components
const InstallContainer = styled.div`
  margin: 16px 0;
`;

const InstallButton = styled.button`
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 16px;
  background: linear-gradient(135deg, #646cff 0%, #747bff 100%);
  border: none;
  border-radius: 12px;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(100, 108, 255, 0.3);
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(100, 108, 255, 0.4);
  }
  
  &:active {
    transform: translateY(0);
  }
`;

const InstallIcon = styled.div`
  font-size: 24px;
  flex-shrink: 0;
`;

const InstallText = styled.div`
  text-align: left;
  flex: 1;
`;

const InstallTitle = styled.div`
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 4px;
`;

const InstallSubtitle = styled.div`
  font-size: 14px;
  opacity: 0.9;
`;

const InstalledMessage = styled.div`
  padding: 12px 16px;
  background: #10b981;
  color: white;
  border-radius: 8px;
  text-align: center;
  font-weight: 500;
  margin: 16px 0;
`;

export default PWAInstallButton;