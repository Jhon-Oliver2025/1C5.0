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
        
        # Modo tolerante - não falhar se variáveis não estiverem disponíveis
        self.is_available = bool(self.supabase_url and self.supabase_anon_key)
        
        if self.is_available:
            self.headers = {
                'apikey': self.supabase_anon_key,
                'Authorization': f'Bearer {self.supabase_anon_key}',
                'Content-Type': 'application/json'
            }
            print("✅ Supabase Auth inicializado com sucesso")
            print(f"DEBUG: SUPABASE_URL: {self.supabase_url}")
            print(f"DEBUG: SUPABASE_ANON_KEY: {self.supabase_anon_key[:5]}...") # Evitar expor a chave completa
        else:
            self.headers = {}
            print("⚠️ Supabase Auth não disponível - variáveis de ambiente ausentes")
            print(f"DEBUG: SUPABASE_URL: {self.supabase_url}")
            print(f"DEBUG: SUPABASE_ANON_KEY: {self.supabase_anon_key}")
    
    def get_user_by_email(self, email: str) -> dict:
        """Busca usuário por email no Supabase"""
        if not self.is_available:
            return None
            
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
        if not self.is_available:
            return False
            
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

# Instância global - modo tolerante
try:
    supabase_auth = SupabaseAuth()
except Exception as e:
    print(f"⚠️ Erro ao inicializar Supabase Auth: {e}")
    supabase_auth = None

@auth_supabase_bp.route('/login', methods=['POST'])
def login_supabase():
    """Endpoint para login usando Supabase"""
    try:
        # Verificar se Supabase está disponível
        if not supabase_auth or not supabase_auth.is_available:
            return jsonify({'error': 'Serviço de autenticação temporariamente indisponível'}), 503
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400
            
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        # Validação
        if not email or not password:
            return jsonify({'error': 'Email e senha são obrigatórios'}), 400
        
        # Tentar fazer login com Supabase Auth
        try:
            response = requests.post(
                f"{supabase_auth.supabase_url}/auth/v1/token?grant_type=password",
                headers=supabase_auth.headers,
                json={
                    "email": email,
                    "password": password
                }
            )
            response.raise_for_status() # Levanta HTTPError para status de erro (4xx ou 5xx)
            
            supabase_user_data = response.json()
            access_token = supabase_user_data['access_token']
            refresh_token = supabase_user_data['refresh_token']
            user_id = supabase_user_data['user']['id']
            user_email = supabase_user_data['user']['email']

            # Opcional: Você pode buscar mais detalhes do perfil do usuário aqui se necessário
            # Ex: user_profile = supabase_auth.get_user_profile_from_db(user_id)

            # Criar sessão local (se ainda for necessário para o backend)
            token = supabase_auth.create_auth_session(user_id)
            
            if not token:
                return jsonify({'error': 'Erro ao criar sessão local'}), 500

            return jsonify({
                'success': True,
                'message': 'Login realizado com sucesso via Supabase',
                'token': token, # Token da sessão local
                'access_token': access_token, # Token de acesso do Supabase
                'refresh_token': refresh_token, # Refresh token do Supabase
                'user': {
                    'id': user_id,
                    'email': user_email,
                    # Adicione outros campos do usuário Supabase se necessário
                }
            }), 200

        except requests.exceptions.HTTPError as http_err:
            current_app.logger.error(f"HTTP error occurred during Supabase login: {http_err} - {http_err.response.text}")
            if http_err.response.status_code == 400: # Bad Request, geralmente credenciais inválidas
                return jsonify({'error': 'Credenciais inválidas'}), 401
            return jsonify({'error': 'Erro na autenticação com Supabase'}), 500
        except Exception as e:
            current_app.logger.error(f"Erro inesperado durante Supabase login: {e}")
            return jsonify({'error': 'Erro interno do servidor'}), 500
    except Exception as e:
        current_app.logger.error(f"Erro geral na função login_supabase: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@auth_supabase_bp.route('/logout', methods=['POST'])
def logout_supabase():
    """Endpoint para logout de usuários do Supabase"""
    try:
        # Verificar se Supabase está disponível
        if not supabase_auth or not supabase_auth.is_available:
            return jsonify({'error': 'Serviço de autenticação temporariamente indisponível'}), 503

        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Token não fornecido'}), 401

        local_token = auth_header.split(' ')[1]

        # Remover token da sessão local
        if hasattr(current_app, 'auth_sessions') and local_token in current_app.auth_sessions:
            del current_app.auth_sessions[local_token]

        # Opcional: Invalidar sessão no Supabase (se houver um endpoint para isso)
        # Supabase geralmente invalida tokens após um tempo ou se o refresh token for usado
        # Para logout explícito, o cliente deve descartar os tokens do Supabase.

        return jsonify({
            'success': True,
            'message': 'Logout realizado com sucesso'
        }), 200

    except Exception as e:
        current_app.logger.error(f"Erro no logout do Supabase: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@auth_supabase_bp.route('/register', methods=['POST'])
def register_supabase():
    """Endpoint para registro de usuários via Supabase Auth"""
    try:
        # Verificar se Supabase está disponível
        if not supabase_auth or not supabase_auth.is_available:
            return jsonify({'error': 'Serviço de registro temporariamente indisponível'}), 503

        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400

        email = data.get('email')
        password = data.get('password')

        if not all([email, password]):
            return jsonify({'error': 'Email e senha são obrigatórios'}), 400

        # Chamar a API de registro do Supabase
        response = requests.post(
            f"{supabase_auth.supabase_url}/auth/v1/signup",
            headers=supabase_auth.headers,
            json={
                "email": email,
                "password": password
            }
        )
        response.raise_for_status() # Levanta HTTPError para status de erro (4xx ou 5xx)

        # Supabase retorna o usuário e tokens após o registro bem-sucedido
        # Dependendo da configuração do Supabase, pode ser necessário verificar o email
        return jsonify({
            'success': True,
            'message': 'Registro realizado com sucesso! Verifique seu email para confirmar sua conta.'
        }), 201

    except requests.exceptions.HTTPError as http_err:
        current_app.logger.error(f"HTTP error occurred during Supabase registration: {http_err} - {http_err.response.text}")
        if http_err.response.status_code == 422: # Unprocessable Entity, geralmente email já existe ou senha fraca
            return jsonify({'error': 'Email já cadastrado ou senha inválida'}), 409
        return jsonify({'error': 'Erro no registro com Supabase'}), 500
    except Exception as e:
        current_app.logger.error(f"Erro inesperado durante Supabase registration: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@auth_supabase_bp.route('/verify', methods=['POST'])
def verify_supabase():
    """Endpoint para verificar token de autenticação do Supabase"""
    try:
        # Verificar se Supabase está disponível
        if not supabase_auth or not supabase_auth.is_available:
            return jsonify({'error': 'Serviço de verificação temporariamente indisponível'}), 503

        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Token não fornecido'}), 401

        # O token aqui deve ser o access_token do Supabase, não o local_token
        supabase_access_token = auth_header.split(' ')[1]

        # Supabase não tem um endpoint direto para 'verificar' um token de acesso
        # A verificação é feita implicitamente ao usar o token em requisições protegidas
        # No entanto, podemos tentar obter o usuário a partir do token para validar
        # Isso geralmente é feito no lado do cliente ou em um middleware

        # Para simular uma verificação, podemos tentar obter o usuário logado
        # Isso requer o token de acesso do Supabase
        response = requests.get(
            f"{supabase_auth.supabase_url}/auth/v1/user",
            headers={
                'apikey': supabase_auth.supabase_anon_key,
                'Authorization': f'Bearer {supabase_access_token}',
                'Content-Type': 'application/json'
            }
        )
        response.raise_for_status() # Levanta HTTPError para status de erro (4xx ou 5xx)

        user_data = response.json()

        return jsonify({
            'success': True,
            'message': 'Token válido',
            'user': user_data
        }), 200

    except requests.exceptions.HTTPError as http_err:
        current_app.logger.error(f"HTTP error occurred during Supabase token verification: {http_err} - {http_err.response.text}")
        if http_err.response.status_code == 401: # Unauthorized
            return jsonify({'error': 'Token inválido ou expirado'}), 401
        return jsonify({'error': 'Erro na verificação do token com Supabase'}), 500
    except Exception as e:
        current_app.logger.error(f"Erro inesperado durante Supabase token verification: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@auth_supabase_bp.route('/refresh-token', methods=['POST'])
def refresh_token_supabase():
    """Endpoint para refrescar token de autenticação do Supabase"""
    try:
        # Verificar se Supabase está disponível
        if not supabase_auth or not supabase_auth.is_available:
            return jsonify({'error': 'Serviço de refresh de token temporariamente indisponível'}), 503

        data = request.get_json()
        if not data or not data.get('refresh_token'):
            return jsonify({'error': 'Refresh token não fornecido'}), 400

        refresh_token = data.get('refresh_token')

        response = requests.post(
            f"{supabase_auth.supabase_url}/auth/v1/token?grant_type=refresh_token",
            headers=supabase_auth.headers,
            json={
                "refresh_token": refresh_token
            }
        )
        response.raise_for_status() # Levanta HTTPError para status de erro (4xx ou 5xx)

        supabase_token_data = response.json()

        return jsonify({
            'success': True,
            'message': 'Token refrescado com sucesso',
            'access_token': supabase_token_data['access_token'],
            'refresh_token': supabase_token_data['refresh_token'],
            'expires_in': supabase_token_data['expires_in']
        }), 200

    except requests.exceptions.HTTPError as http_err:
        current_app.logger.error(f"HTTP error occurred during Supabase token refresh: {http_err} - {http_err.response.text}")
        if http_err.response.status_code == 400: # Bad Request, geralmente refresh token inválido
            return jsonify({'error': 'Refresh token inválido ou expirado'}), 401
        return jsonify({'error': 'Erro ao refrescar token com Supabase'}), 500
    except Exception as e:
        current_app.logger.error(f"Erro inesperado durante Supabase token refresh: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

# Adicionar rota para salvar sinal no Supabase (exemplo de uso da classe SupabaseAuth)
@auth_supabase_bp.route('/save-signal', methods=['POST'])
def save_signal_route():
    """Endpoint para salvar um sinal no Supabase"""
    try:
        if not supabase_auth or not supabase_auth.is_available:
            return jsonify({'error': 'Serviço Supabase indisponível'}), 503

        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400

        if supabase_auth.save_signal_to_supabase(data):
            return jsonify({'success': True, 'message': 'Sinal salvo com sucesso no Supabase'}), 200
        else:
            return jsonify({'error': 'Falha ao salvar sinal no Supabase'}), 500

    except Exception as e:
        current_app.logger.error(f"Erro na rota save-signal: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

# Rota para verificar se o usuário é administrador
@auth_supabase_bp.route('/check-admin', methods=['GET'])
def check_admin():
    """Verifica se o usuário atual é administrador"""
    try:
        if not supabase_auth or not supabase_auth.is_available:
            return jsonify({'is_admin': False, 'error': 'Serviço Supabase indisponível'}), 503

        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'is_admin': False, 'error': 'Token não fornecido'}), 401

        token = auth_header.split(' ')[1]

        # Primeiro, tentar validar como token local (UUID)
        session = supabase_auth.validate_token(token)
        if session:
            # Token local válido - buscar usuário por ID
            user_id = session['user_id']
            
            # Tentar obter dados do usuário do Supabase usando o user_id
            try:
                response = requests.get(
                    f"{supabase_auth.supabase_url}/rest/v1/users?id=eq.{user_id}",
                    headers=supabase_auth.headers
                )
                
                if response.ok:
                    users = response.json()
                    if users:
                        user_email = users[0].get('email', '')
                        is_admin = user_email == 'jonatasprojetos2013@gmail.com'
                        
                        return jsonify({
                            'is_admin': is_admin,
                            'user': {
                                'id': user_id,
                                'email': user_email,
                                'name': user_email
                            }
                        }), 200
            except Exception as e:
                current_app.logger.error(f"Erro ao buscar usuário por ID: {e}")
        
        # Se não for token local, tentar como token do Supabase
        try:
            response = requests.get(
                f"{supabase_auth.supabase_url}/auth/v1/user",
                headers={
                    'apikey': supabase_auth.supabase_anon_key,
                    'Authorization': f'Bearer {token}',
                    'Content-Type': 'application/json'
                }
            )
            
            if response.ok:
                user_data = response.json()
                user_email = user_data.get('email', '')
                
                # Verificar se é admin (por email específico ou campo is_admin)
                is_admin = (
                    user_email == 'jonatasprojetos2013@gmail.com' or
                    user_data.get('user_metadata', {}).get('is_admin', False)
                )
                
                return jsonify({
                    'is_admin': is_admin,
                    'user': {
                        'id': user_data.get('id'),
                        'email': user_email,
                        'name': user_data.get('user_metadata', {}).get('name', user_email)
                    }
                }), 200
        except Exception as e:
            current_app.logger.error(f"Erro ao verificar token do Supabase: {e}")
        
        # Se chegou até aqui, token é inválido
        return jsonify({'is_admin': False, 'error': 'Token inválido'}), 401
        
    except Exception as e:
        current_app.logger.error(f"Erro inesperado ao verificar admin: {e}")
        return jsonify({'is_admin': False, 'error': 'Erro interno do servidor'}), 500

# Adicionar rota para obter usuário logado (exemplo de uso da classe SupabaseAuth)
@auth_supabase_bp.route('/user', methods=['GET'])
def get_logged_in_user():
    """Endpoint para obter informações do usuário logado via Supabase"""
    try:
        if not supabase_auth or not supabase_auth.is_available:
            return jsonify({'error': 'Serviço Supabase indisponível'}), 503

        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Token não fornecido'}), 401

        supabase_access_token = auth_header.split(' ')[1]

        response = requests.get(
            f"{supabase_auth.supabase_url}/auth/v1/user",
            headers={
                'apikey': supabase_auth.supabase_anon_key,
                'Authorization': f'Bearer {supabase_access_token}',
                'Content-Type': 'application/json'
            }
        )
        response.raise_for_status() # Levanta HTTPError para status de erro (4xx ou 5xx)

        user_data = response.json()

        return jsonify({
            'success': True,
            'user': user_data
        }), 200

    except requests.exceptions.HTTPError as http_err:
        current_app.logger.error(f"HTTP error occurred getting logged in user: {http_err} - {http_err.response.text}")
        if http_err.response.status_code == 401: # Unauthorized
            return jsonify({'error': 'Token inválido ou expirado'}), 401
        return jsonify({'error': 'Erro ao obter usuário logado do Supabase'}), 500
    except Exception as e:
        current_app.logger.error(f"Erro inesperado ao obter usuário logado: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

        
# Função para salvar sinais no Supabase
def save_signal_to_supabase(signal_data: dict) -> bool:
    """Função global para salvar sinais no Supabase"""
    if supabase_auth and supabase_auth.is_available:
        return supabase_auth.save_signal_to_supabase(signal_data)
    return False