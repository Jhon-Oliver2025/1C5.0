import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import SignalCard from '../../components/SignalCard/SignalCard';
import TradingSimulation from '../../components/TradingSimulation/TradingSimulation';
import { useAuthToken } from '../../hooks/useAuthToken';
import { useAdminCheck } from '../../hooks/useAdminCheck';
// PWA removido - agora temos página dedicada para o App 1Crypten
import styles from './DashboardPage.module.css';
import './DashboardMobile.css';
import logo3 from '/logo3.png';

/**
 * Interface para definir a estrutura de um sinal
 */
interface Signal {
  id: string;
  symbol: string;
  type: 'COMPRA' | 'VENDA';
  entry_price: number;
  entry_time: string;
  target_price: number;
  projection_percentage: number;
  signal_class: 'PREMIUM' | 'PREMIUM+' | 'ELITE' | 'ELITE+' | 'PADRÃO';
  status: string;
  is_favorite?: boolean;
  created_at?: string;
  confirmed_at?: string;
}

/**
 * Componente principal da página Dashboard
 * Exibe seção motivacional, cabeçalho com horários e lista de sinais
 */
const DashboardPage: React.FC = () => {
  const [signals, setSignals] = useState<Signal[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentTime, setCurrentTime] = useState(new Date());
  const [currentPhraseIndex, setCurrentPhraseIndex] = useState(0);
  
  // Estado para status dos mercados
  const [marketStatus, setMarketStatus] = useState({
    new_york: { status: 'CARREGANDO', time: '00:00:00' },
    asia: { status: 'CARREGANDO', time: '00:00:00' }
  });
  
  // Estado para dados do BTC
  const [btcData, setBtcData] = useState({
    price: 0,
    change_24h: 0,
    strength: 0,
    loading: true
  });
  
  // Estado para status das limpezas
  const [cleanupStatus, setCleanupStatus] = useState({
    morning_cleanup: { time: '10:00', status: 'CARREGANDO', description: 'Limpeza matinal' },
    evening_cleanup: { time: '21:00', status: 'CARREGANDO', description: 'Limpeza noturna' }
  });
  
  const navigate = useNavigate();
  const { isAuthenticated, logout } = useAuthToken();
  const { isAdmin } = useAdminCheck();
  
  /**
   * Limpa o cache da API para resolver problemas de dados duplicados
   */
  const clearApiCache = async () => {
    try {
      if ('serviceWorker' in navigator && navigator.serviceWorker.controller) {
        const messageChannel = new MessageChannel();
        
        return new Promise((resolve, reject) => {
          messageChannel.port1.onmessage = (event) => {
            if (event.data.success) {
              console.log('✅ Cache da API limpo com sucesso');
              resolve(event.data);
            } else {
              console.error('❌ Erro ao limpar cache da API:', event.data.error);
              reject(new Error(event.data.error));
            }
          };
          
          navigator.serviceWorker.controller.postMessage(
            { type: 'CLEAR_API_CACHE' },
            [messageChannel.port2]
          );
        });
      }
    } catch (error) {
      console.error('❌ Erro ao limpar cache da API:', error);
    }
  };

  // Redirecionar para login se não estiver autenticado
  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
    }
  }, [isAuthenticated, navigate]);

  // Função para buscar status dos mercados da API
  const fetchMarketStatus = async () => {
    try {
      const apiUrl = import.meta.env.VITE_API_URL || '';
      const response = await fetch(`${apiUrl}/api/market-status`, {
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
          const responseData = await response.json();
          console.log('📊 Dados recebidos da API market-status:', responseData);
          
          // Verificar se os dados têm a estrutura esperada (nova estrutura)
          if (responseData && responseData.data && responseData.data.markets) {
            const markets = responseData.data.markets;
            setMarketStatus({
              new_york: markets.new_york,
              asia: markets.asia
            });
            console.log('✅ Status dos mercados atualizado:', {
              new_york: markets.new_york,
              asia: markets.asia
            });
          } else if (responseData && responseData.new_york && responseData.asia) {
            // Estrutura antiga (fallback)
            setMarketStatus(responseData);
            console.log('✅ Status dos mercados atualizado (estrutura antiga):', responseData);
          } else {
            console.warn('⚠️ API market-status retornou dados com estrutura inválida:', responseData);
          }
        } else {
          console.warn('⚠️ API market-status retornou HTML em vez de JSON');
        }
      } else {
        console.warn(`⚠️ API market-status não disponível: ${response.status}`);
      }
    } catch (error) {
      console.error('❌ Erro ao buscar status dos mercados:', error);
    }
  };

  // Função para buscar status das limpezas da API
  const fetchCleanupStatus = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      if (!token) {
        console.warn('Token não encontrado para buscar status das limpezas');
        return;
      }
      
      const apiUrl = import.meta.env.VITE_API_URL || '';
      const response = await fetch(`${apiUrl}/api/cleanup-status`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
          const data = await response.json();
          setCleanupStatus(data);
        } else {
          console.warn('API retornou HTML em vez de JSON, usando status padrão');
        }
      } else {
        if (response.status === 401 || response.status === 403) {
          console.warn('Token inválido para cleanup-status, redirecionando para login');
          logout();
          navigate('/login');
          return;
        }
        console.warn('API cleanup-status não disponível');
      }
    } catch (error) {
      console.error('Erro ao buscar status das limpezas:', error);
    }
  };

  // Função para buscar dados do BTC
  const fetchBTCData = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      if (!token) {
        console.warn('Token não encontrado para buscar dados do BTC');
        return;
      }
      
      const apiUrl = import.meta.env.VITE_API_URL || '';
      const response = await fetch(`${apiUrl}/api/btc-signals/metrics`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        
        // Usar dados reais da API metrics que contém btc_price_data e btc_analysis
        const btcPriceData = data.data?.btc_price_data;
        const btcAnalysisData = data.data?.btc_analysis;
        
        if (btcPriceData && btcAnalysisData) {
          setBtcData({
            price: btcPriceData.price || 0,
            change_24h: btcPriceData.change_24h || 0,
            strength: btcAnalysisData.strength || 50,
            loading: false
          });
        } else {
          // Fallback apenas se não houver dados na API
          setBtcData({
            price: 50000,
            change_24h: 0,
            strength: 50,
            loading: false
          });
        }
      } else {
        if (response.status === 401 || response.status === 403) {
          console.warn('Token inválido para BTC data, redirecionando para login');
          logout();
          navigate('/login');
          return;
        }
        // Fallback se a API não estiver disponível
        setBtcData({
          price: 50000,
          change_24h: 0,
          strength: 50,
          loading: false
        });
      }
    } catch (error) {
      console.error('Erro ao buscar dados do BTC:', error);
      // Fallback em caso de erro
      setBtcData({
        price: 50000,
        change_24h: 0,
        strength: 50,
        loading: false
      });
    }
  };



  /**
   * Array de frases motivacionais
   */
  const motivationalPhrases = [
    "A nova fronteira do investimento está ao seu alcance.",
    "Desbrave o universo cripto com clareza e precisão, do seu jeito.",
    "Veja os sinais em meio ao caos e transforme sua jornada.",
    "O futuro dos seus investimentos não é no espaço, mas em suas mãos.",
    "Sua nova jornada de riqueza começa com um único passo certo.",
    "Deixe para trás as promessas vazias. Olhe para a nova oportunidade.",
    "A melhor forma de prever o futuro é construí-lo agora.",
    "O mundo dos investimentos mudou. A nova oportunidade está aqui.",
    "Não se perca no espaço. Siga o caminho que te guia à liberdade.",
    "O mundo das criptomoedas é a nova corrida espacial. Você está pronto?"
  ];

  // Verificação de autenticação removida - gerenciada pelo MainLayout

  /**
   * Atualiza o horário atual a cada segundo
   */
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  /**
   * Alterna as frases motivacionais a cada 8 segundos
   */
  useEffect(() => {
    const phraseTimer = setInterval(() => {
      setCurrentPhraseIndex((prevIndex) => 
        (prevIndex + 1) % motivationalPhrases.length
      );
    }, 8000);

    return () => clearInterval(phraseTimer);
  }, [motivationalPhrases.length]);

  /**
   * Carrega os sinais da API na inicialização
   */
  useEffect(() => {
    fetchSignals();
    fetchMarketStatus();
    fetchCleanupStatus();
    fetchBTCData();
    
    // Verificar novos sinais a cada 2 minutos (sem refresh da página)
    const signalsTimer = setInterval(() => {
      fetchSignalsUpdate();
    }, 120000);
    
    // Atualizar status dos mercados a cada 30 segundos
    const marketTimer = setInterval(() => {
      fetchMarketStatus();
    }, 30000);
    
    // Atualizar status das limpezas a cada 60 segundos
    const cleanupTimer = setInterval(() => {
      fetchCleanupStatus();
    }, 60000);
    
    // Atualizar dados do BTC a cada 30 segundos
    const btcTimer = setInterval(() => {
      fetchBTCData();
    }, 30000);
    
    return () => {
      clearInterval(signalsTimer);
      clearInterval(marketTimer);
      clearInterval(cleanupTimer);
      clearInterval(btcTimer);
    };
  }, []);

  /**
   * Formata a data para exibição com timezone correto do Brasil
   */
  const formatDate = (date: Date) => {
    return date.toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      timeZone: 'America/Sao_Paulo'
    });
  };

  /**
   * Formata o horário para exibição com timezone correto do Brasil
   */
  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('pt-BR', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      timeZone: 'America/Sao_Paulo'
    });
  };



  // Estado para verificar se o backend está online
  const [isBackendOnline, setIsBackendOnline] = useState(true);

  /**
   * Busca os sinais da API
   */
  const fetchSignals = async () => {
    try {
      setLoading(true);
      setError(null);
      setIsBackendOnline(true);
      
      console.log('🔄 Carregando sinais da API...');
      
      // Tentar primeiro o endpoint de sinais confirmados sem autenticação
      let response = await fetch('/api/btc-signals/confirmed', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      // Se falhar, tentar o endpoint antigo com autenticação
      if (!response.ok) {
        console.log('🔄 Tentando endpoint antigo com autenticação...');
        const token = localStorage.getItem('auth_token');
        if (!token) {
          throw new Error('Token não encontrado');
        }
        
        response = await fetch('/api/signals/', {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
      }
      
      if (!response.ok) {
        if (response.status === 401 || response.status === 403) {
          console.warn('Token inválido, redirecionando para login');
          logout();
          navigate('/login');
          return;
        }
        throw new Error(`Erro na API: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('✅ Sinais carregados da API:', data);
      
      // Verificar se a resposta tem a estrutura esperada
      let signalsArray;
      
      // Tratar diferentes formatos de resposta da API
      if (Array.isArray(data)) {
        // Formato direto (novo endpoint público)
        signalsArray = data;
      } else if (data.data && Array.isArray(data.data.confirmed_signals)) {
        // Formato admin com wrapper
        signalsArray = data.data.confirmed_signals;
      } else if (data.signals && Array.isArray(data.signals)) {
        // Formato antigo
        signalsArray = data.signals;
      } else {
        console.warn('⚠️ Formato de resposta não reconhecido:', data);
        signalsArray = [];
      }
      
      if (!Array.isArray(signalsArray)) {
        console.error('❌ Dados não são um array:', signalsArray);
        signalsArray = [];
      }
      
      // Debug: verificar tipos de sinais recebidos
      const signalTypes = signalsArray.map(s => s.type);
      console.log('🔍 Tipos de sinais recebidos:', [...new Set(signalTypes)]);
      
      // Mapear os dados da API para o formato esperado
      const mappedSignals: Signal[] = signalsArray.map((signal: any) => {
        // Normalizar o tipo do sinal
        let normalizedType: 'COMPRA' | 'VENDA';
        const originalType = signal.type?.toUpperCase();
        
        if (originalType === 'LONG' || originalType === 'COMPRA' || originalType === 'BUY') {
          normalizedType = 'COMPRA';
        } else if (originalType === 'SHORT' || originalType === 'VENDA' || originalType === 'SELL') {
          normalizedType = 'VENDA';
        } else {
          console.warn(`⚠️ Tipo de sinal desconhecido: ${signal.type} para ${signal.symbol}`);
          normalizedType = 'COMPRA'; // Default para COMPRA em caso de tipo desconhecido
        }
        
        return {
            id: signal.id || `${signal.symbol}-${signal.entry_time || signal.created_at}`,
            symbol: signal.symbol,
            type: normalizedType,
            entry_price: parseFloat(signal.entry_price) || 0,
            entry_time: signal.entry_time || signal.created_at || signal.confirmed_at || '',
            target_price: parseFloat(signal.target_price) || 0,
            projection_percentage: parseFloat(signal.projection_percentage) || 0,
            signal_class: signal.signal_class || 'PADRÃO',
            status: signal.status || 'CONFIRMED',
            is_favorite: false,
            created_at: signal.created_at,
            confirmed_at: signal.confirmed_at
          };
      });
      
      // Remover duplicatas baseado em símbolo e entry_time
      const uniqueSignals = mappedSignals.filter((signal, index, self) => 
        index === self.findIndex(s => s.symbol === signal.symbol && s.entry_time === signal.entry_time)
      );
      
      // Ordenar sinais por data/hora mais recente primeiro
      const sortedSignals = uniqueSignals.sort((a, b) => {
        const dateA = new Date(a.entry_time || '1970-01-01').getTime();
        const dateB = new Date(b.entry_time || '1970-01-01').getTime();
        return dateB - dateA; // Mais recente primeiro
      });
      
      setSignals(sortedSignals);
      
      console.log(`🔍 Sinais únicos após remoção de duplicatas: ${uniqueSignals.length}/${mappedSignals.length}`);
      
      // Debug: verificar contagem após mapeamento
      const debugBuyCount = sortedSignals.filter(s => s.type === 'COMPRA').length;
      const debugSellCount = sortedSignals.filter(s => s.type === 'VENDA').length;
      console.log(`📊 Contagem após mapeamento: Total: ${sortedSignals.length}, Compra: ${debugBuyCount}, Venda: ${debugSellCount}`);
      
      if (debugBuyCount + debugSellCount !== sortedSignals.length) {
        console.error('❌ ERRO: Soma dos tipos não confere com o total!');
        console.log('Sinais com tipos problemáticos:', sortedSignals.filter(s => s.type !== 'COMPRA' && s.type !== 'VENDA'));
        
        // Limpar cache da API para resolver problemas de dados duplicados
        console.log('🧹 Limpando cache da API devido a inconsistência...');
        await clearApiCache();
        
        // Recarregar sinais após limpar cache
        setTimeout(() => {
          console.log('🔄 Recarregando sinais após limpeza do cache...');
          fetchSignals();
        }, 1000);
      }
    } catch (err) {
      console.error('❌ Erro ao carregar sinais:', err);
      setError(err instanceof Error ? err.message : 'Erro ao carregar sinais');
      setIsBackendOnline(false);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Verifica novos sinais sem fazer refresh da página
   * Mantém os sinais existentes e adiciona apenas novos
   */
  const fetchSignalsUpdate = async () => {
    try {
      console.log('🔄 Verificando novos sinais...');
      
      // Tentar primeiro o endpoint de sinais confirmados sem autenticação
      let response = await fetch('/api/btc-signals/confirmed', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      // Se falhar, tentar o endpoint antigo com autenticação
      if (!response.ok) {
        console.log('🔄 Tentando endpoint antigo para atualização...');
        const token = localStorage.getItem('auth_token');
        if (!token) {
          console.warn('Token não encontrado para atualizar sinais');
          return;
        }
        
        response = await fetch('/api/signals/', {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
      }
      
      if (!response.ok) {
        if (response.status === 403) {
          console.log('⚠️ Acesso negado - verificando autenticação');
          return;
        }
        throw new Error(`Erro na API: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Tratar diferentes formatos de resposta da API (igual à função fetchSignals)
      let signalsArray;
      
      if (Array.isArray(data)) {
        // Formato direto (novo endpoint público)
        signalsArray = data;
      } else if (data.data && Array.isArray(data.data.confirmed_signals)) {
        // Formato admin com wrapper
        signalsArray = data.data.confirmed_signals;
      } else if (data.signals && Array.isArray(data.signals)) {
        // Formato antigo
        signalsArray = data.signals;
      } else {
        console.warn('⚠️ Formato de resposta não reconhecido na atualização:', data);
        signalsArray = [];
      }
      
      if (Array.isArray(signalsArray)) {
        // Mapear novos sinais com normalização de tipo
        const newSignals: Signal[] = signalsArray.map((signal: any) => {
          // Normalizar o tipo do sinal (igual à função fetchSignals)
          let normalizedType: 'COMPRA' | 'VENDA';
          const originalType = signal.type?.toUpperCase();
          
          if (originalType === 'LONG' || originalType === 'COMPRA' || originalType === 'BUY') {
            normalizedType = 'COMPRA';
          } else if (originalType === 'SHORT' || originalType === 'VENDA' || originalType === 'SELL') {
            normalizedType = 'VENDA';
          } else {
            console.warn(`⚠️ Tipo de sinal desconhecido: ${signal.type} para ${signal.symbol}`);
            normalizedType = 'COMPRA'; // Default para COMPRA em caso de tipo desconhecido
          }
          
          return {
          id: signal.id || `${signal.symbol}-${signal.entry_time}`,
          symbol: signal.symbol,
          type: normalizedType,
          entry_price: parseFloat(signal.entry_price) || 0,
          entry_time: signal.entry_time,
          target_price: parseFloat(signal.target_price) || 0,
          projection_percentage: parseFloat(signal.projection_percentage) || 0,
          signal_class: signal.signal_class || 'PADRÃO',
          status: signal.status || 'CONFIRMED',
          is_favorite: false
        };
        });
        
        // Remover duplicatas dos novos sinais
        const uniqueNewSignals = newSignals.filter((signal, index, self) => 
          index === self.findIndex(s => s.symbol === signal.symbol && s.entry_time === signal.entry_time)
        );
        
        // Substituir completamente os sinais para evitar duplicação
        console.log(`🔄 Atualizando sinais: ${uniqueNewSignals.length} sinais únicos`);
        setSignals(uniqueNewSignals);
        
        console.log('📊 Sinais atualizados com sucesso - evitando duplicação');
        
        setIsBackendOnline(true);
      }
    } catch (err) {
      console.error('⚠️ Erro ao verificar novos sinais:', err);
      // Não mostrar erro para o usuário em verificações automáticas
    }
  };



  /**
   * Função para realizar logout
   */
  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    navigate('/login');
  };

  /**
   * Função para alternar favorito de um sinal
   */
  const toggleFavorite = (index: number) => {
    setSignals(prevSignals => 
      prevSignals.map((signal, i) => 
        i === index ? { ...signal, is_favorite: !signal.is_favorite } : signal
      )
    );
  };

  const totalSignals = signals.length;
  const buySignals = signals.filter(s => s.type === 'COMPRA').length;
  const sellSignals = signals.filter(s => s.type === 'VENDA').length;

  return (
    <div className={styles.dashboardContainer}>




      {/* CONTAINER 1 - MOTIVAÇÃO + CABEÇALHO (Fixo) */}
      <div className="mobile-motivation-header-container">
        {/* Seção Motivacional */}
        <div className="mobile-motivational">
          <p className="mobile-motivational-text">
            {motivationalPhrases[currentPhraseIndex]}
          </p>
        </div>

        {/* Espaçamento de Segurança (4px) */}
        <div className="mobile-safety-gap"></div>

        {/* Container Principal para Cabeçalho e Cards */}
        <div className="mobile-signals-container">
          {/* Cabeçalho dos Sinais (150px) */}
          <div className="mobile-signals-header">
            {/* Linha 1: Status dos Mercados + Status Backend */}
            <div className="mobile-market-times">
              <div className="mobile-market-item">
                <span className="mobile-market-label">BTC</span>
                <span className="mobile-market-time">
                  {btcData.loading ? 'Carregando...' : `$${btcData.price.toLocaleString('pt-BR', {minimumFractionDigits: 0, maximumFractionDigits: 0})}`}
                </span>
                <span className={`mobile-market-status ${btcData.change_24h >= 0 ? 'open' : 'closed'}`}>
                  {btcData.loading ? 'CARREGANDO' : `${btcData.change_24h >= 0 ? '+' : ''}${btcData.change_24h.toFixed(2)}%`}
                </span>
              </div>
              <div className="mobile-market-item">
                <span className="mobile-market-label">Asiático</span>
                <span className="mobile-market-time">{marketStatus.asia?.time || '00:00:00'}</span>
                <span className={`mobile-market-status ${marketStatus.asia?.status === 'ABERTO' ? 'open' : 'closed'}`}>
                  {marketStatus.asia?.status || 'CARREGANDO'}
                </span>
              </div>
              <div className="mobile-market-item">
                <span className="mobile-market-label">CRYPTO</span>
                <span className="mobile-market-time">{formatTime(currentTime)}</span>
                <span className="mobile-market-status crypto">ABERTO</span>
              </div>

            </div>
            
            {/* Linha 2: Estatísticas */}
            <div className="mobile-stats-row">
              <div className="mobile-stat-item">
                <span className="mobile-stat-label">Total</span>
                <span className="mobile-stat-value">{String(totalSignals).padStart(2, '0')}</span>
              </div>
              <div className="mobile-stat-item">
                <span className="mobile-stat-label">Compra</span>
                <span className="mobile-stat-value buy">{String(buySignals).padStart(2, '0')}</span>
              </div>
              <div className="mobile-stat-item">
                <span className="mobile-stat-label">Venda</span>
                <span className="mobile-stat-value sell">{String(sellSignals).padStart(2, '0')}</span>
              </div>
            </div>
          </div>

          {/* Seção de Cards dos Sinais (Scrollável) */}
          <div className={styles.cardsContainer}>
            {/* Lista de Sinais */}
            {loading && <div className={styles.loadingMessage}>Carregando sinais...</div>}
            {error && <div className={styles.errorMessage}>Erro ao carregar sinais: {error}</div>}
            {!loading && !error && signals.length === 0 && (
              <div className={styles.noSignalsMessage}>Nenhum sinal encontrado.</div>
            )}
            {!loading && !error && signals.length > 0 && (
              <div className={styles.signalsList}>
                {signals.map((signal, index) => (
                  <SignalCard
                    key={index}
                    symbol={signal.symbol}
                    type={signal.type}
                    entryPrice={String(signal.entry_price)}
                    targetPrice={String(signal.target_price)}
                    projectionPercentage={String(signal.projection_percentage)}
                    date={signal.entry_time}
                    createdAt={signal.created_at}
                    confirmedAt={signal.confirmed_at}
                    signalClass={signal.signal_class}
                    onToggleFavorite={() => toggleFavorite(index)}
                    isFavorite={signal.is_favorite || false}
                  />
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}


export default DashboardPage;