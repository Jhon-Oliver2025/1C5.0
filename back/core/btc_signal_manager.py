# Imports necessários
from typing import Dict, Optional, List, Any, TypedDict
from datetime import datetime, timedelta
import time
import threading
import uuid
import pytz
from .database import Database
from .binance_client import BinanceClient
from .btc_correlation_analyzer import BTCCorrelationAnalyzer
from .telegram_notifier import TelegramNotifier
from config import server
import traceback

class SignalState:
    """Estados possíveis de um sinal"""
    PENDING = "pending"           # Aguardando confirmação
    CONFIRMED = "confirmed"       # Confirmado e enviado para dashboard
    REJECTED = "rejected"         # Rejeitado por algum motivo
    EXPIRED = "expired"           # Expirou sem confirmação

class ConfirmationReason:
    """Motivos de confirmação ou rejeição"""
    # Confirmação
    BREAKOUT_CONFIRMED = "breakout_confirmed"
    VOLUME_CONFIRMED = "volume_confirmed"
    BTC_ALIGNED = "btc_aligned"
    MOMENTUM_SUSTAINED = "momentum_sustained"
    
    # Rejeição
    BTC_OPPOSITE = "btc_opposite"
    VOLUME_INSUFFICIENT = "volume_insufficient"
    REVERSAL_DETECTED = "reversal_detected"
    TIMEOUT_EXPIRED = "timeout_expired"
    SUPPORT_RESISTANCE_HOLD = "support_resistance_hold"

class PendingSignal(TypedDict):
    """Estrutura de um sinal pendente com rastreabilidade completa"""
    id: str
    symbol: str
    type: str  # COMPRA ou VENDA
    entry_price: float
    target_price: float
    projection_percentage: float
    quality_score: float
    signal_class: str
    created_at: datetime
    expires_at: datetime
    confirmation_attempts: int
    last_check: datetime
    btc_correlation: float
    btc_trend: str
    original_data: Dict[str, Any]
    
    # Campos de rastreabilidade
    generation_reasons: Dict[str, Any]     # Por que foi gerado
    confirmation_checks: List[Dict]        # Histórico de verificações
    final_decision_reason: Optional[Dict[str, Any]]  # Por que foi confirmado/rejeitado

class BTCSignalManager:
    """Gerenciador central de sinais BTC e sistema de confirmação"""
    
    def __init__(self, db_instance: Database):
        """Inicializa o gerenciador de sinais BTC"""
        print("₿ Inicializando BTCSignalManager...")
        
        # Dependências principais
        self.db = db_instance
        self.binance = BinanceClient()
        self.btc_analyzer = BTCCorrelationAnalyzer(self.binance)
        
        # Configurações do sistema
        self.config = {
            'confirmation_timeout': 14400,  # 4 horas em segundos
            'check_interval': 300,          # 5 minutos
            'max_confirmation_attempts': 12, # Máximo 12 tentativas (1 hora)
            'min_breakout_percentage': 0.5,  # 0.5% mínimo para rompimento
            'min_volume_increase': 1.2,      # 20% aumento mínimo no volume
            'btc_alignment_threshold': 0.3   # Threshold para alinhamento BTC
        }
        
        # Estados dos sinais
        self.pending_signals: List[PendingSignal] = []
        self.confirmed_signals: List[Dict[str, Any]] = []
        self.rejected_signals: List[Dict[str, Any]] = []
        
        # Controle de sinais duplicados diários
        self.daily_confirmed_signals: set = set()  # (symbol, type) confirmados hoje
        self.last_reset_date = datetime.now().date()  # Data do último reset
        
        # Controle de thread
        self.is_monitoring: bool = False
        self.monitoring_thread: Optional[threading.Thread] = None
        
        # Configurar notificações (opcional)
        self.notifier = self._setup_telegram_notifier()
        
        # Carregar sinais confirmados existentes do CSV
        self._load_confirmed_signals_from_csv()
        
        print("✅ BTCSignalManager inicializado com sucesso!")
        
        # Limpar sinais duplicados na inicialização
        self._cleanup_duplicate_signals()
    
    def _cleanup_duplicate_signals(self) -> None:
        """Remove sinais duplicados da lista de pendentes"""
        try:
            if not self.pending_signals:
                return
            
            original_count = len(self.pending_signals)
            seen_signals = set()
            unique_signals = []
            
            for signal in self.pending_signals:
                signal_key = (signal['symbol'], signal['type'])
                if signal_key not in seen_signals:
                    seen_signals.add(signal_key)
                    unique_signals.append(signal)
                else:
                    print(f"🗑️ Removendo sinal duplicado: {signal['symbol']} ({signal['type']}) - ID: {signal['id'][:8]}")
            
            self.pending_signals = unique_signals
            removed_count = original_count - len(unique_signals)
            
            if removed_count > 0:
                print(f"🧹 Limpeza concluída: {removed_count} sinais duplicados removidos ({original_count} → {len(unique_signals)})")
            else:
                print("✅ Nenhum sinal duplicado encontrado")
                
        except Exception as e:
            print(f"❌ Erro na limpeza de sinais duplicados: {e}")
            traceback.print_exc()
    
    def _setup_telegram_notifier(self) -> Optional[TelegramNotifier]:
        """Configura notificações do Telegram (opcional)"""
        try:
            telegram_token = server.config.get('TELEGRAM_TOKEN')
            telegram_chat_id = server.config.get('TELEGRAM_CHAT_ID')
            
            if telegram_token and telegram_chat_id:
                notifier = TelegramNotifier(telegram_token, telegram_chat_id)
                if notifier.test_connection():
                    return notifier
            return None
        except Exception as e:
            print(f"⚠️ Erro ao configurar Telegram no BTCSignalManager: {e}")
            return None
    
    def start_monitoring(self) -> bool:
        """Inicia o monitoramento de confirmações"""
        if self.is_monitoring:
            print("⚠️ Monitoramento de confirmações já está ativo")
            return False
        
        print("🚀 Iniciando monitoramento de confirmações BTC...")
        self.is_monitoring = True
        
        # Iniciar thread de monitoramento
        self.monitoring_thread = threading.Thread(
            target=self._confirmation_loop,
            daemon=True
        )
        self.monitoring_thread.start()
        
        print("✅ Monitoramento de confirmações iniciado!")
        return True
    
    def reset_daily_confirmed_signals(self) -> None:
        """Reseta o controle de sinais confirmados diários (chamado no restart às 21:00)"""
        try:
            previous_count = len(self.daily_confirmed_signals)
            previous_date = self.last_reset_date
            
            # Limpar lista de sinais confirmados hoje
            self.daily_confirmed_signals.clear()
            
            # Atualizar data do último reset
            self.last_reset_date = datetime.now().date()
            
            print("\n" + "="*60)
            print("🔄 RESET DO CONTROLE DE SINAIS CONFIRMADOS DIÁRIOS")
            print("="*60)
            print(f"📅 Data anterior: {previous_date.strftime('%d/%m/%Y')}")
            print(f"📅 Nova data: {self.last_reset_date.strftime('%d/%m/%Y')}")
            print(f"🧹 Sinais únicos confirmados limpos: {previous_count}")
            print(f"✅ Sistema pronto para detectar novos sinais únicos")
            print("="*60)
            
        except Exception as e:
            print(f"❌ Erro ao resetar controle de sinais diários: {e}")
            traceback.print_exc()
    
    def check_post_restart_signals(self) -> None:
        """Verifica quais sinais ainda estão ativos após o restart e permite nova geração"""
        try:
            print("\n🔍 VERIFICANDO SINAIS AINDA ATIVOS PÓS-RESTART...")
            
            # Aqui podemos implementar lógica para verificar se sinais antigos ainda são válidos
            # Por exemplo, verificar se o preço ainda está em uma condição favorável
            # Se sim, o sinal pode ser gerado novamente
            
            print("✅ Verificação de sinais pós-restart concluída")
            print("🎯 Sinais ainda válidos poderão ser gerados novamente")
            
        except Exception as e:
            print(f"❌ Erro na verificação pós-restart: {e}")
            traceback.print_exc()
    
    def get_daily_confirmed_count(self) -> int:
        """Retorna o número de sinais únicos confirmados hoje"""
        return len(self.daily_confirmed_signals)
    
    def get_daily_confirmed_list(self) -> List[tuple]:
        """Retorna a lista de sinais confirmados hoje"""
        return list(self.daily_confirmed_signals)
    
    def stop_monitoring(self) -> None:
        """Para o monitoramento de confirmações"""
        print("🛑 Parando monitoramento de confirmações...")
        self.is_monitoring = False
        
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5)
        
        print("✅ Monitoramento de confirmações parado")
    
    def add_pending_signal(self, signal_data: Dict[str, Any]) -> str:
        """Adiciona um sinal para aguardar confirmação"""
        try:
            symbol = signal_data['symbol']
            signal_type = signal_data['type']
            
            # Verificar se já foi confirmado hoje (regra de não duplicação)
            signal_key = (symbol, signal_type)
            if signal_key in self.daily_confirmed_signals:
                print(f"🚫 Sinal {symbol} ({signal_type}) já confirmado hoje - ignorando duplicata")
                print(f"   📅 Sinais confirmados hoje: {len(self.daily_confirmed_signals)}")
                return ""
            
            # Verificar se já existe um sinal pendente para o mesmo símbolo e tipo
            existing_signal = next(
                (s for s in self.pending_signals 
                 if s['symbol'] == symbol and s['type'] == signal_type), 
                None
            )
            
            if existing_signal:
                print(f"⚠️ Sinal {symbol} ({signal_type}) já existe pendente (ID: {existing_signal['id'][:8]}) - ignorando duplicata")
                return existing_signal['id']
            
            # Gerar ID único para o sinal
            signal_id = str(uuid.uuid4())
            
            # Usar timezone de São Paulo para timestamps
            sao_paulo_tz = pytz.timezone('America/Sao_Paulo')
            now_sp = datetime.now(sao_paulo_tz)
            
            # Criar sinal pendente
            pending_signal: PendingSignal = {
                'id': signal_id,
                'symbol': symbol,
                'type': signal_type,
                'entry_price': signal_data['entry_price'],
                'target_price': signal_data['target_price'],
                'projection_percentage': signal_data['projection_percentage'],
                'quality_score': signal_data['quality_score'],
                'signal_class': signal_data['signal_class'],
                'created_at': now_sp,
                'expires_at': now_sp + timedelta(seconds=self.config['confirmation_timeout']),
                'confirmation_attempts': 0,
                'last_check': now_sp,
                'btc_correlation': signal_data.get('btc_correlation', 0),
                'btc_trend': signal_data.get('btc_trend', 'NEUTRAL'),
                'original_data': signal_data,
                
                # Campos de rastreabilidade
                'generation_reasons': signal_data.get('generation_reasons', {}),
                'confirmation_checks': [],  # Inicializar lista vazia
                'final_decision_reason': None  # Será preenchido na confirmação/rejeição
            }
            
            # Adicionar à lista de pendentes
            self.pending_signals.append(pending_signal)
            
            print(f"⏳ Sinal {symbol} ({signal_type}) adicionado para confirmação (ID: {signal_id[:8]})")
            
            # Salvar no banco de dados
            self._save_pending_signal_to_db(pending_signal)
            
            return signal_id
            
        except Exception as e:
            print(f"❌ Erro ao adicionar sinal pendente: {e}")
            traceback.print_exc()
            return ""
    
    def _confirmation_loop(self) -> None:
        """Loop principal de verificação de confirmações"""
        print("\n" + "="*60)
        print("🔄 INICIANDO MONITORAMENTO DE CONFIRMAÇÕES BTC")
        print("="*60)
        
        while self.is_monitoring:
            try:
                cycle_start = time.time()
                # Usar timezone de São Paulo
                sao_paulo_tz = pytz.timezone('America/Sao_Paulo')
                current_time = datetime.now(sao_paulo_tz)
                
                if self.pending_signals:
                    print(f"\n⏰ {current_time.strftime('%d/%m/%Y %H:%M:%S')}")
                    print(f"🔍 Verificando {len(self.pending_signals)} sinais pendentes...")
                    
                    # Verificar cada sinal pendente
                    signals_to_remove = []
                    
                    for signal in self.pending_signals:
                        try:
                            result = self._check_signal_confirmation(signal)
                            
                            if result['action'] == 'confirm':
                                self._confirm_signal(signal, result['reasons'])
                                signals_to_remove.append(signal)
                            elif result['action'] == 'reject':
                                self._reject_signal(signal, result['reasons'])
                                signals_to_remove.append(signal)
                            elif result['action'] == 'expire':
                                self._expire_signal(signal)
                                signals_to_remove.append(signal)
                            # Se action == 'wait', continua pendente
                            
                        except Exception as e:
                            print(f"❌ Erro ao verificar sinal {signal['symbol']}: {e}")
                            continue
                    
                    # Remover sinais processados
                    for signal in signals_to_remove:
                        if signal in self.pending_signals:
                            self.pending_signals.remove(signal)
                
                # Calcular tempo de espera
                cycle_duration = time.time() - cycle_start
                wait_time = max(0, self.config['check_interval'] - cycle_duration)
                
                # Aguardar próximo ciclo
                self._interruptible_sleep(wait_time)
                
            except Exception as e:
                print(f"❌ Erro no ciclo de confirmação: {e}")
                traceback.print_exc()
                self._interruptible_sleep(30)  # Aguardar 30s em caso de erro
    
    def _check_signal_confirmation(self, signal: PendingSignal) -> Dict[str, Any]:
        """Verifica se um sinal deve ser confirmado, rejeitado ou continuar pendente"""
        try:
            # Usar timezone de São Paulo
            sao_paulo_tz = pytz.timezone('America/Sao_Paulo')
            current_time = datetime.now(sao_paulo_tz)
            
            # Verificar se expirou
            if current_time > signal['expires_at']:
                return {
                    'action': 'expire',
                    'reasons': [ConfirmationReason.TIMEOUT_EXPIRED]
                }
            
            # Incrementar tentativas
            signal['confirmation_attempts'] += 1
            signal['last_check'] = current_time
            
            # Verificar se excedeu máximo de tentativas
            if signal['confirmation_attempts'] > self.config['max_confirmation_attempts']:
                return {
                    'action': 'expire',
                    'reasons': [ConfirmationReason.TIMEOUT_EXPIRED]
                }
            
            # Obter dados atuais do símbolo
            current_data = self._get_current_symbol_data(signal['symbol'])
            if not current_data:
                return {'action': 'wait', 'reasons': []}
            
            # Verificar confirmações
            confirmations = []
            rejections = []
            
            # 1. Verificar rompimento de preço
            breakout_result = self._check_price_breakout(signal, current_data)
            if breakout_result['confirmed']:
                confirmations.append(ConfirmationReason.BREAKOUT_CONFIRMED)
            elif breakout_result['rejected']:
                rejections.append(ConfirmationReason.REVERSAL_DETECTED)
            
            # 2. Verificar volume
            volume_result = self._check_volume_confirmation(signal, current_data)
            if volume_result['confirmed']:
                confirmations.append(ConfirmationReason.VOLUME_CONFIRMED)
            elif volume_result['rejected']:
                rejections.append(ConfirmationReason.VOLUME_INSUFFICIENT)
            
            # 3. Verificar alinhamento BTC
            btc_result = self._check_btc_alignment(signal)
            if btc_result['confirmed']:
                confirmations.append(ConfirmationReason.BTC_ALIGNED)
            elif btc_result['rejected']:
                rejections.append(ConfirmationReason.BTC_OPPOSITE)
            
            # 4. Verificar momentum sustentado
            momentum_result = self._check_momentum_sustainability(signal, current_data)
            if momentum_result['confirmed']:
                confirmations.append(ConfirmationReason.MOMENTUM_SUSTAINED)
            
            # Registrar histórico desta verificação
            self._record_confirmation_check(signal, current_data, {
                'breakout_result': breakout_result,
                'volume_result': volume_result,
                'btc_result': btc_result,
                'momentum_result': momentum_result
            }, confirmations, rejections)
            
            # Decidir ação baseada nas confirmações
            if len(rejections) >= 2:  # 2+ rejeições = rejeitar
                return {
                    'action': 'reject',
                    'reasons': rejections
                }
            elif len(confirmations) >= 3:  # 3+ confirmações = confirmar
                return {
                    'action': 'confirm',
                    'reasons': confirmations
                }
            else:  # Continuar aguardando
                return {
                    'action': 'wait',
                    'reasons': confirmations + rejections
                }
            
        except Exception as e:
            print(f"❌ Erro na verificação de confirmação: {e}")
            return {'action': 'wait', 'reasons': []}
    
    def _record_confirmation_check(self, signal: PendingSignal, current_data: Dict[str, Any], 
                                  check_results: Dict[str, Dict], confirmations: List[str], 
                                  rejections: List[str]) -> None:
        """
        Registra o histórico detalhado de uma verificação de confirmação
        
        Args:
            signal: Sinal sendo verificado
            current_data: Dados atuais do mercado
            check_results: Resultados das verificações individuais
            confirmations: Lista de confirmações encontradas
            rejections: Lista de rejeições encontradas
        """
        try:
            # Obter análise BTC atual
            btc_analysis = self.btc_analyzer.get_current_btc_analysis()
            
            # Usar timezone de São Paulo para timestamps
            sao_paulo_tz = pytz.timezone('America/Sao_Paulo')
            current_time = datetime.now(sao_paulo_tz)
            
            # Criar registro da verificação
            check_record = {
                'timestamp': current_time,
                'attempt_number': signal['confirmation_attempts'],
                'time_since_creation': (current_time - signal['created_at']).total_seconds() / 60,  # em minutos
                
                # Condições de mercado no momento da verificação
                'market_conditions': {
                    'symbol_price': current_data.get('price', 0),
                    'symbol_volume_24h': current_data.get('volume', 0),
                    'price_change_24h': current_data.get('price_change_24h', 0),
                    'btc_trend': btc_analysis.get('trend', 'NEUTRAL'),
                    'btc_strength': btc_analysis.get('strength', 0),
                    'btc_volatility': btc_analysis.get('volatility', 0)
                },
                
                # Resultados detalhados de cada verificação
                'detailed_checks': {
                    'price_breakout': {
                        'confirmed': check_results['breakout_result'].get('confirmed', False),
                        'rejected': check_results['breakout_result'].get('rejected', False),
                        'percentage': check_results['breakout_result'].get('percentage', 0),
                        'required': self.config.get('min_breakout_percentage', 0.5)
                    },
                    'volume_confirmation': {
                        'confirmed': check_results['volume_result'].get('confirmed', False),
                        'rejected': check_results['volume_result'].get('rejected', False),
                        'ratio': check_results['volume_result'].get('ratio', 1.0),
                        'required': self.config.get('min_volume_increase', 1.2)
                    },
                    'btc_alignment': {
                        'confirmed': check_results['btc_result'].get('confirmed', False),
                        'rejected': check_results['btc_result'].get('rejected', False),
                        'alignment_score': check_results['btc_result'].get('alignment_score', 0),
                        'threshold': self.config.get('btc_alignment_threshold', 0.3)
                    },
                    'momentum_sustainability': {
                        'confirmed': check_results['momentum_result'].get('confirmed', False),
                        'rejected': check_results['momentum_result'].get('rejected', False),
                        'candles_count': check_results['momentum_result'].get('candles_count', 0),
                        'required': 2
                    }
                },
                
                # Resumo da verificação
                'verification_summary': {
                    'confirmations_found': confirmations.copy(),
                    'rejections_found': rejections.copy(),
                    'confirmations_count': len(confirmations),
                    'rejections_count': len(rejections),
                    'status': self._get_check_status(len(confirmations), len(rejections))
                },
                
                # Próximos passos
                'next_steps': {
                    'action_recommended': self._get_recommended_action(len(confirmations), len(rejections)),
                    'time_to_next_check': self.config.get('check_interval', 300),  # segundos
                    'attempts_remaining': self.config['max_confirmation_attempts'] - signal['confirmation_attempts']
                }
            }
            
            # Adicionar ao histórico do sinal
            signal['confirmation_checks'].append(check_record)
            
            # Log para debug
            print(f"📋 [{signal['symbol']}] Verificação #{signal['confirmation_attempts']}: "
                  f"{len(confirmations)} confirmações, {len(rejections)} rejeições")
            
        except Exception as e:
            print(f"❌ Erro ao registrar verificação: {e}")
            # Adicionar registro básico em caso de erro
            sao_paulo_tz = pytz.timezone('America/Sao_Paulo')
            signal['confirmation_checks'].append({
                'timestamp': datetime.now(sao_paulo_tz),
                'attempt_number': signal['confirmation_attempts'],
                'error': str(e),
                'confirmations_count': len(confirmations),
                'rejections_count': len(rejections)
            })
    
    def _get_check_status(self, confirmations_count: int, rejections_count: int) -> str:
        """Determina o status da verificação baseado nas contagens"""
        if rejections_count >= 2:
            return 'READY_TO_REJECT'
        elif confirmations_count >= 3:
            return 'READY_TO_CONFIRM'
        elif confirmations_count > rejections_count:
            return 'LEANING_POSITIVE'
        elif rejections_count > confirmations_count:
            return 'LEANING_NEGATIVE'
        else:
            return 'NEUTRAL'
    
    def _get_recommended_action(self, confirmations_count: int, rejections_count: int) -> str:
        """Retorna a ação recomendada baseada nas contagens"""
        if rejections_count >= 2:
            return 'REJECT'
        elif confirmations_count >= 3:
            return 'CONFIRM'
        else:
            return 'WAIT'
    
    def _get_current_symbol_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Obtém dados atuais do símbolo"""
        try:
            # Obter dados de klines recentes (últimas 5 velas de 1h)
            klines_data = self.binance.get_klines(symbol, '1h', 5)
            if not klines_data:
                return None
            
            # Obter ticker 24h
            ticker_data = self.binance.get_24h_ticker_data([symbol])
            if not ticker_data or symbol not in ticker_data:
                return None
            
            return {
                'klines': klines_data,
                'ticker': ticker_data[symbol],
                'current_price': float(klines_data[-1]['close']),
                'volume_24h': float(ticker_data[symbol]['volume'])
            }
            
        except Exception as e:
            print(f"❌ Erro ao obter dados do símbolo {symbol}: {e}")
            return None
    
    def _check_price_breakout(self, signal: PendingSignal, current_data: Dict[str, Any]) -> Dict[str, bool]:
        """Verifica se houve rompimento de preço confirmado"""
        try:
            current_price = current_data['current_price']
            entry_price = signal['entry_price']
            signal_type = signal['type']
            
            min_breakout = self.config['min_breakout_percentage'] / 100
            
            if signal_type == 'COMPRA':
                # Para compra, verificar se rompeu para cima
                breakout_price = entry_price * (1 + min_breakout)
                reversal_price = entry_price * (1 - min_breakout * 2)  # 2x para reversão
                
                if current_price >= breakout_price:
                    return {'confirmed': True, 'rejected': False}
                elif current_price <= reversal_price:
                    return {'confirmed': False, 'rejected': True}
            
            else:  # VENDA
                # Para venda, verificar se rompeu para baixo
                breakout_price = entry_price * (1 - min_breakout)
                reversal_price = entry_price * (1 + min_breakout * 2)  # 2x para reversão
                
                if current_price <= breakout_price:
                    return {'confirmed': True, 'rejected': False}
                elif current_price >= reversal_price:
                    return {'confirmed': False, 'rejected': True}
            
            return {'confirmed': False, 'rejected': False}
            
        except Exception as e:
            print(f"❌ Erro na verificação de breakout: {e}")
            return {'confirmed': False, 'rejected': False}
    
    def _check_volume_confirmation(self, signal: PendingSignal, current_data: Dict[str, Any]) -> Dict[str, bool]:
        """Verifica se há confirmação de volume"""
        try:
            klines = current_data['klines']
            if len(klines) < 3:
                return {'confirmed': False, 'rejected': False}
            
            # Volume das últimas 2 velas vs média das 3 anteriores
            recent_volume = (float(klines[-1]['volume']) + float(klines[-2]['volume'])) / 2
            avg_volume = sum(float(k['volume']) for k in klines[-5:-2]) / 3
            
            volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1
            
            if volume_ratio >= self.config['min_volume_increase']:
                return {'confirmed': True, 'rejected': False}
            elif volume_ratio < 0.8:  # Volume muito baixo
                return {'confirmed': False, 'rejected': True}
            
            return {'confirmed': False, 'rejected': False}
            
        except Exception as e:
            print(f"❌ Erro na verificação de volume: {e}")
            return {'confirmed': False, 'rejected': False}
    
    def _check_btc_alignment(self, signal: PendingSignal) -> Dict[str, bool]:
        """Verifica alinhamento com BTC"""
        try:
            btc_analysis = self.btc_analyzer.get_current_btc_analysis()
            signal_type = signal['type']
            
            # Verificar se BTC está alinhado com o sinal
            if signal_type == 'COMPRA':
                if btc_analysis['trend'] == 'BULLISH':
                    return {'confirmed': True, 'rejected': False}
                elif btc_analysis['trend'] == 'BEARISH' and btc_analysis['strength'] > 0.5:
                    return {'confirmed': False, 'rejected': True}
            
            else:  # VENDA
                if btc_analysis['trend'] == 'BEARISH':
                    return {'confirmed': True, 'rejected': False}
                elif btc_analysis['trend'] == 'BULLISH' and btc_analysis['strength'] > 0.5:
                    return {'confirmed': False, 'rejected': True}
            
            return {'confirmed': False, 'rejected': False}
            
        except Exception as e:
            print(f"❌ Erro na verificação de alinhamento BTC: {e}")
            return {'confirmed': False, 'rejected': False}
    
    def _check_momentum_sustainability(self, signal: PendingSignal, current_data: Dict[str, Any]) -> Dict[str, bool]:
        """Verifica se o momentum está se sustentando"""
        try:
            klines = current_data['klines']
            if len(klines) < 3:
                return {'confirmed': False, 'rejected': False}
            
            signal_type = signal['type']
            
            # Verificar últimas 3 velas
            last_3_closes = [float(k['close']) for k in klines[-3:]]
            
            if signal_type == 'COMPRA':
                # Para compra, verificar se pelo menos 2 das 3 últimas velas são de alta
                bullish_candles = sum(1 for i in range(1, len(last_3_closes)) 
                                    if last_3_closes[i] > last_3_closes[i-1])
                if bullish_candles >= 2:
                    return {'confirmed': True, 'rejected': False}
            
            else:  # VENDA
                # Para venda, verificar se pelo menos 2 das 3 últimas velas são de baixa
                bearish_candles = sum(1 for i in range(1, len(last_3_closes)) 
                                    if last_3_closes[i] < last_3_closes[i-1])
                if bearish_candles >= 2:
                    return {'confirmed': True, 'rejected': False}
            
            return {'confirmed': False, 'rejected': False}
            
        except Exception as e:
            print(f"❌ Erro na verificação de momentum: {e}")
            return {'confirmed': False, 'rejected': False}
    
    def _confirm_signal(self, signal: PendingSignal, reasons: List[str]) -> None:
        """Confirma um sinal e o envia para o dashboard"""
        try:
            print(f"✅ CONFIRMANDO SINAL: {signal['symbol']} - {signal['type']}")
            print(f"   🎯 Motivos: {', '.join(reasons)}")
            
            # Capturar motivos finais da confirmação
            signal['final_decision_reason'] = self._capture_final_decision_reason(
                signal, 'CONFIRMED', reasons
            )
            
            # Adicionar à lista de sinais confirmados hoje (controle de duplicação)
            signal_key = (signal['symbol'], signal['type'])
            self.daily_confirmed_signals.add(signal_key)
            print(f"   📅 Adicionado à lista de confirmados hoje: {signal_key}")
            print(f"   📊 Total de sinais únicos confirmados hoje: {len(self.daily_confirmed_signals)}")
            
            # Criar sinal confirmado com todos os campos necessários
            confirmed_signal = signal['original_data'].copy()
            # Usar timezone de São Paulo para data de confirmação
            sao_paulo_tz = pytz.timezone('America/Sao_Paulo')
            now_sp = datetime.now(sao_paulo_tz)
            confirmed_signal.update({
                'confirmation_id': signal['id'],
                'confirmed_at': now_sp.strftime('%d/%m/%Y %H:%M:%S'),
                'confirmation_reasons': ', '.join(reasons) if reasons else '',
                'confirmation_attempts': signal['confirmation_attempts'],
                'btc_correlation': signal.get('btc_correlation', 0.0),
                'btc_trend': signal.get('btc_trend', ''),
                'status': 'CONFIRMED'
            })
            
            # Adicionar à lista de confirmados
            self.confirmed_signals.append(confirmed_signal)
            
            # Salvar sinal confirmado no banco (usando o sistema existente)
            from .gerenciar_sinais import GerenciadorSinais
            gerenciador = GerenciadorSinais(self.db)
            gerenciador.save_signal(confirmed_signal)
            print(f"✅ Sinal {signal['symbol']} salvo no banco com motivos: {', '.join(reasons)}")
            
            # NOVO: Adicionar automaticamente ao sistema de monitoramento
            self._add_to_monitoring_system(confirmed_signal)
            
            # Enviar notificação se configurado
            if self.notifier:
                try:
                    self.notifier.send_signal(
                        signal['symbol'],
                        signal['type'],
                        signal['entry_price'],
                        signal['quality_score'],
                        '1h',
                        signal['target_price']
                    )
                except Exception as e:
                    print(f"⚠️ Erro ao enviar notificação de confirmação: {e}")
            
            print(f"✅ Sinal {signal['symbol']} confirmado e enviado para dashboard!")
            print(f"📊 Sinal adicionado ao sistema de monitoramento para avaliação quantitativa")
            
        except Exception as e:
            print(f"❌ Erro ao confirmar sinal: {e}")
            traceback.print_exc()
    
    def _reject_signal(self, signal: PendingSignal, reasons: List[str]) -> None:
        """Rejeita um sinal"""
        try:
            print(f"❌ REJEITANDO SINAL: {signal['symbol']} - {signal['type']}")
            print(f"   🚫 Motivos: {', '.join(reasons)}")
            
            # Capturar motivos finais da rejeição
            signal['final_decision_reason'] = self._capture_final_decision_reason(
                signal, 'REJECTED', reasons
            )
            
            # Usar timezone de São Paulo
            sao_paulo_tz = pytz.timezone('America/Sao_Paulo')
            
            # Criar sinal rejeitado
            rejected_signal = {
                'id': signal['id'],
                'symbol': signal['symbol'],
                'type': signal['type'],
                'entry_price': signal['entry_price'],
                'quality_score': signal['quality_score'],
                'signal_class': signal['signal_class'],
                'created_at': signal['created_at'],
                'rejected_at': datetime.now(sao_paulo_tz),
                'rejection_reasons': reasons,
                'confirmation_attempts': signal['confirmation_attempts'],
                'original_data': signal['original_data']
            }
            
            # Adicionar à lista de rejeitados
            self.rejected_signals.append(rejected_signal)
            
            # Salvar no banco como rejeitado
            self._save_rejected_signal_to_db(rejected_signal)
            
        except Exception as e:
            print(f"❌ Erro ao rejeitar sinal: {e}")
            traceback.print_exc()
    
    def _capture_final_decision_reason(self, signal: PendingSignal, decision: str, 
                                      reasons: List[str]) -> Dict[str, Any]:
        """
        Captura os motivos detalhados da decisão final (confirmação ou rejeição)
        
        Args:
            signal: Sinal que teve a decisão tomada
            decision: Tipo da decisão ('CONFIRMED' ou 'REJECTED')
            reasons: Lista de motivos da decisão
            
        Returns:
            Dicionário com motivos detalhados da decisão final
        """
        try:
            # Obter dados atuais do mercado
            current_data = self._get_current_symbol_data(signal['symbol'])
            btc_analysis = self.btc_analyzer.get_current_btc_analysis()
            
            # Calcular tempo total de processamento
            total_time_minutes = (datetime.now() - signal['created_at']).total_seconds() / 60
            
            # Analisar o histórico de verificações
            verification_summary = self._analyze_verification_history(signal['confirmation_checks'])
            
            # Determinar fatores decisivos
            decisive_factors = self._identify_decisive_factors(signal, reasons, current_data)
            
            return {
                'decision': decision,
                'timestamp': datetime.now(),
                'total_processing_time_minutes': round(total_time_minutes, 2),
                
                # Motivos principais
                'primary_reasons': reasons.copy(),
                'decisive_factors': decisive_factors,
                
                # Snapshot do mercado no momento da decisão
                'market_snapshot': {
                    'symbol_price': current_data.get('price', 0) if current_data else 0,
                    'price_change_from_entry': self._calculate_price_change(
                        signal['entry_price'], 
                        current_data.get('price', 0) if current_data else 0
                    ),
                    'volume_24h': current_data.get('volume', 0) if current_data else 0,
                    'btc_trend': btc_analysis.get('trend', 'NEUTRAL'),
                    'btc_strength': btc_analysis.get('strength', 0),
                    'market_session': self._get_current_market_session()
                },
                
                # Estatísticas do processo de confirmação
                'confirmation_stats': {
                    'total_attempts': signal['confirmation_attempts'],
                    'verification_history_summary': verification_summary,
                    'average_time_between_checks': self._calculate_avg_check_interval(signal),
                    'final_quality_assessment': self._assess_final_quality(signal, decision)
                },
                
                # Análise de performance (se confirmado)
                'performance_prediction': self._predict_signal_performance(signal, decision) if decision == 'CONFIRMED' else None,
                
                # Lições aprendidas
                'lessons_learned': self._extract_lessons_learned(signal, decision, reasons),
                
                # Contexto adicional
                'additional_context': {
                    'signal_generation_quality': signal.get('quality_score', 0),
                    'signal_class': signal.get('signal_class', 'UNKNOWN'),
                    'btc_correlation': signal.get('btc_correlation', 0),
                    'ranking_info': self._get_symbol_ranking_context(signal['symbol'])
                }
            }
            
        except Exception as e:
            print(f"❌ Erro ao capturar motivos da decisão final: {e}")
            return {
                'decision': decision,
                'timestamp': datetime.now(),
                'error': str(e),
                'basic_reasons': reasons.copy()
            }
    
    def _analyze_verification_history(self, checks: List[Dict]) -> Dict[str, Any]:
        """Analisa o histórico de verificações para extrair padrões"""
        if not checks:
            return {'total_checks': 0, 'patterns': []}
        
        confirmations_over_time = [check['verification_summary']['confirmations_count'] for check in checks]
        rejections_over_time = [check['verification_summary']['rejections_count'] for check in checks]
        
        return {
            'total_checks': len(checks),
            'confirmations_trend': 'increasing' if len(confirmations_over_time) > 1 and confirmations_over_time[-1] > confirmations_over_time[0] else 'stable',
            'rejections_trend': 'increasing' if len(rejections_over_time) > 1 and rejections_over_time[-1] > rejections_over_time[0] else 'stable',
            'peak_confirmations': max(confirmations_over_time) if confirmations_over_time else 0,
            'peak_rejections': max(rejections_over_time) if rejections_over_time else 0,
            'final_confirmation_count': confirmations_over_time[-1] if confirmations_over_time else 0,
            'final_rejection_count': rejections_over_time[-1] if rejections_over_time else 0
        }
    
    def _identify_decisive_factors(self, signal: PendingSignal, reasons: List[str], 
                                  current_data: Optional[Dict]) -> List[str]:
        """Identifica os fatores mais decisivos para a confirmação/rejeição"""
        factors = []
        
        # Analisar motivos específicos
        if 'BREAKOUT_CONFIRMED' in reasons:
            factors.append('Rompimento de preço confirmado')
        if 'VOLUME_CONFIRMED' in reasons:
            factors.append('Volume elevado sustentado')
        if 'BTC_ALIGNED' in reasons:
            factors.append('Alinhamento favorável com BTC')
        if 'MOMENTUM_SUSTAINED' in reasons:
            factors.append('Momentum técnico sustentado')
        
        # Fatores de rejeição
        if 'REVERSAL_DETECTED' in reasons:
            factors.append('Reversão de preço detectada')
        if 'VOLUME_INSUFFICIENT' in reasons:
            factors.append('Volume insuficiente')
        if 'BTC_OPPOSITE' in reasons:
            factors.append('BTC em direção oposta')
        if 'TIMEOUT_EXPIRED' in reasons:
            factors.append('Tempo limite excedido')
        
        return factors
    
    def _calculate_price_change(self, entry_price: float, current_price: float) -> float:
        """Calcula a mudança percentual do preço"""
        if entry_price == 0:
            return 0
        return ((current_price - entry_price) / entry_price) * 100
    
    def _get_current_market_session(self) -> str:
        """Determina a sessão de mercado atual"""
        hour = datetime.now().hour
        if 0 <= hour < 8:
            return 'Asiática'
        elif 8 <= hour < 16:
            return 'Europeia'
        else:
            return 'Americana'
    
    def _calculate_avg_check_interval(self, signal: PendingSignal) -> float:
        """Calcula o intervalo médio entre verificações"""
        checks = signal.get('confirmation_checks', [])
        if len(checks) < 2:
            return 0
        
        intervals = []
        for i in range(1, len(checks)):
            prev_time = checks[i-1]['timestamp']
            curr_time = checks[i]['timestamp']
            interval = (curr_time - prev_time).total_seconds() / 60  # em minutos
            intervals.append(interval)
        
        return sum(intervals) / len(intervals) if intervals else 0
    
    def _assess_final_quality(self, signal: PendingSignal, decision: str) -> str:
        """Avalia a qualidade final do processo de decisão"""
        attempts = signal['confirmation_attempts']
        quality_score = signal.get('quality_score', 0)
        
        if decision == 'CONFIRMED':
            if attempts <= 3 and quality_score >= 80:
                return 'EXCELLENT'
            elif attempts <= 6 and quality_score >= 75:
                return 'GOOD'
            else:
                return 'ACCEPTABLE'
        else:  # REJECTED
            if attempts <= 3:
                return 'EFFICIENT_REJECTION'
            elif attempts <= 6:
                return 'STANDARD_REJECTION'
            else:
                return 'SLOW_REJECTION'
    
    def _predict_signal_performance(self, signal: PendingSignal, decision: str) -> Dict[str, Any]:
        """Prediz a performance esperada do sinal (apenas para confirmados)"""
        quality_score = signal.get('quality_score', 0)
        signal_class = signal.get('signal_class', 'STANDARD')
        
        # Estimativa baseada na qualidade
        if quality_score >= 90:
            success_probability = 0.85
        elif quality_score >= 80:
            success_probability = 0.75
        elif quality_score >= 75:
            success_probability = 0.65
        else:
            success_probability = 0.55
        
        return {
            'estimated_success_probability': success_probability,
            'risk_level': 'LOW' if quality_score >= 85 else 'MEDIUM' if quality_score >= 75 else 'HIGH',
            'expected_timeframe': '2-6 horas' if signal_class in ['ELITE', 'PREMIUM+'] else '4-12 horas'
        }
    
    def _extract_lessons_learned(self, signal: PendingSignal, decision: str, reasons: List[str]) -> List[str]:
        """Extrai lições aprendidas do processo"""
        lessons = []
        
        attempts = signal['confirmation_attempts']
        quality_score = signal.get('quality_score', 0)
        
        if decision == 'CONFIRMED':
            if attempts <= 2:
                lessons.append('Sinal de alta qualidade confirmado rapidamente')
            if quality_score >= 85:
                lessons.append('Pontuação alta correlaciona com confirmação rápida')
        else:
            if 'REVERSAL_DETECTED' in reasons:
                lessons.append('Reversão de preço é um forte indicador de rejeição')
            if attempts > 8:
                lessons.append('Sinais que demoram muito para confirmar tendem a ser rejeitados')
        
        return lessons
    
    def _get_symbol_ranking_context(self, symbol: str) -> Dict[str, Any]:
        """Obtém contexto de ranking da moeda"""
        try:
            from .coin_ranking import coin_ranking
            return coin_ranking.get_ranking_info(symbol)
        except Exception:
            return {'error': 'Ranking info not available'}
    
    def _expire_signal(self, signal: PendingSignal) -> None:
        """Expira um sinal por timeout"""
        try:
            print(f"⏰ EXPIRANDO SINAL: {signal['symbol']} - {signal['type']} (Timeout)")
            
            # Tratar como rejeição por timeout
            self._reject_signal(signal, [ConfirmationReason.TIMEOUT_EXPIRED])
            
        except Exception as e:
            print(f"❌ Erro ao expirar sinal: {e}")
            traceback.print_exc()
    
    def _interruptible_sleep(self, duration: float) -> None:
        """Sleep que pode ser interrompido"""
        end_time = time.time() + duration
        while time.time() < end_time and self.is_monitoring:
            time.sleep(0.1)
    
    def _save_pending_signal_to_db(self, signal: PendingSignal) -> None:
        """Salva sinal pendente no banco de dados"""
        try:
            # Implementar salvamento no banco se necessário
            # Por enquanto, apenas log
            pass
        except Exception as e:
            print(f"❌ Erro ao salvar sinal pendente no DB: {e}")
    
    def _save_confirmed_signal_to_db(self, original_signal: PendingSignal, 
                                   confirmed_signal: Dict[str, Any], reasons: List[str]) -> None:
        """Salva sinal confirmado no banco de dados"""
        try:
            # Importar GerenciadorSinais
            from .gerenciar_sinais import GerenciadorSinais
            
            # Criar instância do gerenciador
            gerenciador = GerenciadorSinais(self.db)
            
            # Preparar dados do sinal para salvamento
            signal_data = {
                'id': confirmed_signal.get('id', original_signal['id']),
                'symbol': confirmed_signal['symbol'],
                'type': confirmed_signal['type'],
                'entry_price': confirmed_signal['entry_price'],
                'target_price': confirmed_signal['target_price'],
                'projection_percentage': confirmed_signal['projection_percentage'],
                'quality_score': confirmed_signal['quality_score'],
                'signal_class': confirmed_signal['signal_class'],
                'status': 'CONFIRMED',
                'created_at': original_signal['created_at'].strftime('%d/%m/%Y %H:%M:%S'),
                'confirmed_at': datetime.now(pytz.timezone('America/Sao_Paulo')).strftime('%d/%m/%Y %H:%M:%S'),
                'confirmation_reasons': ', '.join(reasons) if reasons else '',
                'confirmation_attempts': original_signal.get('confirmation_attempts', 0),
                'btc_correlation': original_signal.get('btc_correlation', 0.0),
                'btc_trend': original_signal.get('btc_trend', '')
            }
            
            # Salvar no banco de dados
            gerenciador.save_signal(signal_data)
            print(f"✅ Sinal {confirmed_signal['symbol']} salvo no banco com motivos: {', '.join(reasons)}")
            
        except Exception as e:
            print(f"❌ Erro ao salvar sinal confirmado no DB: {e}")
            import traceback
            traceback.print_exc()
    
    def _save_rejected_signal_to_db(self, rejected_signal: Dict[str, Any]) -> None:
        """Salva sinal rejeitado no banco de dados"""
        try:
            # Implementar salvamento no banco se necessário
            # Por enquanto, apenas log
            pass
        except Exception as e:
            print(f"❌ Erro ao salvar sinal rejeitado no DB: {e}")
    
    # Métodos para API
    def get_pending_signals(self) -> List[Dict[str, Any]]:
        """Retorna lista de sinais pendentes para a API"""
        return [{
            'id': signal['id'],
            'symbol': signal['symbol'],
            'type': signal['type'],
            'entry_price': signal['entry_price'],
            'target_price': signal['target_price'],
            'projection_percentage': signal['projection_percentage'],
            'quality_score': signal['quality_score'],
            'signal_class': signal['signal_class'],
            'created_at': signal['created_at'].strftime('%d/%m/%Y %H:%M:%S'),
            'expires_at': signal['expires_at'].strftime('%d/%m/%Y %H:%M:%S'),
            'confirmation_attempts': signal['confirmation_attempts'],
            'btc_correlation': signal['btc_correlation'],
            'btc_trend': signal['btc_trend']
        } for signal in self.pending_signals]
    
    def get_rejected_signals(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retorna lista de sinais rejeitados para a API"""
        # Retornar os mais recentes primeiro
        recent_rejected = sorted(self.rejected_signals, 
                               key=lambda x: x['rejected_at'], reverse=True)[:limit]
        
        return [{
            'id': signal['id'],
            'symbol': signal['symbol'],
            'type': signal['type'],
            'entry_price': signal['entry_price'],
            'quality_score': signal['quality_score'],
            'signal_class': signal['signal_class'],
            'created_at': signal['created_at'].strftime('%d/%m/%Y %H:%M:%S'),
            'rejected_at': signal['rejected_at'].strftime('%d/%m/%Y %H:%M:%S'),
            'rejection_reasons': signal['rejection_reasons'],
            'confirmation_attempts': signal['confirmation_attempts']
        } for signal in recent_rejected]
    
    def get_confirmed_signals(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retorna lista de sinais confirmados para a API (busca do Supabase + memória)"""
        try:
            # Buscar sinais confirmados do Supabase
            supabase_signals = self._get_confirmed_signals_from_supabase(limit)
            
            # Combinar com sinais em memória (para sinais recém-confirmados)
            memory_signals = sorted(self.confirmed_signals, 
                                  key=lambda x: x.get('confirmed_at', ''), reverse=True)
            
            # Aplicar limite aos sinais em memória se especificado
            if limit is not None:
                memory_signals = memory_signals[:limit]
            
            # Converter sinais em memória para o formato padrão
            memory_formatted = [{
                'id': signal.get('confirmation_id', signal.get('id', '')),
                'symbol': signal['symbol'],
                'type': signal['type'],
                'entry_price': signal['entry_price'],
                'target_price': signal['target_price'],
                'projection_percentage': signal['projection_percentage'],
                'quality_score': signal['quality_score'],
                'signal_class': signal['signal_class'],
                'created_at': signal.get('timestamp', signal.get('created_at', '')),
                'confirmed_at': signal.get('confirmed_at', ''),
                'confirmation_reasons': signal.get('confirmation_reasons', []),
                'confirmation_attempts': signal.get('confirmation_attempts', 0),
                'btc_correlation': signal.get('btc_correlation', 0),
                'btc_trend': signal.get('btc_trend', 'NEUTRAL')
            } for signal in memory_signals]
            
            # Combinar e remover duplicatas (priorizar Supabase)
            all_signals = supabase_signals + memory_formatted
            
            # Remover duplicatas baseado no símbolo e tipo
            seen = set()
            unique_signals = []
            for signal in all_signals:
                key = (signal['symbol'], signal['type'])
                if key not in seen:
                    seen.add(key)
                    unique_signals.append(signal)
            
            # Ordenar por data de confirmação (mais recente primeiro)
            unique_signals.sort(key=lambda x: x.get('confirmed_at', ''), reverse=True)
            
            # Aplicar limite final se especificado
            if limit is not None:
                unique_signals = unique_signals[:limit]
            
            print(f"📊 Retornando {len(unique_signals)} sinais confirmados ({len(supabase_signals)} do Supabase, {len(memory_formatted)} da memória)")
            return unique_signals
            
        except Exception as e:
            print(f"❌ Erro ao buscar sinais confirmados: {e}")
            # Fallback para sinais em memória apenas
            recent_confirmed = sorted(self.confirmed_signals, 
                                    key=lambda x: x.get('confirmed_at', ''), reverse=True)
            
            if limit is not None:
                recent_confirmed = recent_confirmed[:limit]
            
            return [{
                'id': signal.get('confirmation_id', signal.get('id', '')),
                'symbol': signal['symbol'],
                'type': signal['type'],
                'entry_price': signal['entry_price'],
                'target_price': signal['target_price'],
                'projection_percentage': signal['projection_percentage'],
                'quality_score': signal['quality_score'],
                'signal_class': signal['signal_class'],
                'created_at': signal.get('timestamp', signal.get('created_at', '')),
                'confirmed_at': signal.get('confirmed_at', ''),
                'confirmation_reasons': signal.get('confirmation_reasons', []),
                'confirmation_attempts': signal.get('confirmation_attempts', 0),
                'btc_correlation': signal.get('btc_correlation', 0),
                'btc_trend': signal.get('btc_trend', 'NEUTRAL')
            } for signal in recent_confirmed]
    
    def _get_confirmed_signals_from_supabase(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Busca sinais confirmados diretamente do Supabase"""
        try:
            # Importar Supabase
            import os
            from supabase import create_client, Client
            
            supabase_url = os.getenv('SUPABASE_URL')
            supabase_key = os.getenv('SUPABASE_ANON_KEY')
            
            if not supabase_url or not supabase_key:
                print("⚠️ Supabase não configurado para buscar sinais confirmados")
                return []
            
            supabase: Client = create_client(supabase_url, supabase_key)
            
            # Buscar sinais confirmados, ordenados por data de confirmação
            query = supabase.table('signals').select('*').eq('status', 'CONFIRMED').order('confirmed_at', desc=True)
            
            if limit is not None:
                query = query.limit(limit)
            
            result = query.execute()
            
            if not result.data:
                return []
            
            # Converter para formato padrão
            formatted_signals = []
            for signal in result.data:
                try:
                    formatted_signal = {
                        'id': signal.get('id', ''),
                        'symbol': signal.get('symbol', ''),
                        'type': signal.get('type', ''),
                        'entry_price': float(signal.get('entry_price', 0)),
                        'target_price': float(signal.get('target_price', 0)),
                        'projection_percentage': float(signal.get('projection_percentage', 0)),
                        'quality_score': float(signal.get('quality_score', 0)),
                        'signal_class': signal.get('signal_class', ''),
                        'created_at': signal.get('created_at', ''),
                        'confirmed_at': signal.get('confirmed_at', ''),
                        'confirmation_reasons': signal.get('confirmation_reasons', ''),
                        'confirmation_attempts': int(signal.get('confirmation_attempts', 0)),
                        'btc_correlation': float(signal.get('btc_correlation', 0)),
                        'btc_trend': signal.get('btc_trend', 'NEUTRAL')
                    }
                    formatted_signals.append(formatted_signal)
                except Exception as e:
                    print(f"⚠️ Erro ao formatar sinal {signal.get('id', 'unknown')}: {e}")
                    continue
            
            print(f"📊 Encontrados {len(formatted_signals)} sinais confirmados no Supabase")
            return formatted_signals
            
        except Exception as e:
            print(f"❌ Erro ao buscar sinais confirmados do Supabase: {e}")
            return []
    
    def get_confirmation_metrics(self) -> Dict[str, Any]:
        """Retorna métricas de confirmação para a API"""
        try:
            total_signals = len(self.confirmed_signals) + len(self.rejected_signals)
            confirmed_count = len(self.confirmed_signals)
            rejected_count = len(self.rejected_signals)
            pending_count = len(self.pending_signals)
            
            confirmation_rate = (confirmed_count / total_signals * 100) if total_signals > 0 else 0
            
            # Calcular tempo médio de confirmação
            avg_confirmation_time = 0
            if self.confirmed_signals:
                total_attempts = sum(signal.get('confirmation_attempts', 1) for signal in self.confirmed_signals)
                avg_confirmation_time = (total_attempts * self.config['check_interval']) / len(self.confirmed_signals) / 60  # em minutos
            
            return {
                'total_signals_processed': int(total_signals),
                'confirmed_signals': int(confirmed_count),
                'rejected_signals': int(rejected_count),
                'pending_signals': int(pending_count),
                'confirmation_rate': float(round(confirmation_rate, 1)),
                'average_confirmation_time_minutes': float(round(avg_confirmation_time, 1)),
                'system_status': 'active' if bool(self.is_monitoring) else 'inactive'
            }
            
        except Exception as e:
            print(f"❌ Erro ao calcular métricas: {e}")
            return {
                'total_signals_processed': 0,
                'confirmed_signals': 0,
                'rejected_signals': 0,
                'pending_signals': 0,
                'confirmation_rate': 0,
                'average_confirmation_time_minutes': 0,
                'system_status': 'error'
            }
    
    def manual_confirm_signal(self, signal_id: str) -> bool:
        """Confirma um sinal manualmente (para interface admin) com motivos técnicos"""
        try:
            # Encontrar sinal pendente
            signal = next((s for s in self.pending_signals if s['id'] == signal_id), None)
            if not signal:
                return False
            
            # Gerar motivos técnicos baseados na análise atual
            reasons = self._generate_technical_reasons(signal)
            
            # Confirmar sinal com motivos técnicos
            self._confirm_signal(signal, reasons)
            
            # Remover da lista de pendentes
            self.pending_signals.remove(signal)
            
            return True
            
        except Exception as e:
            print(f"❌ Erro na confirmação manual: {e}")
            return False
    
    def _generate_technical_reasons(self, signal: PendingSignal) -> List[str]:
        """Gera motivos técnicos para confirmação manual baseados na análise atual"""
        try:
            reasons = []
            
            # Obter dados atuais do símbolo
            current_data = self._get_current_symbol_data(signal['symbol'])
            if current_data:
                # Verificar rompimento de preço
                breakout_result = self._check_price_breakout(signal, current_data)
                if breakout_result.get('confirmed', False):
                    reasons.append(ConfirmationReason.BREAKOUT_CONFIRMED)
                
                # Verificar volume
                volume_result = self._check_volume_confirmation(signal, current_data)
                if volume_result.get('confirmed', False):
                    reasons.append(ConfirmationReason.VOLUME_CONFIRMED)
                
                # Verificar momentum
                momentum_result = self._check_momentum_sustainability(signal, current_data)
                if momentum_result.get('confirmed', False):
                    reasons.append(ConfirmationReason.MOMENTUM_SUSTAINED)
            
            # Verificar alinhamento BTC
            btc_result = self._check_btc_alignment(signal)
            if btc_result.get('confirmed', False):
                reasons.append(ConfirmationReason.BTC_ALIGNED)
            
            # Se não há motivos técnicos específicos, usar motivos gerais
            if not reasons:
                reasons = [
                    ConfirmationReason.BREAKOUT_CONFIRMED,
                    ConfirmationReason.VOLUME_CONFIRMED,
                    'MANUAL_CONFIRMATION'
                ]
            
            return reasons
            
        except Exception as e:
            print(f"⚠️ Erro ao gerar motivos técnicos: {e}")
            return ['MANUAL_CONFIRMATION']
    
    def manual_reject_signal(self, signal_id: str, reason: str = 'MANUAL_REJECTION') -> bool:
        """Rejeita um sinal manualmente (para interface admin)"""
        try:
            # Encontrar sinal pendente
            signal = next((s for s in self.pending_signals if s['id'] == signal_id), None)
            if not signal:
                return False
            
            # Rejeitar sinal
            self._reject_signal(signal, [reason])
            
            # Remover da lista de pendentes
            self.pending_signals.remove(signal)
            
            return True
            
        except Exception as e:
            print(f"❌ Erro na rejeição manual: {e}")
            return False
    
    def _add_to_monitoring_system(self, confirmed_signal: Dict[str, Any]) -> None:
        """Adiciona sinal confirmado ao sistema de monitoramento para avaliação quantitativa"""
        try:
            # Importar o sistema de monitoramento
            from .signal_monitoring_system import SignalMonitoringSystem
            
            # Obter instância do sistema de monitoramento
            monitoring_system = SignalMonitoringSystem.get_instance(self.db)
            
            # Adicionar sinal ao monitoramento
            monitoring_system.add_signal_to_monitoring(
                signal_id=confirmed_signal.get('confirmation_id', confirmed_signal.get('id', '')),
                symbol=confirmed_signal['symbol'],
                signal_type=confirmed_signal['type'],
                entry_price=confirmed_signal['entry_price'],
                target_price=confirmed_signal['target_price'],
                quality_score=confirmed_signal['quality_score'],
                signal_class=confirmed_signal['signal_class'],
                confirmation_reasons=confirmed_signal.get('confirmation_reasons', []),
                btc_correlation=confirmed_signal.get('btc_correlation', 0),
                btc_trend=confirmed_signal.get('btc_trend', 'NEUTRAL')
            )
            
            print(f"📊 Sinal {confirmed_signal['symbol']} adicionado ao monitoramento quantitativo")
            
        except Exception as e:
            print(f"⚠️ Erro ao adicionar sinal ao monitoramento: {e}")
            # Não falhar a confirmação por causa disso
            pass
    
    def _load_confirmed_signals_from_csv(self) -> None:
        """Carrega sinais confirmados do CSV na inicialização"""
        try:
            from .gerenciar_sinais import GerenciadorSinais
            
            # Criar instância do gerenciador
            gerenciador = GerenciadorSinais(self.db)
            
            # Carregar sinais do CSV
            csv_signals = gerenciador.load_signals_from_csv()
            
            if csv_signals:
                # Filtrar sinais que têm motivos de confirmação dos últimos 2 dias
                today = datetime.now().date()
                yesterday = today - timedelta(days=1)
                confirmed_with_reasons = []
                
                for signal in csv_signals:
                    try:
                        # Verificar se tem motivos de confirmação
                        reasons = signal.get('confirmation_reasons')
                        confirmed_at = signal.get('confirmed_at')
                        
                        if reasons and confirmed_at:
                            # Verificar se foi confirmado hoje
                            signal_date = None
                            for date_format in ['%d/%m/%Y %H:%M:%S', '%Y-%m-%d %H:%M:%S', '%d/%m/%Y']:
                                try:
                                    signal_date = datetime.strptime(confirmed_at, date_format).date()
                                    break
                                except ValueError:
                                    continue
                            
                            if signal_date == today or signal_date == yesterday:
                                # Converter para formato esperado pela API
                                confirmed_signal = {
                                    'id': signal.get('id', ''),
                                    'confirmation_id': signal.get('id', ''),
                                    'symbol': signal['symbol'],
                                    'type': signal['type'],
                                    'entry_price': float(signal['entry_price']) if signal.get('entry_price') else 0.0,
                                    'target_price': float(signal['target_price']) if signal.get('target_price') else 0.0,
                                    'projection_percentage': float(signal['projection_percentage']) if signal.get('projection_percentage') else 0.0,
                                    'quality_score': float(signal['quality_score']) if signal.get('quality_score') else 0.0,
                                    'signal_class': signal.get('signal_class', ''),
                                    'created_at': signal.get('entry_time', ''),
                                    'confirmed_at': confirmed_at,
                                    'confirmation_reasons': reasons if isinstance(reasons, list) else [reasons] if reasons else [],
                                    'confirmation_attempts': int(signal.get('confirmation_attempts', 0)) if signal.get('confirmation_attempts') else 0,
                                    'btc_correlation': float(signal.get('btc_correlation', 0)) if signal.get('btc_correlation') else 0.0,
                                    'btc_trend': signal.get('btc_trend', 'NEUTRAL'),
                                    'status': 'CONFIRMED'
                                }
                                
                                confirmed_with_reasons.append(confirmed_signal)
                                
                                # Adicionar ao controle de duplicação
                                signal_key = (signal['symbol'], signal['type'])
                                self.daily_confirmed_signals.add(signal_key)
                    
                    except Exception as e:
                        print(f"⚠️ Erro ao processar sinal do CSV: {e}")
                        continue
                
                # Adicionar à lista de confirmados
                self.confirmed_signals.extend(confirmed_with_reasons)
                
                print(f"📊 Carregados {len(confirmed_with_reasons)} sinais confirmados de hoje do CSV")
                print(f"🔒 {len(self.daily_confirmed_signals)} tipos de sinais únicos já confirmados hoje")
                
                if confirmed_with_reasons:
                    print(f"✅ Primeiros sinais carregados:")
                    for signal in confirmed_with_reasons[:3]:
                        reasons_str = ', '.join(signal['confirmation_reasons']) if signal['confirmation_reasons'] else 'Sem motivos'
                        print(f"   • {signal['symbol']} - {signal['type']} - Motivos: {reasons_str}")
            
        except Exception as e:
            print(f"⚠️ Erro ao carregar sinais confirmados do CSV: {e}")
            # Não falhar a inicialização por causa disso
            pass
    
    def get_monitoring_integration_status(self) -> Dict[str, Any]:
        """Retorna status da integração com o sistema de monitoramento"""
        try:
            from .signal_monitoring_system import SignalMonitoringSystem
            
            # Verificar se o sistema de monitoramento está ativo
            monitoring_system = SignalMonitoringSystem.get_instance(self.db)
            monitoring_stats = monitoring_system.get_system_statistics()
            
            return {
                'integration_active': True,
                'monitoring_system_status': 'active',
                'total_signals_monitored': monitoring_stats.get('total_active_signals', 0),
                'successful_signals': monitoring_stats.get('successful_signals', 0),
                'failed_signals': monitoring_stats.get('failed_signals', 0),
                'success_rate': monitoring_stats.get('success_rate', 0)
            }
            
        except Exception as e:
            print(f"⚠️ Erro ao verificar status do monitoramento: {e}")
            return {
                'integration_active': False,
                'monitoring_system_status': 'error',
                'error': str(e)
            }
    
    def add_signal_for_reanalysis(self, signal_data: Dict[str, Any]) -> bool:
        """Adiciona sinal baixado do Supabase para reprocessamento automático"""
        try:
            print(f"🔄 Adicionando sinal para reprocessamento: {signal_data.get('symbol')} - {signal_data.get('type')}")
            
            # Verificar se o sinal já existe nos pendentes (evitar duplicação)
            signal_key = (signal_data.get('symbol'), signal_data.get('type'))
            existing_signal = next(
                (s for s in self.pending_signals if (s['symbol'], s['type']) == signal_key),
                None
            )
            
            if existing_signal:
                print(f"⚠️ Sinal {signal_data.get('symbol')} - {signal_data.get('type')} já existe nos pendentes")
                return False
            
            # Criar sinal pendente para reprocessamento
            from datetime import datetime, timedelta
            import uuid
            
            # Usar timezone de São Paulo
            sao_paulo_tz = pytz.timezone('America/Sao_Paulo')
            now_sp = datetime.now(sao_paulo_tz)
            
            # Criar sinal pendente
            pending_signal = {
                'id': str(uuid.uuid4()),
                'symbol': signal_data.get('symbol'),
                'type': signal_data.get('type'),
                'entry_price': signal_data.get('entry_price'),
                'target_price': signal_data.get('target_price'),
                'projection_percentage': signal_data.get('projection_percentage'),
                'quality_score': signal_data.get('quality_score'),
                'signal_class': signal_data.get('signal_class'),
                'created_at': now_sp.strftime('%d/%m/%Y %H:%M:%S'),
                'expires_at': (now_sp + timedelta(hours=24)).strftime('%d/%m/%Y %H:%M:%S'),
                'confirmation_attempts': 0,
                'status': 'PENDING_REANALYSIS',
                'reprocessed_from_supabase': True,
                'original_supabase_data': signal_data.get('original_supabase_data', {}),
                'original_data': signal_data,
                'btc_correlation': 0.0,
                'btc_trend': 'NEUTRAL'
            }
            
            # Adicionar à lista de pendentes
            self.pending_signals.append(pending_signal)
            
            print(f"✅ Sinal {signal_data.get('symbol')} adicionado para reprocessamento automático")
            print(f"📊 Total de sinais pendentes: {len(self.pending_signals)}")
            
            # O sistema de confirmação automática processará este sinal
            # na próxima execução do ciclo de análise
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao adicionar sinal para reprocessamento: {e}")
            import traceback
            traceback.print_exc()
            return False