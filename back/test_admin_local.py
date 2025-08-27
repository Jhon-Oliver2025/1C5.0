#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste local para verificação de admin
"""

from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:3000"], "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"], "allow_headers": ["Content-Type", "Authorization"], "supports_credentials": True}})

@app.route('/')
def index():
    return {"message": "API local de teste funcionando!"}, 200

@app.route('/api/auth/check-admin', methods=['GET'])
def check_admin():
    """Rota de teste que sempre retorna admin=true para jonatasprojetos2013@gmail.com"""
    try:
        # Para teste local, sempre retornar admin=true
        return jsonify({
            'is_admin': True,
            'user': {
                'id': 'test-user-id',
                'email': 'jonatasprojetos2013@gmail.com',
                'name': 'Admin Local'
            }
        }), 200
        
    except Exception as e:
        return jsonify({'is_admin': False, 'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Rota de login de teste"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        # Para teste, aceitar apenas as credenciais específicas
        if email == 'jonatasprojetos2013@gmail.com' and password == 'admin123':
            return jsonify({
                'token': 'test-admin-token-12345',
                'user': {
                    'id': 'test-user-id',
                    'email': email,
                    'name': 'Admin Local'
                }
            }), 200
        else:
            return jsonify({'error': 'Credenciais inválidas'}), 401
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/signals', methods=['GET'])
def get_signals():
    """Rota de sinais de teste"""
    return jsonify({
        'success': True,
        'signals': [
            {
                'id': 1,
                'symbol': 'BTCUSDT',
                'type': 'COMPRA',
                'price': 45000,
                'created_at': '2025-08-27T10:00:00Z'
            },
            {
                'id': 2,
                'symbol': 'ETHUSDT',
                'type': 'VENDA',
                'price': 3000,
                'created_at': '2025-08-27T10:05:00Z'
            }
        ]
    }), 200

@app.route('/api/market-status', methods=['GET'])
def market_status():
    """Rota de status do mercado de teste"""
    return jsonify({
        'success': True,
        'data': {
            'new_york': {'status': 'open', 'time': '10:00'},
            'asia': {'status': 'closed', 'time': '22:00'}
        }
    }), 200

if __name__ == '__main__':
    print("🚀 Iniciando servidor de teste local...")
    print("📍 URL: http://localhost:5001")
    print("🔐 Admin: jonatasprojetos2013@gmail.com / admin123")
    app.run(host='0.0.0.0', port=5001, debug=True)