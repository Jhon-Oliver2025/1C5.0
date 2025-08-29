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
        const deviceSupport = checkDeviceSupport();
        
        // Mostrar botão se o dispositivo suporta instalação PWA
        if (deviceSupport.supportsInstallation) {
          setIsInstallable(true);
          console.log('📱 PWA: Botão de instalação ativado via fallback para', deviceSupport.platform, deviceSupport.browser);
        } else {
          console.log('⚠️ PWA: Dispositivo não suporta instalação PWA');
        }
      }
    }, 2000); // Reduzido para 2 segundos

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
    const deviceSupport = checkDeviceSupport();
    
    if (deferredPrompt) {
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
    } else {
      // Fallback: mostrar instruções específicas por plataforma
      showInstallInstructions(deviceSupport);
    }
  };
  
  /**
   * Mostra instruções de instalação específicas por plataforma
   */
  const showInstallInstructions = (deviceSupport: any) => {
    let instructions = '';
    
    if (deviceSupport.platform === 'android') {
      if (deviceSupport.browser === 'chrome') {
        instructions = 'No Chrome Android:\n1. Toque no menu (⋮) no canto superior direito\n2. Selecione "Adicionar à tela inicial"\n3. Confirme a instalação';
      } else {
        instructions = 'Para instalar:\n1. Abra este site no Chrome\n2. Toque no menu (⋮)\n3. Selecione "Adicionar à tela inicial"';
      }
    } else if (deviceSupport.platform === 'ios') {
      instructions = 'No Safari iOS:\n1. Toque no botão de compartilhar (□↗)\n2. Role para baixo e toque em "Adicionar à Tela de Início"\n3. Toque em "Adicionar"';
    } else {
      instructions = 'No navegador desktop:\n1. Procure pelo ícone de instalação na barra de endereços\n2. Ou use Ctrl+Shift+A (Chrome)\n3. Ou acesse Menu > Instalar aplicativo';
    }
    
    alert(instructions);
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

  const deviceSupport = checkDeviceSupport();
  const buttonText = deferredPrompt 
    ? 'Instalar 1Crypten'
    : deviceSupport.platform === 'android' 
      ? 'Como Instalar no Android'
      : deviceSupport.platform === 'ios'
        ? 'Como Instalar no iPhone'
        : 'Como Instalar no Desktop';
        
  const buttonSubtitle = deferredPrompt
    ? 'Acesso rápido como app nativo'
    : 'Ver instruções de instalação';

  return (
    <InstallContainer>
      <InstallButton onClick={handleInstallClick}>
        <InstallIcon>📱</InstallIcon>
        <InstallText>
          <InstallTitle>{buttonText}</InstallTitle>
          <InstallSubtitle>{buttonSubtitle}</InstallSubtitle>
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