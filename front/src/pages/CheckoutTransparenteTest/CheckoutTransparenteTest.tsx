import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { CreditCard, Lock, CheckCircle, AlertCircle, Info, Settings } from 'lucide-react';
import MercadoPagoCheckout from '../../components/MercadoPagoCheckout/MercadoPagoCheckout';

// Styled Components
const TestContainer = styled.div`
  min-height: 100vh;
  background: linear-gradient(135deg, #000000 0%, #1a1a2e 50%, #16213e 100%);
  padding: 2rem;
`;

const TestHeader = styled.div`
  text-align: center;
  margin-bottom: 3rem;
  
  h1 {
    color: #ffffff;
    font-size: 2.5rem;
    margin-bottom: 1rem;
    background: linear-gradient(135deg, #2196f3, #00bcd4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  
  p {
    color: rgba(255, 255, 255, 0.8);
    font-size: 1.1rem;
    max-width: 800px;
    margin: 0 auto;
    line-height: 1.6;
  }
`;

const TestGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 2rem;
  max-width: 1400px;
  margin: 0 auto;
  
  @media (max-width: 1200px) {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
`;

const CheckoutSection = styled.div`
  background: rgba(255, 255, 255, 0.05);
  border-radius: 20px;
  padding: 2rem;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
`;

const DebugSection = styled.div`
  background: rgba(255, 255, 255, 0.05);
  border-radius: 20px;
  padding: 2rem;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  height: fit-content;
`;

const SectionTitle = styled.h2`
  color: #ffffff;
  font-size: 1.5rem;
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const StatusBadge = styled.div<{ type: 'success' | 'error' | 'warning' | 'info' }>`
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 600;
  margin-bottom: 1rem;
  
  ${props => {
    switch (props.type) {
      case 'success':
        return `
          background: rgba(76, 175, 80, 0.2);
          border: 1px solid rgba(76, 175, 80, 0.5);
          color: #4caf50;
        `;
      case 'error':
        return `
          background: rgba(244, 67, 54, 0.2);
          border: 1px solid rgba(244, 67, 54, 0.5);
          color: #f44336;
        `;
      case 'warning':
        return `
          background: rgba(255, 193, 7, 0.2);
          border: 1px solid rgba(255, 193, 7, 0.5);
          color: #ffc107;
        `;
      case 'info':
        return `
          background: rgba(33, 150, 243, 0.2);
          border: 1px solid rgba(33, 150, 243, 0.5);
          color: #2196f3;
        `;
      default:
        return '';
    }
  }}
`;

const InfoBox = styled.div`
  background: rgba(33, 150, 243, 0.1);
  border: 1px solid rgba(33, 150, 243, 0.3);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  
  h3 {
    color: #2196f3;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 1.1rem;
  }
  
  p {
    color: rgba(255, 255, 255, 0.8);
    margin: 0;
    line-height: 1.6;
    font-size: 0.9rem;
  }
`;

const DebugLog = styled.div`
  background: rgba(0, 0, 0, 0.3);
  border-radius: 8px;
  padding: 1rem;
  margin-top: 1rem;
  max-height: 300px;
  overflow-y: auto;
  font-family: 'Courier New', monospace;
  font-size: 0.8rem;
  
  .log-entry {
    color: rgba(255, 255, 255, 0.8);
    margin-bottom: 0.5rem;
    
    &.success {
      color: #4caf50;
    }
    
    &.error {
      color: #f44336;
    }
    
    &.warning {
      color: #ffc107;
    }
    
    &.info {
      color: #2196f3;
    }
  }
`;

const ConfigSection = styled.div`
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  
  h4 {
    color: #ffffff;
    margin-bottom: 1rem;
    font-size: 1rem;
  }
  
  .config-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.5rem 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    
    &:last-child {
      border-bottom: none;
    }
    
    .label {
      color: rgba(255, 255, 255, 0.8);
      font-size: 0.9rem;
    }
    
    .value {
      color: #2196f3;
      font-size: 0.9rem;
      font-weight: 600;
    }
  }
`;

/**
 * Página de teste para o checkout transparente do Mercado Pago
 * Inclui debug e monitoramento em tempo real
 */
const CheckoutTransparenteTest: React.FC = () => {
  const [logs, setLogs] = useState<Array<{type: string, message: string, timestamp: string}>>([]);
  const [sdkStatus, setSdkStatus] = useState<'loading' | 'loaded' | 'error'>('loading');
  const [apiStatus, setApiStatus] = useState<'checking' | 'online' | 'offline'>('checking');

  // Curso de teste
  const testCourse = {
    id: 'test_checkout_transparente',
    name: 'Teste Checkout Transparente',
    description: 'Curso de teste para validar o checkout transparente do Mercado Pago',
    price: 97.00
  };

  /**
   * Adiciona log ao debug
   */
  const addLog = (type: string, message: string) => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs(prev => [...prev.slice(-20), { type, message, timestamp }]);
  };

  /**
   * Verifica status da API
   */
  const checkApiStatus = async () => {
    try {
      const apiUrl = import.meta.env.VITE_API_URL || '';
      const response = await fetch(`${apiUrl}/api/payments/config`);
      
      if (response.ok) {
        setApiStatus('online');
        addLog('success', 'API do backend está online');
      } else {
        setApiStatus('offline');
        addLog('error', `API retornou status ${response.status}`);
      }
    } catch (error) {
      setApiStatus('offline');
      addLog('error', `Erro ao conectar com API: ${error}`);
    }
  };

  /**
   * Verifica status do SDK do Mercado Pago
   */
  const checkSDKStatus = () => {
    if (window.MercadoPago) {
      setSdkStatus('loaded');
      addLog('success', 'SDK do Mercado Pago carregado');
    } else {
      setSdkStatus('loading');
      addLog('info', 'Aguardando carregamento do SDK...');
      
      // Verificar novamente em 2 segundos
      setTimeout(checkSDKStatus, 2000);
    }
  };

  useEffect(() => {
    addLog('info', 'Iniciando teste do checkout transparente');
    checkApiStatus();
    checkSDKStatus();
    
    // Interceptar logs do console para debug
    const originalLog = console.log;
    const originalError = console.error;
    const originalWarn = console.warn;
    
    console.log = (...args) => {
      originalLog(...args);
      if (args[0] && typeof args[0] === 'string' && args[0].includes('Mercado Pago')) {
        addLog('info', args.join(' '));
      }
    };
    
    console.error = (...args) => {
      originalError(...args);
      if (args[0] && typeof args[0] === 'string') {
        addLog('error', args.join(' '));
      }
    };
    
    console.warn = (...args) => {
      originalWarn(...args);
      if (args[0] && typeof args[0] === 'string') {
        addLog('warning', args.join(' '));
      }
    };
    
    return () => {
      console.log = originalLog;
      console.error = originalError;
      console.warn = originalWarn;
    };
  }, []);

  return (
    <TestContainer>
      <TestHeader>
        <h1>🧪 Teste Checkout Transparente</h1>
        <p>
          Página de teste para validar e refinar o checkout transparente do Mercado Pago.
          Monitore os logs em tempo real e teste diferentes cenários de pagamento.
        </p>
      </TestHeader>

      <TestGrid>
        <CheckoutSection>
          <SectionTitle>
            <CreditCard size={24} />
            Checkout Transparente
          </SectionTitle>
          
          <InfoBox>
            <h3>
              <Info size={20} />
              Informações do Teste
            </h3>
            <p>
              Este é um ambiente de teste para o checkout transparente. 
              Use dados de teste do Mercado Pago para simular transações.
            </p>
          </InfoBox>
          
          <MercadoPagoCheckout
            courseId={testCourse.id}
            course={testCourse}
            onSuccess={(paymentData) => {
              addLog('success', `Pagamento realizado com sucesso: ${JSON.stringify(paymentData)}`);
              console.log('✅ Pagamento realizado:', paymentData);
            }}
            onError={(error) => {
              addLog('error', `Erro no pagamento: ${error}`);
              console.error('❌ Erro no pagamento:', error);
            }}
          />
        </CheckoutSection>

        <DebugSection>
          <SectionTitle>
            <Settings size={24} />
            Debug & Monitoramento
          </SectionTitle>
          
          <ConfigSection>
            <h4>Status do Sistema</h4>
            <div className="config-item">
              <span className="label">API Backend:</span>
              <StatusBadge type={apiStatus === 'online' ? 'success' : apiStatus === 'offline' ? 'error' : 'warning'}>
                {apiStatus === 'online' && <CheckCircle size={16} />}
                {apiStatus === 'offline' && <AlertCircle size={16} />}
                {apiStatus === 'checking' && <Info size={16} />}
                {apiStatus}
              </StatusBadge>
            </div>
            <div className="config-item">
              <span className="label">SDK Mercado Pago:</span>
              <StatusBadge type={sdkStatus === 'loaded' ? 'success' : sdkStatus === 'error' ? 'error' : 'warning'}>
                {sdkStatus === 'loaded' && <CheckCircle size={16} />}
                {sdkStatus === 'error' && <AlertCircle size={16} />}
                {sdkStatus === 'loading' && <Info size={16} />}
                {sdkStatus}
              </StatusBadge>
            </div>
          </ConfigSection>
          
          <ConfigSection>
            <h4>Configurações</h4>
            <div className="config-item">
              <span className="label">Ambiente:</span>
              <span className="value">{import.meta.env.DEV ? 'Desenvolvimento' : 'Produção'}</span>
            </div>
            <div className="config-item">
              <span className="label">API URL:</span>
              <span className="value">{import.meta.env.VITE_API_URL || 'localhost:5000'}</span>
            </div>
            <div className="config-item">
              <span className="label">Valor do Teste:</span>
              <span className="value">R$ {testCourse.price.toFixed(2)}</span>
            </div>
          </ConfigSection>
          
          <div>
            <h4 style={{ color: '#ffffff', marginBottom: '1rem' }}>Logs em Tempo Real</h4>
            <DebugLog>
              {logs.length === 0 ? (
                <div className="log-entry info">Aguardando logs...</div>
              ) : (
                logs.map((log, index) => (
                  <div key={index} className={`log-entry ${log.type}`}>
                    [{log.timestamp}] {log.message}
                  </div>
                ))
              )}
            </DebugLog>
          </div>
          
          <InfoBox>
            <h3>
              <Lock size={20} />
              Dados de Teste
            </h3>
            <p>
              <strong>Cartão de Teste:</strong><br/>
              Número: 4509 9535 6623 3704<br/>
              Vencimento: 11/25<br/>
              CVV: 123<br/>
              Nome: APRO (aprovado) ou CONT (rejeitado)
            </p>
          </InfoBox>
        </DebugSection>
      </TestGrid>
    </TestContainer>
  );
};

export default CheckoutTransparenteTest;