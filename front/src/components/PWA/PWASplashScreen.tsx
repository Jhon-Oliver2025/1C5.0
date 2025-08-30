import React, { useEffect, useState } from 'react';
import './PWASplashScreen.css';

interface PWASplashScreenProps {
  onComplete: () => void;
  duration?: number;
}

/**
 * Componente de Splash Screen para PWA
 * Proporciona uma experiência nativa de inicialização
 */
const PWASplashScreen: React.FC<PWASplashScreenProps> = ({ 
  onComplete, 
  duration = 2000 
}) => {
  const [isVisible, setIsVisible] = useState(true);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Simular carregamento inicial
    const loadingTimer = setTimeout(() => {
      setIsLoading(false);
    }, duration * 0.7); // 70% do tempo para loading

    // Timer para esconder splash screen
    const hideTimer = setTimeout(() => {
      setIsVisible(false);
      
      // Aguardar animação de fade out
      setTimeout(() => {
        onComplete();
      }, 500);
    }, duration);

    return () => {
      clearTimeout(loadingTimer);
      clearTimeout(hideTimer);
    };
  }, [duration, onComplete]);

  if (!isVisible) {
    return null;
  }

  return (
    <div className={`pwa-splash-screen ${!isVisible ? 'fade-out' : ''}`}>
      <div className="pwa-splash-content">
        <img 
          src="/logo3.png" 
          alt="1Crypten Logo" 
          className="pwa-splash-logo"
        />
        
        {/* Removido: título, subtítulo e textos de loading/ready */}
      </div>
      
      {/* Indicador de progresso */}
      <div className="pwa-splash-progress">
        <div className="pwa-splash-progress-bar"></div>
      </div>
    </div>
  );
};

export default PWASplashScreen;