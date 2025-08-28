import React, { useState, useEffect } from 'react';
import styles from './UpdateNotification.module.css';

/**
 * Componente para notificar usuários sobre atualizações do PWA
 * Similar ao comportamento de apps nativos
 */
interface UpdateNotificationProps {
  onUpdate?: () => void;
}

const UpdateNotification: React.FC<UpdateNotificationProps> = ({ onUpdate }) => {
  const [showUpdate, setShowUpdate] = useState(false);
  const [newVersion, setNewVersion] = useState('');
  const [isUpdating, setIsUpdating] = useState(false);

  useEffect(() => {
    /**
     * Verifica se há uma nova versão do service worker disponível
     */
    const checkForUpdates = () => {
      if ('serviceWorker' in navigator) {
        navigator.serviceWorker.addEventListener('controllerchange', () => {
          // Nova versão foi instalada e está ativa
          setShowUpdate(false);
          window.location.reload();
        });

        navigator.serviceWorker.ready.then((registration) => {
          registration.addEventListener('updatefound', () => {
            const newWorker = registration.installing;
            if (newWorker) {
              newWorker.addEventListener('statechange', () => {
                if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                  // Nova versão disponível
                  setNewVersion('1.5.0'); // Versão atual
                  setShowUpdate(true);
                }
              });
            }
          });
        });
      }
    };

    checkForUpdates();

    // Listener para mensagens do Service Worker
    const handleServiceWorkerMessage = (event: MessageEvent) => {
      if (event.data && event.data.type === 'SW_UPDATED') {
        setNewVersion(event.data.version || '1.3.1');
        setShowUpdate(true);
      }
    };

    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.addEventListener('message', handleServiceWorkerMessage);
    }

    return () => {
      if ('serviceWorker' in navigator) {
        navigator.serviceWorker.removeEventListener('message', handleServiceWorkerMessage);
      }
    };
  }, []);

  /**
   * Atualiza o app para a nova versão
   */
  const handleUpdate = async () => {
    setIsUpdating(true);
    
    try {
      if ('serviceWorker' in navigator) {
        const registration = await navigator.serviceWorker.ready;
        if (registration.waiting) {
          // Força a ativação do novo service worker
          registration.waiting.postMessage({ type: 'SKIP_WAITING' });
        }
      }
      
      // Callback personalizado
      if (onUpdate) {
        onUpdate();
      }
      
      // Aguardar um pouco antes de recarregar
      setTimeout(() => {
        window.location.reload();
      }, 1000);
    } catch (error) {
      console.error('Erro ao atualizar:', error);
      setIsUpdating(false);
    }
  };

  /**
   * Dispensar a notificação de atualização
   */
  const handleDismiss = () => {
    setShowUpdate(false);
  };

  if (!showUpdate) {
    return null;
  }

  return (
    <div className={styles.overlay}>
      <div className={styles.notification}>
        <div className={styles.header}>
          <div className={styles.icon}>✨</div>
          <div className={styles.content}>
            <h4 className={styles.title}>Nova versão disponível</h4>
            <p className={styles.message}>
              v{newVersion} • Melhorias e correções
            </p>
          </div>
          <button 
            className={styles.closeButton}
            onClick={handleDismiss}
            disabled={isUpdating}
            aria-label="Fechar notificação"
          >
            ×
          </button>
        </div>
        
        <div className={styles.actions}>
          <button 
            className={styles.updateButton}
            onClick={handleUpdate}
            disabled={isUpdating}
          >
            {isUpdating ? (
              <>
                <span className={styles.spinner}></span>
                Atualizando
              </>
            ) : (
              'Atualizar'
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default UpdateNotification;