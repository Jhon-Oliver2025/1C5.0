/**
 * Página dedicada para o App 1Crypten
 * Apresenta informações sobre o aplicativo e funcionalidade de instalação
 */

import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import styles from './App1CryptenPage.module.css';
import logo3 from '/logo3.png';
import '../Dashboard/DashboardMobile.css';
import { usePWA } from '../../hooks/usePWA';
import PWAInstallPrompt from '../../components/PWA/PWAInstallPrompt';
import PWASplashScreen from '../../components/PWA/PWASplashScreen';

/**
 * Página principal do App 1Crypten com PWA nativo
 */

/**
 * Página principal do App 1Crypten
 */
const App1CryptenPage: React.FC = () => {
  const { capabilities, showInstallPrompt, addToHomeScreen } = usePWA();
  const [isInstalling, setIsInstalling] = useState(false);
  const [showPrompt, setShowPrompt] = useState(false);

  /**
   * Função para instalar o app com feedback visual
   */
  const handleInstallApp = async () => {
    setIsInstalling(true);
    
    try {
      if (capabilities.platform === 'ios') {
        // Para iOS, mostrar instruções
        addToHomeScreen();
      } else {
        // Para outras plataformas, tentar instalação automática
        const installed = await showInstallPrompt();
        if (!installed) {
          // Se não conseguiu instalar automaticamente, mostrar prompt personalizado
          setShowPrompt(true);
        }
      }
    } catch (error) {
      console.error('Erro ao instalar app:', error);
      setShowPrompt(true);
    } finally {
      setIsInstalling(false);
    }
  };

  return (
    <div className={styles.container}>
      {/* CONTAINER MOTIVACIONAL NO TOPO DA DIV PRINCIPAL (4px) */}
      <div className="mobile-motivation-header-container">
        {/* Seção Motivacional */}
        <div className="mobile-motivational">
          <p className="mobile-motivational-text">
            Tenha o poder dos sinais na palma da sua mão, onde quer que esteja.
          </p>
        </div>

        {/* Espaçamento de Segurança (4px) */}
        <div className="mobile-safety-gap"></div>
      </div>

      {/* CONTEÚDO DA PÁGINA APP1CRYPTEN */}
      {/* Hero Section */}
      <section className={styles.hero}>
        <div className={styles.heroContent}>
          <img src={logo3} alt="1Crypten" className={styles.appIcon} />
          <h2 className={styles.heroTitle}>1Crypten</h2>
          <p className={styles.heroSubtitle}>Sinais de Trading em Tempo Real</p>
          <div className={styles.versionInfo}>
            <span className={styles.version}>v1.4.0</span>
            <span className={styles.versionLabel}>Versão Atual</span>
          </div>
          
          {/* Status do App */}
          {capabilities.isInstalled ? (
            <div className={styles.installedBadge}>
              ✅ App Instalado
            </div>
          ) : (
            <button 
              className={styles.installButton}
              onClick={handleInstallApp}
              disabled={isInstalling || !capabilities.canInstall}
            >
              {isInstalling ? (
                <>
                  <span className={styles.loadingIcon}>⏳</span>
                  Instalando...
                </>
              ) : (
                <>
                  <span className={styles.downloadIcon}>📱</span>
                  {capabilities.platform === 'ios' ? 'Ver Instruções' : 'Instalar App'}
                </>
              )}
            </button>
          )}
          
          {!capabilities.canInstall && !capabilities.isInstalled && (
            <div className={styles.notSupportedBadge}>
              ⚠️ Instalação não suportada neste navegador
            </div>
          )}
        </div>
      </section>

      {/* Features Section */}
      <section className={styles.features}>
        <h3 className={styles.sectionTitle}>Por que usar o App 1Crypten?</h3>
        
        <div className={styles.featureGrid}>
          <div className={styles.featureCard}>
            <div className={styles.featureIcon}>⚡</div>
            <h4 className={styles.featureTitle}>Ultra Rápido</h4>
            <p className={styles.featureDescription}>
              Acesso instantâneo aos sinais de trading sem demora
            </p>
          </div>

          <div className={styles.featureCard}>
            <div className={styles.featureIcon}>📱</div>
            <h4 className={styles.featureTitle}>Experiência Nativa</h4>
            <p className={styles.featureDescription}>
              Interface otimizada para celular com navegação fluida
            </p>
          </div>

          <div className={styles.featureCard}>
            <div className={styles.featureIcon}>🔄</div>
            <h4 className={styles.featureTitle}>Sempre Atualizado</h4>
            <p className={styles.featureDescription}>
              Atualizações automáticas sem precisar baixar da loja
            </p>
          </div>

          <div className={styles.featureCard}>
            <div className={styles.featureIcon}>💾</div>
            <h4 className={styles.featureTitle}>Super Leve</h4>
            <p className={styles.featureDescription}>
              Ocupa menos de 5MB no seu celular
            </p>
          </div>

          <div className={styles.featureCard}>
            <div className={styles.featureIcon}>🌐</div>
            <h4 className={styles.featureTitle}>Funciona Offline</h4>
            <p className={styles.featureDescription}>
              Acesse dados em cache mesmo sem internet
            </p>
          </div>

          <div className={styles.featureCard}>
            <div className={styles.featureIcon}>🔔</div>
            <h4 className={styles.featureTitle}>Notificações</h4>
            <p className={styles.featureDescription}>
              Receba alertas de novos sinais em tempo real
            </p>
          </div>
        </div>
      </section>

      {/* Installation Guide */}
      <section className={styles.guide}>
        <h3 className={styles.sectionTitle}>Como Instalar</h3>
        
        <div className={styles.guideSteps}>
          <div className={styles.step}>
            <div className={styles.stepNumber}>1</div>
            <div className={styles.stepContent}>
              <h4 className={styles.stepTitle}>Clique em "Baixar App"</h4>
              <p className={styles.stepDescription}>
                Toque no botão azul acima para iniciar a instalação
              </p>
            </div>
          </div>

          <div className={styles.step}>
            <div className={styles.stepNumber}>2</div>
            <div className={styles.stepContent}>
              <h4 className={styles.stepTitle}>Confirme a Instalação</h4>
              <p className={styles.stepDescription}>
                Seu navegador mostrará uma popup para confirmar
              </p>
            </div>
          </div>

          <div className={styles.step}>
            <div className={styles.stepNumber}>3</div>
            <div className={styles.stepContent}>
              <h4 className={styles.stepTitle}>Pronto!</h4>
              <p className={styles.stepDescription}>
                O ícone do 1Crypten aparecerá na sua tela inicial
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className={styles.faq}>
        <h3 className={styles.sectionTitle}>Perguntas Frequentes</h3>
        
        <div className={styles.faqList}>
          <div className={styles.faqItem}>
            <h4 className={styles.faqQuestion}>O app é gratuito?</h4>
            <p className={styles.faqAnswer}>
              Sim! O app 1Crypten é completamente gratuito para instalar e usar.
            </p>
          </div>

          <div className={styles.faqItem}>
            <h4 className={styles.faqQuestion}>Funciona em todos os celulares?</h4>
            <p className={styles.faqAnswer}>
              Sim, funciona em Android e iPhone com qualquer navegador moderno.
            </p>
          </div>

          <div className={styles.faqItem}>
            <h4 className={styles.faqQuestion}>Preciso de internet para usar?</h4>
            <p className={styles.faqAnswer}>
              Para sinais em tempo real sim, mas dados em cache funcionam offline.
            </p>
          </div>

          <div className={styles.faqItem}>
            <h4 className={styles.faqQuestion}>Como desinstalar?</h4>
            <p className={styles.faqAnswer}>
              Mantenha pressionado o ícone na tela inicial e selecione "Remover".
            </p>
          </div>
        </div>
      </section>

      {/* CTA Final */}
      <section className={styles.cta}>
        <div className={styles.ctaContent}>
          <h3 className={styles.ctaTitle}>Pronto para começar?</h3>
          <p className={styles.ctaDescription}>
            Instale o app 1Crypten agora e tenha acesso aos melhores sinais de trading na palma da sua mão!
          </p>
          
          <button 
            className={styles.finalInstallButton}
            onClick={handleInstallApp}
            disabled={isInstalling || !capabilities.canInstall || capabilities.isInstalled}
          >
            {capabilities.isInstalled ? (
              <>
                <span className={styles.downloadIcon}>✅</span>
                App Já Instalado
              </>
            ) : isInstalling ? (
              <>
                <span className={styles.loadingIcon}>⏳</span>
                Instalando...
              </>
            ) : (
              <>
                <span className={styles.downloadIcon}>📱</span>
                {capabilities.platform === 'ios' ? 'Ver Instruções de Instalação' : 'Instalar App Agora'}
              </>
            )}
          </button>
        </div>
      </section></div>
      
      {/* Componentes PWA */}
      {showPrompt && (
        <PWAInstallPrompt 
          onInstall={() => {
            setShowPrompt(false);
            console.log('App instalado via prompt!');
          }}
          onDismiss={() => setShowPrompt(false)}
          autoShow={false}
        />
      )}
    </div>
  );
};

export default App1CryptenPage;