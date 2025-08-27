from flask import Blueprint, request, jsonify, current_app
import bcrypt
import uuid
import requests
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Criar blueprint para autenticação com Supabase
auth_supabase_bp = Blueprint('auth_supabase', __name__)

class SupabaseAuth:
    """
    Classe para autenticação usando Supabase diretamente
    """
    
    def __init__(self):
        """Inicializa a autenticação Supabase"""
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_anon_key = os.getenv('SUPABASE_ANON_KEY')
        
        if not self.supabase_url or not self.supabase_anon_key:
            raise ValueError("Variáveis SUPABASE_URL e SUPABASE_ANON_KEY são obrigatórias")
        
        self.headers = {
            'apikey': self.supabase_anon_key,
            'Authorization': f'Bearer {self.supabase_anon_key}',
            'Content-Type': 'application/json'
        }
    
    def get_user_by_email(self, email: str) -> dict:
        """Busca usuário por email no Supabase"""
        try:
            response = requests.get(
                f"{self.supabase_url}/rest/v1/users?email=eq.{email}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                users = response.json()
                return users[0] if users else None
            else:
                return None
                
        except Exception as e:
            current_app.logger.error(f"Erro ao buscar usuário: {e}")
            return None
    
    def create_auth_session(self, user_id: str) -> str:
        """Cria uma sessão de autenticação simples"""
        try:
            # Gerar token único
            token = str(uuid.uuid4())
            
            # Para simplicidade, vamos usar um sistema de token em memória
            # Em produção, isso deveria ser armazenado no Redis ou banco
            if not hasattr(current_app, 'auth_sessions'):
                current_app.auth_sessions = {}
            
            current_app.auth_sessions[token] = {
                'user_id': user_id,
                'created_at': datetime.now(),
                'expires_at': datetime.now() + timedelta(hours=24)
            }
            
            return token
            
        except Exception as e:
            current_app.logger.error(f"Erro ao criar sessão: {e}")
            return None
    
    def validate_token(self, token: str) -> dict:
        """Valida token de autenticação"""
        try:
            if not hasattr(current_app, 'auth_sessions'):
                return None
            
            session = current_app.auth_sessions.get(token)
            if not session:
                return None
            
            # Verificar se token expirou
            if datetime.now() > session['expires_at']:
                del current_app.auth_sessions[token]
                return None
            
            return session
            
        except Exception as e:
            current_app.logger.error(f"Erro ao validar token: {e}")
            return None
    
    def save_signal_to_supabase(self, signal_data: dict) -> bool:
        """Salva sinal no Supabase"""
        try:
            # Adaptar dados para a estrutura da tabela signals
            supabase_signal = {
                'symbol': signal_data.get('symbol'),
                'type': signal_data.get('type'),
                'entry_price': float(signal_data.get('entry_price', 0)),
                'target_price': float(signal_data.get('target_price', 0)),
                'entry_time': signal_data.get('timestamp', datetime.now().isoformat()),
                'status': signal_data.get('status', 'pending'),
                'quality_score': float(signal_data.get('quality_score', 0)),
                'signal_class': signal_data.get('signal_class'),
                'trend_score': float(signal_data.get('trend_score', 0)),
                'rsi_score': float(signal_data.get('rsi_score', 0)),
                'timeframe': signal_data.get('entry_timeframe', '1h')
            }
            
            response = requests.post(
                f"{self.supabase_url}/rest/v1/signals",
                headers=self.headers,
                json=supabase_signal
            )
            
            if response.status_code in [200, 201]:
                current_app.logger.info(f"Sinal salvo no Supabase: {signal_data['symbol']}")
                return True
            else:
                current_app.logger.error(f"Erro ao salvar sinal: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            current_app.logger.error(f"Erro ao salvar sinal no Supabase: {e}")
            return False

# Instância global
supabase_auth = SupabaseAuth()

@auth_supabase_bp.route('/login', methods=['POST'])
def login_supabase():
    """Endpoint para login usando Supabase"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400
            
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        # Validação
        if not username or not password:
            return jsonify({'error': 'Username e senha são obrigatórios'}), 400
        
        # Buscar usuário no Supabase (assumindo que username é email)
        user = supabase_auth.get_user_by_email(username)
        
        if not user:
            # Delay para prevenir ataques de timing
            import time
            time.sleep(0.1)
            return jsonify({'error': 'Credenciais inválidas'}), 401
        
        # Verificar senha
        stored_password = user.get('password', '')
        password_valid = False
        
        if stored_password.startswith('$2b$'):
            # Hash bcrypt
            password_valid = bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8'))
        else:
            # Texto plano (compatibilidade)
            password_valid = (password == stored_password)
        
        if not password_valid:
            import time
            time.sleep(0.1)
            return jsonify({'error': 'Credenciais inválidas'}), 401
        
        # Verificar se é admin
        if not user.get('is_admin', False):
            return jsonify({'error': 'Acesso negado. Apenas administradores podem acessar.'}), 403
        
        # Criar sessão
        token = supabase_auth.create_auth_session(user['id'])
        
        if not token:
            return jsonify({'error': 'Erro ao criar sessão'}), 500
        
        # Resposta de sucesso
        user_data = {
            'id': user['id'],
            'email': user['email'],
            'is_admin': bool(user.get('is_admin', False))
        }
        
        current_app.logger.info(f"Login bem-sucedido para: {user['email']}")
        
        return jsonify({
            'success': True,
            'message': 'Login realizado com sucesso',
            'token': token,
            'user': user_data
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro no login Supabase: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@auth_supabase_bp.route('/logout', methods=['POST'])
def logout_supabase():
    """Endpoint para logout"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Token não fornecido'}), 401
        
        token = auth_header.split(' ')[1]
        
        # Remover sessão
        if hasattr(current_app, 'auth_sessions') and token in current_app.auth_sessions:
            del current_app.auth_sessions[token]
        
        return jsonify({
            'success': True,
            'message': 'Logout realizado com sucesso'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro no logout: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@auth_supabase_bp.route('/verify', methods=['GET'])
def verify_token():
    """Verifica se o token é válido"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Token não fornecido'}), 401
        
        token = auth_header.split(' ')[1]
        session = supabase_auth.validate_token(token)
        
        if not session:
            return jsonify({'error': 'Token inválido ou expirado'}), 401
        
        # Buscar dados atualizados do usuário
        user = supabase_auth.get_user_by_email('jonatasprojetos2013@gmail.com')  # Simplificado para admin
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        user_data = {
            'id': user['id'],
            'email': user['email'],
            'is_admin': bool(user.get('is_admin', False))
        }
        
        return jsonify({
            'success': True,
            'user': user_data
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro na verificação: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

# Função para salvar sinais no Supabase
def save_signal_to_supabase(signal_data: dict) -> bool:
    """Função global para salvar sinais no Supabase"""
    return supabase_auth.save_signal_to_supabase(signal_data)