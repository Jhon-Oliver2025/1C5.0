# API Routes para Sistema BTC de Confirmação de Sinais
from flask import Blueprint, jsonify, request
from middleware.auth_middleware import jwt_required, get_current_user
from core.database import Database
from core.btc_signal_manager import BTCSignalManager
from core.signal_confirmation_system import SignalConfirmationSystem
from core.binance_client import BinanceClient
from core.btc_correlation_analyzer import BTCCorrelationAnalyzer
import traceback
from datetime import datetime
import pytz

# Criar blueprint
btc_signals_bp = Blueprint('btc_signals', __name__, url_prefix='/api/btc-signals')

# Instâncias globais (serão inicializadas no app principal)
btc_signal_manager = None
confirmation_system = None
btc_analyzer = None

def init_btc_signals_routes(db_instance: Database, btc_manager: BTCSignalManager):
    """Inicializa as rotas com as instâncias necessárias"""
    global btc_signal_manager, confirmation_system, btc_analyzer
    btc_signal_manager = btc_manager
    
    # Inicializar sistemas auxiliares
    binance_client = BinanceClient()
    confirmation_system = SignalConfirmationSystem(binance_client)
    btc_analyzer = BTCCorrelationAnalyzer(binance_client)
    
    print("✅ Rotas BTC Signals inicializadas!")

@btc_signals_bp.route('/pending', methods=['GET'])
def get_pending_signals():
    """Retorna lista de sinais aguardando confirmação - Rota pública para dashboard"""
    try:
        print('📊 Processando requisição para /api/btc-signals/pending')
        
        if not btc_signal_manager:
            return jsonify({
                'success': False,
                'message': 'Sistema BTC não inicializado'
            }), 500
        
        # Obter sinais pendentes
        pending_signals = btc_signal_manager.get_pending_signals()
        
        return jsonify({
            'success': True,
            'data': {
                'pending_signals': pending_signals,
                'count': len(pending_signals),
                'last_updated': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            }
        })
        
    except Exception as e:
        print(f"❌ Erro ao obter sinais pendentes: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500

@btc_signals_bp.route('/download-and-reprocess', methods=['POST'])
def download_and_reprocess_signals():
    """Baixa sinais do Supabase gerados após 21:00 e reprocessa automaticamente"""
    try:
        print('📥 Iniciando download e reprocessamento de sinais do Supabase...')
        
        if not btc_signal_manager:
            return jsonify({
                'success': False,
                'error': 'Sistema BTC não inicializado'
            }), 500
        
        # Importar Supabase
        import os
        from supabase import create_client, Client
        from datetime import datetime, time
        
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_ANON_KEY')
        
        if not supabase_url or not supabase_key:
            return jsonify({
                'success': False,
                'error': 'Supabase não configurado'
            }), 500
        
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # Calcular timestamp de 21:00 de hoje
        sao_paulo_tz = pytz.timezone('America/Sao_Paulo')
        today = datetime.now(sao_paulo_tz).date()
        cutoff_time = datetime.combine(today, time(21, 0)).replace(tzinfo=sao_paulo_tz)
        cutoff_iso = cutoff_time.isoformat()
        
        print(f'🕘 Buscando sinais gerados após: {cutoff_time.strftime("%d/%m/%Y %H:%M:%S")}')
        
        # Buscar sinais do Supabase gerados após 21:00 de hoje
        query = supabase.table('signals').select('*').gte('created_at', cutoff_iso).order('created_at', desc=True)
        result = query.execute()
        
        if not result.data:
            return jsonify({
                'success': True,
                'downloaded': 0,
                'message': 'Nenhum sinal encontrado após 21:00 de hoje'
            })
        
        downloaded_count = 0
        reprocessed_count = 0
        
        # Processar cada sinal encontrado
        for signal_data in result.data:
            try:
                # Converter sinal do Supabase para formato do sistema
                formatted_signal = {
                    'id': signal_data.get('id', ''),
                    'symbol': signal_data.get('symbol', ''),
                    'type': signal_data.get('type', ''),
                    'entry_price': float(signal_data.get('entry_price', 0)),
                    'target_price': float(signal_data.get('target_price', 0)),
                    'projection_percentage': float(signal_data.get('projection_percentage', 0)),
                    'quality_score': float(signal_data.get('quality_score', 0)),
                    'signal_class': signal_data.get('signal_class', ''),
                    'created_at': signal_data.get('created_at', ''),
                    'entry_time': signal_data.get('entry_time', signal_data.get('created_at', '')),
                    'status': 'PENDING_REANALYSIS',
                    'reprocessed_at': datetime.now(sao_paulo_tz).isoformat(),
                    'original_supabase_data': signal_data
                }
                
                downloaded_count += 1
                
                # Adicionar sinal ao sistema para reprocessamento automático
                success = btc_signal_manager.add_signal_for_reanalysis(formatted_signal)
                
                if success:
                    reprocessed_count += 1
                    print(f'✅ Sinal {signal_data.get("symbol")} adicionado para reprocessamento')
                else:
                    print(f'⚠️ Falha ao adicionar sinal {signal_data.get("symbol")} para reprocessamento')
                    
            except Exception as e:
                print(f'❌ Erro ao processar sinal {signal_data.get("id", "unknown")}: {e}')
                continue
        
        print(f'📊 Download concluído: {downloaded_count} sinais baixados, {reprocessed_count} enviados para reprocessamento')
        
        return jsonify({
            'success': True,
            'downloaded': downloaded_count,
            'reprocessed': reprocessed_count,
            'message': f'{downloaded_count} sinais baixados do Supabase e {reprocessed_count} enviados para reprocessamento automático'
        })
        
    except Exception as e:
        print(f'❌ Erro no download e reprocessamento: {e}')
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

@btc_signals_bp.route('/start-monitoring', methods=['POST'])
@jwt_required
def start_monitoring():
    """Inicia o monitoramento do sistema BTC"""
    try:
        # Verificar se usuário é admin
        user_data = get_current_user()
        if not user_data or not user_data.get('is_admin'):
            return jsonify({
                'success': False,
                'message': 'Acesso negado. Apenas administradores podem iniciar o monitoramento.'
            }), 403
        
        if not btc_signal_manager:
            return jsonify({
                'success': False,
                'message': 'Sistema BTC não inicializado'
            }), 500
        
        # Verificar se já está monitorando
        if btc_signal_manager.is_monitoring:
            return jsonify({
                'success': True,
                'message': 'Monitoramento já está ativo',
                'data': {
                    'is_monitoring': True,
                    'pending_signals': len(btc_signal_manager.pending_signals),
                    'confirmed_signals': len(btc_signal_manager.confirmed_signals),
                    'rejected_signals': len(btc_signal_manager.rejected_signals)
                }
            })
        
        # Iniciar monitoramento
        success = btc_signal_manager.start_monitoring()
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Monitoramento iniciado com sucesso!',
                'data': {
                    'is_monitoring': btc_signal_manager.is_monitoring,
                    'started_by': user_data.get('email', 'admin'),
                    'started_at': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                    'pending_signals': len(btc_signal_manager.pending_signals),
                    'confirmed_signals': len(btc_signal_manager.confirmed_signals),
                    'rejected_signals': len(btc_signal_manager.rejected_signals)
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Falha ao iniciar monitoramento'
            }), 500
        
    except Exception as e:
        print(f"❌ Erro ao iniciar monitoramento: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500

@btc_signals_bp.route('/stop-monitoring', methods=['POST'])
@jwt_required
def stop_monitoring():
    """Para o monitoramento do sistema BTC"""
    try:
        # Verificar se usuário é admin
        user_data = get_current_user()
        if not user_data or not user_data.get('is_admin'):
            return jsonify({
                'success': False,
                'message': 'Acesso negado. Apenas administradores podem parar o monitoramento.'
            }), 403
        
        if not btc_signal_manager:
            return jsonify({
                'success': False,
                'message': 'Sistema BTC não inicializado'
            }), 500
        
        # Verificar se está monitorando
        if not btc_signal_manager.is_monitoring:
            return jsonify({
                'success': True,
                'message': 'Monitoramento já está parado',
                'data': {
                    'is_monitoring': False
                }
            })
        
        # Parar monitoramento
        btc_signal_manager.stop_monitoring()
        
        return jsonify({
            'success': True,
            'message': 'Monitoramento parado com sucesso!',
            'data': {
                'is_monitoring': btc_signal_manager.is_monitoring,
                'stopped_by': user_data.get('email', 'admin'),
                'stopped_at': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            }
        })
        
    except Exception as e:
        print(f"❌ Erro ao parar monitoramento: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500

@btc_signals_bp.route('/daily-status', methods=['GET'])
@jwt_required
def get_daily_signals_status():
    """Retorna status do controle de sinais confirmados diários"""
    try:
        # Verificar se usuário é admin
        user_data = get_current_user()
        if not user_data or not user_data.get('is_admin'):
            return jsonify({
                'success': False,
                'message': 'Acesso negado. Apenas administradores podem acessar esta funcionalidade.'
            }), 403
        
        if not btc_signal_manager:
            return jsonify({
                'success': False,
                'message': 'Sistema BTC não inicializado'
            }), 500
        
        # Obter informações do controle diário
        daily_count = btc_signal_manager.get_daily_confirmed_count()
        daily_list = btc_signal_manager.get_daily_confirmed_list()
        last_reset_date = btc_signal_manager.last_reset_date
        
        return jsonify({
            'success': True,
            'data': {
                'daily_confirmed_count': daily_count,
                'daily_confirmed_signals': [
                    {'symbol': signal[0], 'type': signal[1]} 
                    for signal in daily_list
                ],
                'last_reset_date': last_reset_date.strftime('%d/%m/%Y'),
                'current_date': datetime.now().strftime('%d/%m/%Y'),
                'duplicate_prevention': {
                    'enabled': True,
                    'description': 'Sinais do mesmo símbolo e tipo não podem ser confirmados mais de uma vez por dia',
                    'reset_time': '21:00 (Horário de São Paulo)'
                },
                'system_info': {
                    'pending_signals': len(btc_signal_manager.get_pending_signals()),
                    'total_confirmed': len(btc_signal_manager.get_confirmed_signals()),
                    'total_rejected': len(btc_signal_manager.get_rejected_signals())
                }
            }
        })
        
    except Exception as e:
        print(f"❌ Erro ao obter status diário: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500

# Função duplicada removida - já existe acima

@btc_signals_bp.route('/rejected', methods=['GET'])
def get_rejected_signals():
    """Retorna lista de sinais rejeitados - Rota pública para dashboard"""
    try:
        print('📊 Processando requisição para /api/btc-signals/rejected')
        
        if not btc_signal_manager:
            return jsonify({
                'success': False,
                'message': 'Sistema BTC não inicializado'
            }), 500
        
        # Obter parâmetros opcionais
        limit = request.args.get('limit', 50, type=int)
        limit = min(limit, 200)  # Máximo 200 registros
        
        # Obter sinais rejeitados
        rejected_signals = btc_signal_manager.get_rejected_signals(limit=limit)
        
        return jsonify({
            'success': True,
            'data': {
                'rejected_signals': rejected_signals,
                'count': len(rejected_signals),
                'limit': limit,
                'last_updated': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            }
        })
        
    except Exception as e:
        print(f"❌ Erro ao obter sinais rejeitados: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500

@btc_signals_bp.route('/confirmed', methods=['GET'])
def get_confirmed_signals():
    """Retorna lista de sinais confirmados (Público para dashboard, Admin para painel)"""
    try:
        # Verificar se há token de autenticação
        auth_header = request.headers.get('Authorization')
        
        # Se há token, verificar se é admin (para painel admin)
        if auth_header and auth_header.startswith('Bearer '):
            try:
                # Verificação simples de token admin
                token = auth_header.split(' ')[1]
                
                # Por enquanto, permitir acesso se há token válido
                # TODO: Implementar verificação de admin adequada
                if not token:
                    return jsonify({
                        'success': False,
                        'message': 'Acesso negado. Token inválido.'
                    }), 403
                    
                # Usuário admin autenticado - retornar formato completo
                admin_format = True
            except:
                # Token inválido - tratar como acesso público
                admin_format = False
        else:
            # Sem token - acesso público para dashboard
            admin_format = False
        
        if not btc_signal_manager:
            return jsonify({
                'success': False,
                'message': 'Sistema BTC não inicializado'
            }), 500
        
        # Obter parâmetros opcionais (sem limite padrão)
        limit = request.args.get('limit', type=int)
        if limit is not None:
            limit = min(limit, 500)  # Máximo 500 registros se especificado
        
        # Obter sinais confirmados (todos se não especificado limite)
        confirmed_signals = btc_signal_manager.get_confirmed_signals(limit=limit)
        
        if admin_format:
            # Formato completo para admin
            return jsonify({
                'success': True,
                'data': {
                    'confirmed_signals': confirmed_signals,
                    'count': len(confirmed_signals),
                    'limit': limit,
                    'last_updated': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                }
            })
        else:
            # Formato completo para dashboard público (incluindo todos os campos necessários)
            formatted_signals = []
            for signal in confirmed_signals:
                formatted_signals.append({
                    'id': signal.get('id'),
                    'symbol': signal.get('symbol'),
                    'type': signal.get('type'),
                    'entry_time': signal.get('entry_time'),
                    'entry_price': signal.get('entry_price'),
                    'target_price': signal.get('target_price'),
                    'projection_percentage': signal.get('projection_percentage'),
                    'signal_class': signal.get('signal_class', 'PADRÃO'),
                    'status': signal.get('status', 'CONFIRMED'),
                    'created_at': signal.get('created_at'),
                    'confirmed_at': signal.get('confirmed_at'),
                    'quality_score': signal.get('quality_score'),
                    'confirmation_reasons': signal.get('confirmation_reasons', []),
                    'confirmation_attempts': signal.get('confirmation_attempts', 0),
                    'btc_correlation': signal.get('btc_correlation', 0),
                    'btc_trend': signal.get('btc_trend', 'NEUTRAL')
                })
            
            return jsonify(formatted_signals)
        
    except Exception as e:
        print(f"❌ Erro ao obter sinais confirmados: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500



@btc_signals_bp.route('/metrics', methods=['GET'])
def get_btc_metrics():
    """Retorna métricas do sistema BTC - Rota pública para cards do dashboard"""
    try:
        print('📊 Processando requisição para /api/btc-signals/metrics')
        
        if not btc_signal_manager or not btc_analyzer:
            return jsonify({
                'success': False,
                'message': 'Sistema BTC não inicializado'
            }), 500
        
        # Obter métricas de confirmação
        confirmation_metrics = btc_signal_manager.get_confirmation_metrics()
        
        # Obter análise atual do BTC
        btc_analysis = btc_analyzer.get_current_btc_analysis()
        
        # Obter dados de preço do BTC
        btc_price_data = btc_analyzer.get_btc_price_data()
        
        # Converter todos os valores para tipos serializáveis
        def make_serializable(obj):
            """Converte objetos para tipos serializáveis JSON"""
            import numpy as np
            import pandas as pd
            
            if isinstance(obj, dict):
                return {k: make_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [make_serializable(item) for item in obj]
            elif isinstance(obj, tuple):
                return [make_serializable(item) for item in obj]
            elif isinstance(obj, (np.integer, np.floating)):
                return obj.item()
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, (np.bool_, bool)):
                return bool(obj)
            elif isinstance(obj, (pd.Timestamp, datetime)):
                return obj.strftime('%d/%m/%Y %H:%M:%S') if hasattr(obj, 'strftime') else str(obj)
            elif hasattr(obj, 'item'):  # outros tipos numpy
                return obj.item()
            elif isinstance(obj, (int, float, str, type(None))):
                return obj
            else:
                return str(obj)
        
        return jsonify({
            'success': True,
            'data': {
                'confirmation_metrics': make_serializable(confirmation_metrics),
                'btc_analysis': make_serializable(btc_analysis),
                'btc_price_data': make_serializable(btc_price_data),
                'system_status': {
                    'btc_manager_active': bool(btc_signal_manager.is_monitoring),
                    'last_updated': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                }
            }
        })
        
    except Exception as e:
        print(f"❌ Erro ao obter métricas BTC: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500

@btc_signals_bp.route('/confirm/<signal_id>', methods=['POST'])
@jwt_required
def confirm_signal_manually(signal_id):
    """Confirma um sinal manualmente"""
    try:
        # Verificar se usuário é admin
        user_data = get_current_user()
        if not user_data or not user_data.get('is_admin'):
            return jsonify({
                'success': False,
                'message': 'Acesso negado. Apenas administradores podem confirmar sinais.'
            }), 403
        
        if not btc_signal_manager:
            return jsonify({
                'success': False,
                'message': 'Sistema BTC não inicializado'
            }), 500
        
        # Confirmar sinal
        success = btc_signal_manager.manual_confirm_signal(signal_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Sinal {signal_id[:8]} confirmado com sucesso!',
                'data': {
                    'signal_id': signal_id,
                    'confirmed_by': user_data.get('email', 'admin'),
                    'confirmed_at': datetime.now(pytz.timezone('America/Sao_Paulo')).strftime('%d/%m/%Y %H:%M:%S')
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': f'Sinal {signal_id[:8]} não encontrado ou já processado'
            }), 404
        
    except Exception as e:
        print(f"❌ Erro ao confirmar sinal: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500

@btc_signals_bp.route('/reject/<signal_id>', methods=['POST'])
@jwt_required
def reject_signal_manually(signal_id):
    """Rejeita um sinal manualmente"""
    try:
        # Verificar se usuário é admin
        user_data = get_current_user()
        if not user_data or not user_data.get('is_admin'):
            return jsonify({
                'success': False,
                'message': 'Acesso negado. Apenas administradores podem rejeitar sinais.'
            }), 403
        
        if not btc_signal_manager:
            return jsonify({
                'success': False,
                'message': 'Sistema BTC não inicializado'
            }), 500
        
        # Obter motivo da rejeição (opcional)
        data = request.get_json() or {}
        reason = data.get('reason', 'MANUAL_REJECTION_BY_ADMIN')
        
        # Rejeitar sinal
        success = btc_signal_manager.manual_reject_signal(signal_id, reason)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Sinal {signal_id[:8]} rejeitado com sucesso!',
                'data': {
                    'signal_id': signal_id,
                    'rejected_by': user_data.get('email', 'admin'),
                    'rejected_at': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                    'reason': reason
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': f'Sinal {signal_id[:8]} não encontrado ou já processado'
            }), 404
        
    except Exception as e:
        print(f"❌ Erro ao rejeitar sinal: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500

@btc_signals_bp.route('/analysis/<symbol>', methods=['GET'])
@jwt_required
def get_symbol_btc_analysis(symbol):
    """Retorna análise detalhada de um símbolo em relação ao BTC"""
    try:
        # Verificar se usuário é admin
        user_data = get_current_user()
        if not user_data or not user_data.get('is_admin'):
            return jsonify({
                'success': False,
                'message': 'Acesso negado. Apenas administradores podem acessar esta funcionalidade.'
            }), 403
        
        if not btc_analyzer or not confirmation_system:
            return jsonify({
                'success': False,
                'message': 'Sistema BTC não inicializado'
            }), 500
        
        # Validar símbolo
        symbol = symbol.upper()
        if not symbol.endswith('USDT'):
            return jsonify({
                'success': False,
                'message': 'Símbolo deve terminar com USDT'
            }), 400
        
        # Obter correlação com BTC
        btc_correlation = btc_analyzer.calculate_symbol_btc_correlation(symbol)
        
        # Obter análise atual do BTC
        btc_analysis = btc_analyzer.get_current_btc_analysis()
        
        # Obter thresholds do sistema de confirmação
        confirmation_thresholds = confirmation_system.get_confirmation_thresholds()
        
        return jsonify({
            'success': True,
            'data': {
                'symbol': symbol,
                'btc_correlation': btc_correlation,
                'btc_analysis': btc_analysis,
                'confirmation_thresholds': confirmation_thresholds,
                'analysis_timestamp': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            }
        })
        
    except Exception as e:
        print(f"❌ Erro na análise do símbolo {symbol}: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500

@btc_signals_bp.route('/config', methods=['GET'])
@jwt_required
def get_btc_config():
    """Retorna configurações do sistema BTC"""
    try:
        # Verificar se usuário é admin
        user_data = get_current_user()
        if not user_data or not user_data.get('is_admin'):
            return jsonify({
                'success': False,
                'message': 'Acesso negado. Apenas administradores podem acessar esta funcionalidade.'
            }), 403
        
        if not btc_signal_manager or not confirmation_system:
            return jsonify({
                'success': False,
                'message': 'Sistema BTC não inicializado'
            }), 500
        
        # Obter configurações
        btc_config = btc_signal_manager.config
        confirmation_thresholds = confirmation_system.get_confirmation_thresholds()
        
        return jsonify({
            'success': True,
            'data': {
                'btc_signal_manager_config': btc_config,
                'confirmation_system_config': confirmation_thresholds,
                'system_info': {
                    'version': '1.0',
                    'last_updated': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                }
            }
        })
        
    except Exception as e:
        print(f"❌ Erro ao obter configurações BTC: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500

@btc_signals_bp.route('/config', methods=['PUT'])
@jwt_required
def update_btc_config():
    """Atualiza configurações do sistema BTC"""
    try:
        # Verificar se usuário é admin
        user_data = get_current_user()
        if not user_data or not user_data.get('is_admin'):
            return jsonify({
                'success': False,
                'message': 'Acesso negado. Apenas administradores podem alterar configurações.'
            }), 403
        
        if not confirmation_system:
            return jsonify({
                'success': False,
                'message': 'Sistema BTC não inicializado'
            }), 500
        
        # Obter dados da requisição
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'Dados não fornecidos'
            }), 400
        
        # Atualizar thresholds se fornecidos
        if 'confirmation_thresholds' in data:
            success = confirmation_system.update_confirmation_thresholds(
                data['confirmation_thresholds']
            )
            
            if not success:
                return jsonify({
                    'success': False,
                    'message': 'Erro ao atualizar thresholds'
                }), 500
        
        return jsonify({
            'success': True,
            'message': 'Configurações atualizadas com sucesso!',
            'data': {
                'updated_by': user_data.get('email', 'admin'),
                'updated_at': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            }
        })
        
    except Exception as e:
        print(f"❌ Erro ao atualizar configurações BTC: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500

@btc_signals_bp.route('/status', methods=['GET'])
@jwt_required
def get_system_status():
    """Retorna status geral do sistema BTC"""
    try:
        # Verificar se usuário é admin
        user_data = get_current_user()
        if not user_data or not user_data.get('is_admin'):
            return jsonify({
                'success': False,
                'message': 'Acesso negado. Apenas administradores podem acessar esta funcionalidade.'
            }), 403
        
        status_data = {
            'btc_signal_manager': {
                'initialized': btc_signal_manager is not None,
                'monitoring': btc_signal_manager.is_monitoring if btc_signal_manager else False,
                'pending_count': len(btc_signal_manager.pending_signals) if btc_signal_manager else 0
            },
            'confirmation_system': {
                'initialized': confirmation_system is not None
            },
            'btc_analyzer': {
                'initialized': btc_analyzer is not None
            },
            'system_timestamp': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        }
        
        return jsonify({
            'success': True,
            'data': status_data
        })
        
    except Exception as e:
        print(f"❌ Erro ao obter status do sistema: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500

# Rota de teste para verificar se o sistema está funcionando
@btc_signals_bp.route('/test', methods=['GET'])
@jwt_required
def test_btc_system():
    """Testa o sistema BTC"""
    try:
        # Verificar se usuário é admin
        user_data = get_current_user()
        if not user_data or not user_data.get('is_admin'):
            return jsonify({
                'success': False,
                'message': 'Acesso negado. Apenas administradores podem acessar esta funcionalidade.'
            }), 403
        
        test_results = {
            'btc_signal_manager': 'OK' if btc_signal_manager else 'NOT_INITIALIZED',
            'confirmation_system': 'OK' if confirmation_system else 'NOT_INITIALIZED',
            'btc_analyzer': 'OK' if btc_analyzer else 'NOT_INITIALIZED',
            'test_timestamp': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        }
        
        all_ok = all(status == 'OK' for status in test_results.values() if status != test_results['test_timestamp'])
        
        return jsonify({
            'success': all_ok,
            'message': 'Sistema BTC funcionando corretamente!' if all_ok else 'Alguns componentes não estão inicializados',
            'data': test_results
        })
        
    except Exception as e:
        print(f"❌ Erro no teste do sistema BTC: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500