/**
 * Utilitário para verificar se o PWA atende a todos os critérios de instalação
 * Baseado nas diretrizes do Google para PWAs instaláveis
 */

export interface PWACheckResult {
  isInstallable: boolean;
  issues: string[];
  recommendations: string[];
  score: number;
}

/**
 * Verifica se o PWA atende aos critérios mínimos de instalação
 */
export const checkPWAInstallability = async (): Promise<PWACheckResult> => {
  const issues: string[] = [];
  const recommendations: string[] = [];
  let score = 0;
  const maxScore = 10;

  // 1. Verificar HTTPS
  if (location.protocol !== 'https:' && location.hostname !== 'localhost') {
    issues.push('❌ Site não está usando HTTPS');
  } else {
    score += 1;
  }

  // 2. Verificar manifest.json
  try {
    const manifestResponse = await fetch('/manifest.json');
    if (manifestResponse.ok) {
      const manifest = await manifestResponse.json();
      
      // Verificar propriedades obrigatórias do manifest
      if (manifest.name || manifest.short_name) {
        score += 1;
      } else {
        issues.push('❌ Manifest sem nome definido');
      }
      
      if (manifest.start_url) {
        score += 1;
      } else {
        issues.push('❌ Manifest sem start_url definida');
      }
      
      if (manifest.display === 'standalone' || manifest.display === 'fullscreen' || manifest.display === 'minimal-ui') {
        score += 1;
      } else {
        issues.push('❌ Manifest sem display mode adequado');
      }
      
      // Verificar ícones
      if (manifest.icons && manifest.icons.length >= 2) {
        const hasLargeIcon = manifest.icons.some((icon: any) => {
          const sizes = icon.sizes.split('x');
          return parseInt(sizes[0]) >= 192;
        });
        
        const hasSmallIcon = manifest.icons.some((icon: any) => {
          const sizes = icon.sizes.split('x');
          return parseInt(sizes[0]) >= 144 && parseInt(sizes[0]) < 192;
        });
        
        if (hasLargeIcon && hasSmallIcon) {
          score += 1;
        } else {
          issues.push('❌ Ícones insuficientes (precisa de pelo menos 144x144 e 192x192)');
        }
      } else {
        issues.push('❌ Manifest sem ícones suficientes');
      }
      
    } else {
      issues.push('❌ Manifest.json não encontrado ou inacessível');
    }
  } catch (error) {
    issues.push('❌ Erro ao carregar manifest.json');
  }

  // 3. Verificar Service Worker
  if ('serviceWorker' in navigator) {
    try {
      const registration = await navigator.serviceWorker.getRegistration();
      if (registration && registration.active) {
        score += 2;
      } else {
        issues.push('❌ Service Worker não está ativo');
      }
    } catch (error) {
      issues.push('❌ Erro ao verificar Service Worker');
    }
  } else {
    issues.push('❌ Service Worker não suportado pelo navegador');
  }

  // 4. Verificar se já está instalado
  const isStandalone = window.matchMedia('(display-mode: standalone)').matches;
  const isInWebAppiOS = (window.navigator as any).standalone === true;
  
  if (isStandalone || isInWebAppiOS) {
    recommendations.push('✅ PWA já está instalado');
    score += 1;
  }

  // 5. Verificar suporte a beforeinstallprompt
  if ('onbeforeinstallprompt' in window) {
    score += 1;
  } else {
    recommendations.push('⚠️ Navegador pode não suportar instalação automática');
  }

  // Recomendações baseadas no score
  if (score < 5) {
    recommendations.push('🔧 PWA precisa de correções críticas para ser instalável');
  } else if (score < 8) {
    recommendations.push('⚠️ PWA pode ser instalável, mas precisa de melhorias');
  } else {
    recommendations.push('✅ PWA atende aos critérios de instalação');
  }

  return {
    isInstallable: score >= 7,
    issues,
    recommendations,
    score: Math.round((score / maxScore) * 100)
  };
};

/**
 * Força a verificação de instalabilidade e exibe no console
 */
export const debugPWAInstallability = async () => {
  console.group('🔍 PWA Installability Check');
  
  const result = await checkPWAInstallability();
  
  console.log(`📊 Score: ${result.score}%`);
  console.log(`🎯 Instalável: ${result.isInstallable ? 'SIM' : 'NÃO'}`);
  
  if (result.issues.length > 0) {
    console.group('❌ Problemas encontrados:');
    result.issues.forEach(issue => console.log(issue));
    console.groupEnd();
  }
  
  if (result.recommendations.length > 0) {
    console.group('💡 Recomendações:');
    result.recommendations.forEach(rec => console.log(rec));
    console.groupEnd();
  }
  
  console.groupEnd();
  
  return result;
};

/**
 * Verifica se o dispositivo suporta instalação PWA
 */
export const checkDeviceSupport = () => {
  const userAgent = navigator.userAgent.toLowerCase();
  const isAndroid = userAgent.includes('android');
  const isIOS = /ipad|iphone|ipod/.test(userAgent);
  const isChrome = userAgent.includes('chrome');
  const isSafari = userAgent.includes('safari') && !userAgent.includes('chrome');
  const isEdge = userAgent.includes('edge');
  const isFirefox = userAgent.includes('firefox');
  
  return {
    platform: isAndroid ? 'android' : isIOS ? 'ios' : 'desktop',
    browser: isChrome ? 'chrome' : isSafari ? 'safari' : isEdge ? 'edge' : isFirefox ? 'firefox' : 'unknown',
    supportsInstallation: (
      (isAndroid && (isChrome || isEdge)) ||
      (isIOS && isSafari) ||
      (!isAndroid && !isIOS && (isChrome || isEdge))
    ),
    installationMethod: (
      isAndroid ? 'beforeinstallprompt' :
      isIOS ? 'add-to-homescreen' :
      'beforeinstallprompt'
    )
  };
};