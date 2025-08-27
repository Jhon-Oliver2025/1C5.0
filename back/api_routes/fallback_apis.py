#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APIs de Fallback para garantir que endpoints essenciais sempre respondam
Evita erros 503 e ERR_CONNECTION_CLOSED no frontend
"""

from flask import Blueprint, jsonify, current_app
from datetime import datetime
import time
import os

fallback_bp = Blueprint('fallback', __name__)

# Cache simples para respostas
_cache = {
    'last_update': None,
    'market_status': None,
    'btc_metrics': None,
    'cleanup_status': None
}

@fallback_bp.route('/api/status', methods=['GET'])
def fallback_status():
    """Status básico sempre disponível"""
    try:
        # Verificar se o bot está disponível
        bot_status = 'running'
        if hasattr(current_app, 'bot_instance'):
            try:
                bot = current_app.bot_instance
                if hasattr(bot, 'get_status'):
                    bot_status = bot.get_status().get('bot', 'running')
            except:
                bot_status = 'degraded'
        
        return jsonify({
            'status': 'online',
            'bot': bot_status,
            'timestamp': datetime.now().isoformat(),
            'uptime': time.time() - getattr(current_app, 'start_time', time.time()),
            'version': '2.0.0',
            'mode': 'fallback' if bot_status == 'degraded' else 'normal'
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'online',
            'bot': 'error',
            'timestamp': datetime.now().isoformat(),
            'error': str(e),
            'mode': 'emergency'
        }), 200  # Sempre retorna 200 para manter frontend funcionando

@fallback_bp.route('/api/market-status', methods=['GET'])
def fallback_market_status():
    """Status do mercado com fallback"""
    try:
        # Tentar obter dados reais primeiro
        if hasattr(current_app, 'bot_instance'):
            try:
                bot = current_app.bot_instance
                if hasattr(bot, 'btc_signal_manager') and bot.btc_signal_manager:
                    if hasattr(bot.btc_signal_manager, 'btc_analyzer'):
                        analyzer = bot.btc_signal_manager.btc_analyzer
                        if hasattr(analyzer, 'get_market_status'):
                            real_data = analyzer.get_market_status()
                            if real_data:
                                _cache['market_status'] = real_data
                                _cache['last_update'] = datetime.now()
                                return jsonify({
                                    'success': True,
                                    'data': real_data,
                                    'timestamp': datetime.now().isoformat(),
                                    'source': 'real'
                                }), 200
            except Exception as e:
                print(f"⚠️ Erro ao obter dados reais do mercado: {e}")
        
        # Fallback para dados simulados
        current_hour = datetime.now().hour
        
        # Simular status baseado no horário
        ny_status = 'open' if 9 <= current_hour <= 16 else 'closed'
        asia_status = 'open' if 21 <= current_hour or current_hour <= 5 else 'closed'
        
        fallback_data = {
            'new_york': {
                'status': ny_status,
                'time': f"{current_hour:02d}:00",
                'timezone': 'EST'
            },
            'asia': {
                'status': asia_status,
                'time': f"{(current_hour + 12) % 24:02d}:00",
                'timezone': 'JST'
            },
            'crypto': {
                'status': 'open',
                'time': '24/7',
                'timezone': 'UTC'
            }
        }
        
        return jsonify({
            'success': True,
            'data': fallback_data,
            'timestamp': datetime.now().isoformat(),
            'source': 'fallback'
        }), 200
        
    except Exception as e:
        # Fallback de emergência
        return jsonify({
            'success': True,
            'data': {
                'new_york': {'status': 'unknown', 'time': '00:00'},
                'asia': {'status': 'unknown', 'time': '00:00'},
                'crypto': {'status': 'open', 'time': '24/7'}
            },
            'timestamp': datetime.now().isoformat(),
            'source': 'emergency',
            'error': str(e)
        }), 200

@fallback_bp.route('/api/btc-signals/metrics', methods=['GET'])
def fallback_btc_metrics():
    """Métricas BTC com fallback"""
    try:
        # Tentar obter dados reais
        if hasattr(current_app, 'bot_instance'):
            try:
                bot = current_app.bot_instance
                if hasattr(bot, 'btc_signal_manager') and bot.btc_signal_manager:
                    manager = bot.btc_signal_manager
                    if hasattr(manager, 'get_metrics'):
                        real_metrics = manager.get_metrics()
                        if real_metrics:
                            _cache['btc_metrics'] = real_metrics
                            _cache['last_update'] = datetime.now()
                            return jsonify({
                                'success': True,
                                'data': real_metrics,
                                'timestamp': datetime.now().isoformat(),
                                'source': 'real'
                            }), 200
            except Exception as e:
                print(f"⚠️ Erro ao obter métricas BTC reais: {e}")
        
        # Fallback para métricas simuladas
        fallback_metrics = {
            'pending_signals': 0,
            'confirmed_signals': 0,
            'confirmation_rate': 85.0,
            'average_confirmation_time': 25.0,
            'btc_trend': 'NEUTRAL',
            'market_sentiment': 'NEUTRAL',
            'last_update': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'data': fallback_metrics,
            'timestamp': datetime.now().isoformat(),
            'source': 'fallback'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'data': {},
            'timestamp': datetime.now().isoformat(),
            'source': 'emergency',
            'error': str(e)
        }), 200  # Sempre 200 para não quebrar frontend

@fallback_bp.route('/api/cleanup-status', methods=['GET'])
def fallback_cleanup_status():
    """Status de limpeza com fallback"""
    try:
        # Dados básicos de limpeza
        cleanup_data = {
            'last_cleanup': datetime.now().isoformat(),
            'signals_cleaned': 0,
            'status': 'active',
            'next_cleanup': datetime.now().isoformat(),
            'cleanup_interval': '1h'
        }
        
        return jsonify({
            'success': True,
            'data': cleanup_data,
            'timestamp': datetime.now().isoformat(),
            'source': 'fallback'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'data': {},
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }), 200

@fallback_bp.route('/api/signals', methods=['GET'])
def fallback_signals():
    """Sinais com fallback"""
    try:
        # Tentar obter sinais reais do Supabase
        try:
            from api_routes.auth_supabase import supabase_auth
            if supabase_auth and supabase_auth.is_available:
                import requests
                response = requests.get(
                    f"{supabase_auth.supabase_url}/rest/v1/signals?order=created_at.desc&limit=50",
                    headers=supabase_auth.headers,
                    timeout=5
                )
                if response.status_code == 200:
                    signals = response.json()
                    return jsonify({
                        'success': True,
                        'signals': signals,
                        'count': len(signals),
                        'timestamp': datetime.now().isoformat(),
                        'source': 'supabase'
                    }), 200
        except Exception as e:
            print(f"⚠️ Erro ao obter sinais do Supabase: {e}")
        
        # Fallback para lista vazia
        return jsonify({
            'success': True,
            'signals': [],
            'count': 0,
            'timestamp': datetime.now().isoformat(),
            'source': 'fallback',
            'message': 'Nenhum sinal disponível no momento'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'signals': [],
            'count': 0,
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }), 200

@fallback_bp.route('/api/fallback/status', methods=['GET'])
def fallback_system_status():
    """Status do sistema de fallback"""
    return jsonify({
        'fallback_active': True,
        'cache_status': {
            'last_update': _cache.get('last_update'),
            'market_status_cached': _cache.get('market_status') is not None,
            'btc_metrics_cached': _cache.get('btc_metrics') is not None
        },
        'endpoints_available': [
            '/api/status',
            '/api/market-status',
            '/api/btc-signals/metrics',
            '/api/cleanup-status',
            '/api/signals'
        ],
        'timestamp': datetime.now().isoformat()
    }), 200

def init_fallback_routes(app):
    """Inicializa as rotas de fallback"""
    app.register_blueprint(fallback_bp)
    
    # Registrar timestamp de início
    app.start_time = time.time()
    
    print("🛡️ Sistema de Fallback APIs inicializado")
    print("📡 Endpoints de fallback disponíveis:")
    print("   • /api/status")
    print("   • /api/market-status")
    print("   • /api/btc-signals/metrics")
    print("   • /api/cleanup-status")
    print("   • /api/signals")