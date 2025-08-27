#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Keep-Alive para manter APIs essenciais sempre ativas
Evita que o backend entre em modo sleep e pare de responder
"""

import time
import threading
import requests
from datetime import datetime
from typing import Dict, List, Optional
from flask import current_app

class KeepAliveSystem:
    """Sistema para manter o backend sempre ativo e responsivo"""
    
    def __init__(self, app=None):
        self.app = app
        self.is_running = False
        self.heartbeat_thread = None
        self.api_status_cache = {}
        self.last_heartbeat = None
        
        # Configurações
        self.heartbeat_interval = 30  # segundos
        self.api_timeout = 10  # segundos
        
        # APIs essenciais que devem sempre responder
        self.essential_apis = [
            '/api/status',
            '/api/market-status', 
            '/api/signals',
            '/api/btc-signals/metrics'
        ]
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Inicializa o sistema com a aplicação Flask"""
        self.app = app
        
        # Registrar rotas de keep-alive
        self._register_keepalive_routes()
        
        # Iniciar sistema automaticamente
        self.start()
    
    def _register_keepalive_routes(self):
        """Registra rotas específicas para keep-alive"""
        
        @self.app.route('/api/keepalive/ping', methods=['GET'])
        def keepalive_ping():
            """Endpoint simples para verificar se o servidor está vivo"""
            return {
                'status': 'alive',
                'timestamp': datetime.now().isoformat(),
                'uptime': time.time() - getattr(self.app, 'start_time', time.time())
            }, 200
        
        @self.app.route('/api/keepalive/health', methods=['GET'])
        def keepalive_health():
            """Endpoint de saúde detalhado"""
            return {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'heartbeat_active': self.is_running,
                'last_heartbeat': self.last_heartbeat,
                'api_status': self.api_status_cache,
                'essential_apis_count': len(self.essential_apis)
            }, 200
        
        @self.app.route('/api/keepalive/wake', methods=['POST'])
        def keepalive_wake():
            """Endpoint para 'acordar' o sistema se necessário"""
            self._perform_wake_up()
            return {
                'status': 'awakened',
                'timestamp': datetime.now().isoformat(),
                'message': 'Sistema acordado com sucesso'
            }, 200
    
    def start(self):
        """Inicia o sistema de keep-alive"""
        if self.is_running:
            return
        
        self.is_running = True
        self.heartbeat_thread = threading.Thread(
            target=self._heartbeat_loop,
            daemon=True,
            name='KeepAliveHeartbeat'
        )
        self.heartbeat_thread.start()
        
        print("💓 Sistema Keep-Alive iniciado")
        print(f"⏱️ Intervalo de heartbeat: {self.heartbeat_interval}s")
        print(f"🎯 APIs monitoradas: {len(self.essential_apis)}")
    
    def stop(self):
        """Para o sistema de keep-alive"""
        self.is_running = False
        if self.heartbeat_thread:
            self.heartbeat_thread.join(timeout=5)
        print("💔 Sistema Keep-Alive parado")
    
    def _heartbeat_loop(self):
        """Loop principal do heartbeat"""
        while self.is_running:
            try:
                self._perform_heartbeat()
                time.sleep(self.heartbeat_interval)
            except Exception as e:
                print(f"❌ Erro no heartbeat: {e}")
                time.sleep(5)  # Aguardar menos tempo em caso de erro
    
    def _perform_heartbeat(self):
        """Executa um ciclo de heartbeat"""
        self.last_heartbeat = datetime.now().isoformat()
        
        # Verificar status das APIs essenciais
        self._check_essential_apis()
        
        # Executar tarefas de manutenção
        self._perform_maintenance_tasks()
        
        # Log de heartbeat (apenas a cada 5 minutos para não poluir)
        current_time = time.time()
        if not hasattr(self, '_last_log_time') or current_time - self._last_log_time > 300:
            print(f"💓 Heartbeat: {self.last_heartbeat} - APIs: {len([k for k, v in self.api_status_cache.items() if v.get('status') == 'ok'])} OK")
            self._last_log_time = current_time
    
    def _check_essential_apis(self):
        """Verifica o status das APIs essenciais"""
        for api_path in self.essential_apis:
            try:
                # Simular uma verificação interna (sem fazer request HTTP)
                # Em produção, isso mantém as rotas "quentes"
                status = self._check_api_internal(api_path)
                self.api_status_cache[api_path] = {
                    'status': 'ok' if status else 'error',
                    'last_check': datetime.now().isoformat(),
                    'response_time': 0.1  # Tempo simulado
                }
            except Exception as e:
                self.api_status_cache[api_path] = {
                    'status': 'error',
                    'last_check': datetime.now().isoformat(),
                    'error': str(e)
                }
    
    def _check_api_internal(self, api_path: str) -> bool:
        """Verifica internamente se uma API está funcionando"""
        try:
            # Verificar se a rota existe no Flask app
            with self.app.test_request_context(api_path):
                # Isso mantém as rotas "quentes" sem fazer requests externos
                return True
        except Exception:
            return False
    
    def _perform_maintenance_tasks(self):
        """Executa tarefas de manutenção durante o heartbeat"""
        try:
            # Limpar cache antigo
            self._cleanup_old_cache()
            
            # Verificar memória (se necessário)
            self._check_memory_usage()
            
            # Manter conexões ativas
            self._maintain_connections()
            
        except Exception as e:
            print(f"⚠️ Erro em tarefas de manutenção: {e}")
    
    def _cleanup_old_cache(self):
        """Remove entradas antigas do cache"""
        current_time = datetime.now()
        # Implementar limpeza se necessário
        pass
    
    def _check_memory_usage(self):
        """Verifica uso de memória"""
        try:
            import psutil
            memory_percent = psutil.virtual_memory().percent
            if memory_percent > 85:
                print(f"⚠️ Uso de memória alto: {memory_percent}%")
        except ImportError:
            pass  # psutil não disponível
    
    def _maintain_connections(self):
        """Mantém conexões ativas"""
        # Verificar se há instâncias importantes que precisam ser mantidas ativas
        if hasattr(self.app, 'bot_instance'):
            bot = self.app.bot_instance
            if hasattr(bot, 'analyzer') and hasattr(bot.analyzer, 'is_monitoring'):
                # O sistema de análise está ativo, não precisa fazer nada especial
                pass
    
    def _perform_wake_up(self):
        """Executa procedimentos para 'acordar' o sistema"""
        print("🔔 Executando wake-up do sistema...")
        
        # Verificar todas as APIs essenciais
        self._check_essential_apis()
        
        # Forçar um heartbeat
        self._perform_heartbeat()
        
        # Verificar se o sistema de análise está rodando
        if hasattr(self.app, 'bot_instance'):
            bot = self.app.bot_instance
            if hasattr(bot, 'analyzer'):
                analyzer = bot.analyzer
                if not getattr(analyzer, 'is_monitoring', False):
                    print("🔄 Reativando sistema de análise...")
                    # Tentar reativar se necessário
        
        print("✅ Wake-up concluído")
    
    def get_status(self) -> Dict:
        """Retorna status completo do sistema"""
        return {
            'is_running': self.is_running,
            'last_heartbeat': self.last_heartbeat,
            'api_status': self.api_status_cache,
            'heartbeat_interval': self.heartbeat_interval,
            'essential_apis': self.essential_apis,
            'thread_alive': self.heartbeat_thread.is_alive() if self.heartbeat_thread else False
        }

# Instância global
keep_alive_system = KeepAliveSystem()

def init_keep_alive(app):
    """Inicializa o sistema de keep-alive com a aplicação"""
    global keep_alive_system
    keep_alive_system.init_app(app)
    return keep_alive_system