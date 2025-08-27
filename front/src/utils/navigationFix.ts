// Utilitário para corrigir problemas de navegação e loops infinitos
// Este arquivo resolve o problema de throttling do React Router

export class NavigationFix {
  private static navigationInProgress = false;
  private static lastNavigation = 0;
  private static readonly NAVIGATION_DELAY = 100; // 100ms entre navegações

  /**
   * Navega de forma segura, evitando loops infinitos
   * @param navigate - Função de navegação do React Router
   * @param path - Caminho para navegar
   * @param options - Opções de navegação
   */
  static safeNavigate(
    navigate: (path: string, options?: any) => void,
    path: string,
    options: any = { replace: true }
  ): void {
    const now = Date.now();
    
    // Evitar navegações muito rápidas
    if (this.navigationInProgress || (now - this.lastNavigation) < this.NAVIGATION_DELAY) {
      console.log(`🚫 NavigationFix: Navegação bloqueada para evitar loop - ${path}`);
      return;
    }

    // Verificar se já estamos na rota de destino
    if (window.location.pathname === path) {
      console.log(`🔄 NavigationFix: Já na rota ${path}, ignorando navegação`);
      return;
    }

    this.navigationInProgress = true;
    this.lastNavigation = now;

    console.log(`🎯 NavigationFix: Navegando para ${path}`);

    try {
      // Usar setTimeout para quebrar o ciclo de renderização
      setTimeout(() => {
        navigate(path, options);
        this.navigationInProgress = false;
      }, this.NAVIGATION_DELAY);
    } catch (error) {
      console.error('❌ NavigationFix: Erro na navegação:', error);
      this.navigationInProgress = false;
    }
  }

  /**
   * Reseta o estado de navegação
   */
  static reset(): void {
    this.navigationInProgress = false;
    this.lastNavigation = 0;
    console.log('🔄 NavigationFix: Estado resetado');
  }

  /**
   * Verifica se uma navegação está em progresso
   */
  static isNavigating(): boolean {
    return this.navigationInProgress;
  }

  /**
   * Força uma navegação usando window.location (último recurso)
   * @param path - Caminho para navegar
   */
  static forceNavigate(path: string): void {
    console.log(`🚨 NavigationFix: Forçando navegação para ${path}`);
    window.location.href = path;
  }

  /**
   * Debounce para useEffect que fazem navegação
   * @param callback - Função a ser executada
   * @param delay - Delay em ms
   */
  static debounceNavigation(callback: () => void, delay: number = 200): void {
    const now = Date.now();
    
    if ((now - this.lastNavigation) < delay) {
      console.log('🚫 NavigationFix: Navegação debounced');
      return;
    }

    this.lastNavigation = now;
    setTimeout(callback, 50);
  }
}

// Hook personalizado para navegação segura
export const useSafeNavigation = () => {
  const navigate = (path: string, options?: any) => {
    NavigationFix.safeNavigate(
      (p, o) => window.history.pushState(null, '', p),
      path,
      options
    );
  };

  const replace = (path: string) => {
    NavigationFix.safeNavigate(
      (p) => window.history.replaceState(null, '', p),
      path,
      { replace: true }
    );
  };

  return { navigate, replace, isNavigating: NavigationFix.isNavigating };
};

export default NavigationFix;