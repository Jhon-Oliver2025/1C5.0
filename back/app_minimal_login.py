#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Servidor Flask Mínimo para Teste de Login
Apenas funcionalidades essenciais para autenticação
"""

import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import datetime

# Carregar variáveis de ambiente
load_dotenv()

# Importar configurações do Supabase
from supabase_config import supabase_config

# Criar aplicação Flask
app = Flask(__name__)

# Configurar CORS
CORS(app, resources={
    r"/api/*": {
        "origins": ["*"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Configurações
app.config['JWT_SECRET'] = os.getenv('JWT_SECRET', 'dev_jwt_secret_key_for_testing')

print("\n🚀 === SERVIDOR FLASK MÍNIMO PARA LOGIN ===")
print(f"📅 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"🔧 Supabase configurado: {'✅ Sim' if supabase_config.is_configured else '❌ Não'}")
print("🚀 === INICIANDO SERVIDOR MÍNIMO ===")

# Importar apenas as rotas de autenticação
try:
    from api_routes.auth_supabase import auth_supabase_bp
    app.register_blueprint(auth_supabase_bp, url_prefix='/api/auth')
    print("✅ Rotas de autenticação registradas")
except Exception as e:
    print(f"❌ Erro ao registrar rotas de auth: {e}")

# Importar rotas de pagamentos para checkout
try:
    from api_routes.payments import payments_bp
    app.register_blueprint(payments_bp, url_prefix='/api/payments')
    print("✅ Rotas de pagamentos registradas")
except Exception as e:
    print(f"❌ Erro ao registrar rotas de payments: {e}")

# Importar rotas de sinais
try:
    from api_routes.signals import signals_bp
    app.register_blueprint(signals_bp, url_prefix='/api')
    print("✅ Rotas de sinais registradas")
except Exception as e:
    print(f"❌ Erro ao registrar rotas de signals: {e}")

# Rota de status básica
@app.route('/api/status', methods=['GET'])
def status():
    """Rota de status básica"""
    return jsonify({
        'status': 'online',
        'service': 'minimal-login-server',
        'timestamp': datetime.now().isoformat(),
        'supabase_configured': supabase_config.is_configured
    })

# Rota de health check
@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

# Rota de configuração do Mercado Pago (mock para desenvolvimento)
@app.route('/api/payments/config', methods=['GET'])
def payment_config():
    """Configuração do Mercado Pago"""
    return jsonify({
        'config': {
            'public_key': os.getenv('MERCADO_PAGO_PUBLIC_KEY', 'TEST-mock-public-key-for-development')
        }
    })

# Rota de sinais mock para desenvolvimento
@app.route('/api/signals', methods=['GET'])
@app.route('/api/signals/', methods=['GET'])
def signals_mock():
    """Sinais mock para desenvolvimento"""
    return jsonify([
        {
            "symbol": "BTCUSDT",
            "type": "LONG",
            "entry_price": 50000.0,
            "entry_time": "2025-08-29T23:00:00",
            "target_price": 52000.0,
            "projection_percentage": 4.0,
            "status": "CONFIRMADO",
            "quality_score": 8.5,
            "signal_class": "PREMIUM"
        },
        {
            "symbol": "ETHUSDT",
            "type": "SHORT",
            "entry_price": 3000.0,
            "entry_time": "2025-08-29T22:30:00",
            "target_price": 2850.0,
            "projection_percentage": -5.0,
            "status": "CONFIRMADO",
            "quality_score": 7.8,
            "signal_class": "ELITE"
        }
    ])

if __name__ == '__main__':
    # Configurações do servidor
    port = int(os.getenv('FLASK_PORT', 5000))
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    print(f"\n🌐 Servidor mínimo iniciando em {host}:{port}")
    print(f"🔧 Debug mode: {debug}")
    print(f"🗄️ Database: Supabase (mínimo)")
    print(f"🎯 Funcionalidades: Login + Checkout")
    
    try:
        app.run(
            host=host,
            port=port,
            debug=debug,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n👋 Encerrando servidor mínimo...")
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")