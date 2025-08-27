import React, { useState, useEffect } from 'react';
import { usePWA } from '../../hooks/usePWA';
import './PWAInstallPrompt.css';

interface PWAInstallPromptProps {
  onInstall?: () => void;
  onDismiss?: () => void;
  autoShow?: boolean;
}

/**
 * Componente para prompt de instalação PWA nativo
 * Adapta-se automaticamente para diferentes plataformas
 */
const PWAInstallPrompt: React.FC<PWAInstallPromptProps> = ({
  onInstall,
  onDismiss,
  autoShow = true
}) => {
  const { capabilities, showInstallPrompt, addToHomeScreen } = usePWA();
  const [isVisible, setIsVisible] = useState(false);
  const [isDismissed, setIsDismissed] = useState(false);

  useEffect(() => {
    // Verificar se deve mostrar o prompt
    if (autoShow && capabilities.canInstall && !capabilities.isInstalled && !isDismissed) {
      // Aguardar um pouco antes de mostrar
      const timer = setTimeout(() => {
        setIsVisible(true);
      }, 3000); // 3 segundos após carregamento

      return () => clearTimeout(timer);
    }
  }, [autoShow, capabilities.canInstall, capabilities.isInstalled, isDismissed]);

  const handleInstall = async () => {
    try {
      if (capabilities.platform === 'ios') {
        // Para iOS, mostrar instruções
        addToHomeScreen();
      } else {
        // Para outras plataformas, usar prompt nativo
        const installed = await showInstallPrompt();
        if (installed) {
          setIsVisible(false);
          onInstall?.();
        }
      }
    } catch (error) {
      console.error('Erro ao instalar PWA:', error);
    }
  };

  const handleDismiss = () => {
    setIsVisible(false);
    setIsDismissed(true);
    onDismiss?.();
  };

  const getInstallInstructions = () => {
    switch (capabilities.platform) {
      case 'ios':
        return {
          title: 'Instalar 1Crypten',
          subtitle: 'Adicione à sua tela inicial para acesso rápido',
          instructions: [
            'Toque no ícone de compartilhar',
            'Selecione "Adicionar à Tela de Início"',
            'Confirme a instalação'
          ],
          icon: '🍎'
        };
      case 'android':
        return {
          title: 'Instalar App 1Crypten',
          subtitle: 'Tenha acesso rápido aos sinais de trading',
          instructions: [
            'Toque em "Instalar" quando aparecer',
            'Ou use o menu do navegador',
            'Selecione "Adicionar à tela inicial"'
          ],
          icon: '🤖'
        };
      default:
        return {
          title: 'Instalar 1Crypten',
          subtitle: 'Acesse como um aplicativo nativo',
          instructions: [
            'Clique no ícone de instalação',
            'Ou use Ctrl+Shift+A',
            'Confirme a instalação'
          ],
          icon: '💻'
        };
    }
  };

  if (!isVisible || capabilities.isInstalled || !capabilities.canInstall) {
    return null;
  }

  const installInfo = getInstallInstructions();

  return (
    <div className="pwa-install-overlay">
      <div className="pwa-install-prompt">
        <div className="pwa-install-header">
          <div className="pwa-install-icon">{installInfo.icon}</div>
          <button 
            className="pwa-install-close"
            onClick={handleDismiss}
            aria-label="Fechar"
          >
            ✕
          </button>
        </div>
        
        <div className="pwa-install-content">
          <img 
            src="/logo3.png" 
            alt="1Crypten Logo" 
            className="pwa-install-logo"
          />
          
          <h3 className="pwa-install-title">{installInfo.title}</h3>
          <p className="pwa-install-subtitle">{installInfo.subtitle}</p>
          
          {capabilities.platform === 'ios' ? (
            <div className="pwa-install-instructions">
              <h4>Como instalar:</h4>
              <ol>
                {installInfo.instructions.map((instruction, index) => (
                  <li key={index}>{instruction}</li>
                ))}
              </ol>
            </div>
          ) : (
            <div className="pwa-install-features">
              <div className="pwa-feature">
                <span className="pwa-feature-icon">⚡</span>
                <span>Acesso instantâneo</span>
              </div>
              <div className="pwa-feature">
                <span className="pwa-feature-icon">📱</span>
                <span>Experiência nativa</span>
              </div>
              <div className="pwa-feature">
                <span className="pwa-feature-icon">🔔</span>
                <span>Notificações push</span>
              </div>
              <div className="pwa-feature">
                <span className="pwa-feature-icon">📶</span>
                <span>Funciona offline</span>
              </div>
            </div>
          )}
        </div>
        
        <div className="pwa-install-actions">
          {capabilities.platform !== 'ios' && (
            <button 
              className="pwa-install-button primary"
              onClick={handleInstall}
            >
              Instalar App
            </button>
          )}
          
          {capabilities.platform === 'ios' && (
            <button 
              className="pwa-install-button primary"
              onClick={handleInstall}
            >
              Ver Instruções
            </button>
          )}
          
          <button 
            className="pwa-install-button secondary"
            onClick={handleDismiss}
          >
            Agora não
          </button>
        </div>
        
        <div className="pwa-install-footer">
          <span className="pwa-install-platform">
            {capabilities.platform === 'ios' && '📱 iOS Safari'}
            {capabilities.platform === 'android' && '🤖 Android Chrome'}
            {capabilities.platform === 'desktop' && '💻 Desktop'}
          </span>
        </div>
      </div>
    </div>
  );
};

export default PWAInstallPrompt;