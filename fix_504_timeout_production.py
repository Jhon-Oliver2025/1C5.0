#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Diagnóstico e Correção para Gateway Timeout 504
Data: 29/08/2025
Objetivo: Identificar e corrigir problemas de timeout em produção
"""

import requests
import time
import json
import subprocess
import sys
from datetime import datetime
from typing import Dict, List, Tuple

class ProductionTimeoutFixer:
    """Classe para diagnosticar e corrigir problemas de timeout em produção"""
    
    def __init__(self):
        self.domain = "https://1crypten.space"
        self.api_endpoints = [
            "/api/status",
            "/api/auth/check-admin",
            "/api/btc-signals/confirmed",
            "/api/market-status",
            "/health"
        ]
        self.frontend_routes = [
            "/",
            "/login",
            "/dashboard",
            "/app",
            "/btc-analysis"
        ]
        self.static_files = [
            "/logo3.png",
            "/terra2.png",
            "/sw.js",
            "/manifest.json"
        ]
        self.timeout_threshold = 30  # segundos
        self.results = []
    
    def log_message(self, message: str, level: str = "INFO"):
        """Log formatado com timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
    
    def test_endpoint(self, url: str, timeout: int = 30) -> Dict:
        """Testa um endpoint específico"""
        start_time = time.time()
        result = {
            "url": url,
            "status": "unknown",
            "status_code": None,
            "response_time": None,
            "error": None,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            response = requests.get(url, timeout=timeout, verify=True)
            end_time = time.time()
            response_time = end_time - start_time
            
            result.update({
                "status": "success" if response.status_code == 200 else "error",
                "status_code": response.status_code,
                "response_time": round(response_time, 2)
            })
            
            if response.status_code == 504:
                result["error"] = "Gateway Timeout"
            elif response.status_code != 200:
                result["error"] = f"HTTP {response.status_code}"
                
        except requests.exceptions.Timeout:
            result.update({
                "status": "timeout",
                "error": "Request timeout",
                "response_time": timeout
            })
        except requests.exceptions.ConnectionError:
            result.update({
                "status": "connection_error",
                "error": "Connection failed"
            })
        except Exception as e:
            result.update({
                "status": "error",
                "error": str(e)
            })
        
        return result
    
    def diagnose_all_endpoints(self) -> List[Dict]:
        """Diagnostica todos os endpoints"""
        self.log_message("🔍 Iniciando diagnóstico completo...")
        all_results = []
        
        # Testar APIs
        self.log_message("📡 Testando APIs...")
        for endpoint in self.api_endpoints:
            url = f"{self.domain}{endpoint}"
            result = self.test_endpoint(url)
            all_results.append(result)
            
            status_emoji = "✅" if result["status"] == "success" else "❌"
            time_info = f" ({result['response_time']}s)" if result['response_time'] else ""
            self.log_message(f"{status_emoji} {endpoint}: {result['status_code']}{time_info}")
        
        # Testar rotas do frontend
        self.log_message("🌐 Testando rotas do frontend...")
        for route in self.frontend_routes:
            url = f"{self.domain}{route}"
            result = self.test_endpoint(url)
            all_results.append(result)
            
            status_emoji = "✅" if result["status"] == "success" else "❌"
            time_info = f" ({result['response_time']}s)" if result['response_time'] else ""
            self.log_message(f"{status_emoji} {route}: {result['status_code']}{time_info}")
        
        # Testar arquivos estáticos
        self.log_message("📁 Testando arquivos estáticos...")
        for file_path in self.static_files:
            url = f"{self.domain}{file_path}"
            result = self.test_endpoint(url)
            all_results.append(result)
            
            status_emoji = "✅" if result["status"] == "success" else "❌"
            time_info = f" ({result['response_time']}s)" if result['response_time'] else ""
            self.log_message(f"{status_emoji} {file_path}: {result['status_code']}{time_info}")
        
        return all_results
    
    def analyze_results(self, results: List[Dict]) -> Dict:
        """Analisa os resultados dos testes"""
        analysis = {
            "total_tests": len(results),
            "successful": 0,
            "timeouts": 0,
            "errors": 0,
            "slow_responses": 0,
            "avg_response_time": 0,
            "max_response_time": 0,
            "problematic_endpoints": []
        }
        
        response_times = []
        
        for result in results:
            if result["status"] == "success":
                analysis["successful"] += 1
                if result["response_time"]:
                    response_times.append(result["response_time"])
                    if result["response_time"] > self.timeout_threshold:
                        analysis["slow_responses"] += 1
            elif result["status"] == "timeout":
                analysis["timeouts"] += 1
                analysis["problematic_endpoints"].append(result)
            else:
                analysis["errors"] += 1
                if result["status_code"] == 504:
                    analysis["problematic_endpoints"].append(result)
        
        if response_times:
            analysis["avg_response_time"] = round(sum(response_times) / len(response_times), 2)
            analysis["max_response_time"] = round(max(response_times), 2)
        
        return analysis
    
    def generate_nginx_fix(self) -> str:
        """Gera configuração otimizada do nginx"""
        nginx_config = '''
# Configuração Nginx Otimizada para Corrigir 504 Gateway Timeout
# Data: 29/08/2025

http {
    # Timeouts globais otimizados
    client_body_timeout 120s;
    client_header_timeout 120s;
    send_timeout 120s;
    keepalive_timeout 75s;
    
    # Buffer sizes otimizados
    client_body_buffer_size 256k;
    client_header_buffer_size 4m;
    large_client_header_buffers 8 256k;
    client_max_body_size 100m;
    
    # Proxy timeouts aumentados
    proxy_connect_timeout 180s;
    proxy_send_timeout 180s;
    proxy_read_timeout 180s;
    proxy_buffering on;
    proxy_buffer_size 256k;
    proxy_buffers 8 256k;
    proxy_busy_buffers_size 512k;
    
    # Upstream com failover robusto
    upstream backend {
        server backend:5000 max_fails=5 fail_timeout=60s weight=1;
        # Adicionar mais servidores se disponível
        # server backend2:5000 max_fails=5 fail_timeout=60s weight=1 backup;
        
        keepalive 64;
        keepalive_requests 1000;
        keepalive_timeout 120s;
    }
    
    server {
        listen 443 ssl http2;
        server_name 1crypten.space www.1crypten.space;
        
        # API routes com timeouts estendidos
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Timeouts específicos para APIs
            proxy_connect_timeout 180s;
            proxy_send_timeout 180s;
            proxy_read_timeout 300s;  # 5 minutos para operações longas
            
            # Keep-alive otimizado
            proxy_http_version 1.1;
            proxy_set_header Connection "";
            
            # Retry automático
            proxy_next_upstream error timeout invalid_header http_500 http_502 http_503 http_504;
            proxy_next_upstream_tries 3;
            proxy_next_upstream_timeout 60s;
        }
        
        # Health check com timeout menor
        location /health {
            proxy_pass http://backend/api/health;
            proxy_connect_timeout 30s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;
            access_log off;
        }
        
        # Frontend com cache otimizado
        location / {
            root /var/www/html;
            try_files $uri $uri/ /index.html;
            
            # Cache para arquivos estáticos
            location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
                expires 1y;
                add_header Cache-Control "public, immutable";
                add_header X-Cache-Status "HIT";
            }
            
            # Manifest.json específico
            location = /manifest.json {
                try_files $uri =404;
                add_header Cache-Control "no-cache";
            }
        }
    }
}
'''
        return nginx_config
    
    def generate_docker_fix(self) -> str:
        """Gera configuração otimizada do docker-compose"""
        docker_config = '''
# Docker Compose Otimizado para Corrigir 504 Gateway Timeout
# Data: 29/08/2025

version: '3.8'

services:
  backend:
    build: ./back
    container_name: crypto-backend
    environment:
      # Configurações de performance
      - GUNICORN_WORKERS=6          # Aumentado
      - GUNICORN_THREADS=4          # Aumentado
      - GUNICORN_TIMEOUT=300        # 5 minutos
      - GUNICORN_KEEPALIVE=10       # Aumentado
      - GUNICORN_MAX_REQUESTS=1000  # Restart workers
      - GUNICORN_MAX_REQUESTS_JITTER=100
      
      # Configurações de aplicação
      - FLASK_ENV=production
      - PYTHONUNBUFFERED=1
      - PYTHONDONTWRITEBYTECODE=1
      
      # Timeouts de banco
      - DB_CONNECT_TIMEOUT=60
      - DB_READ_TIMEOUT=120
      - DB_WRITE_TIMEOUT=120
      
    deploy:
      resources:
        limits:
          memory: 4G              # Dobrado
          cpus: '4.0'             # Dobrado
        reservations:
          memory: 1G              # Aumentado
          cpus: '1.0'             # Aumentado
    
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/api/health"]
      interval: 60s             # Reduzido overhead
      timeout: 30s              # Aumentado
      retries: 5
      start_period: 120s        # Mais tempo para inicialização
    
    restart: unless-stopped
    
  nginx:
    image: nginx:alpine
    container_name: crypto-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.prod.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
      - ./front/dist:/var/www/html
    depends_on:
      backend:
        condition: service_healthy
    restart: unless-stopped
    
    # Configurações de sistema
    ulimits:
      nofile:
        soft: 65536
        hard: 65536
    
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '1.0'
'''
        return docker_config
    
    def create_monitoring_script(self) -> str:
        """Cria script de monitoramento contínuo"""
        monitoring_script = '''
#!/bin/bash
# Script de Monitoramento Contínuo para 504 Gateway Timeout
# Data: 29/08/2025

DOMAIN="https://1crypten.space"
LOG_FILE="/var/log/504_monitoring.log"
ALERT_THRESHOLD=3  # Número de falhas consecutivas para alertar

# Função de log
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a $LOG_FILE
}

# Função de teste de endpoint
test_endpoint() {
    local url=$1
    local timeout=${2:-30}
    
    response=$(curl -s -o /dev/null -w "%{http_code}:%{time_total}" \
                   --max-time $timeout \
                   --connect-timeout 10 \
                   "$url" 2>/dev/null)
    
    if [ $? -eq 0 ]; then
        http_code=$(echo $response | cut -d: -f1)
        time_total=$(echo $response | cut -d: -f2)
        echo "$http_code:$time_total"
    else
        echo "000:timeout"
    fi
}

# Função principal de monitoramento
monitor_system() {
    log_message "🔍 Iniciando monitoramento do sistema..."
    
    # Endpoints críticos
    endpoints=(
        "/api/status"
        "/api/health"
        "/login"
        "/dashboard"
    )
    
    failed_count=0
    
    for endpoint in "${endpoints[@]}"; do
        url="$DOMAIN$endpoint"
        result=$(test_endpoint "$url" 60)
        
        http_code=$(echo $result | cut -d: -f1)
        time_total=$(echo $result | cut -d: -f2)
        
        if [ "$http_code" = "200" ]; then
            log_message "✅ $endpoint: OK (${time_total}s)"
        elif [ "$http_code" = "504" ]; then
            log_message "❌ $endpoint: Gateway Timeout (504)"
            failed_count=$((failed_count + 1))
        elif [ "$http_code" = "000" ]; then
            log_message "⏰ $endpoint: Request Timeout"
            failed_count=$((failed_count + 1))
        else
            log_message "⚠️ $endpoint: HTTP $http_code (${time_total}s)"
        fi
        
        sleep 2
    done
    
    # Verificar se precisa de ação
    if [ $failed_count -ge $ALERT_THRESHOLD ]; then
        log_message "🚨 ALERTA: $failed_count endpoints falharam!"
        
        # Tentar restart do nginx
        log_message "🔄 Tentando restart do nginx..."
        docker exec crypto-nginx nginx -s reload
        
        # Verificar logs do backend
        log_message "📋 Verificando logs do backend..."
        docker logs --tail 50 crypto-backend | tail -10 >> $LOG_FILE
        
        # Verificar recursos do sistema
        log_message "💾 Verificando recursos do sistema..."
        echo "Memory usage:" >> $LOG_FILE
        free -h >> $LOG_FILE
        echo "CPU usage:" >> $LOG_FILE
        top -bn1 | head -5 >> $LOG_FILE
    fi
    
    log_message "✅ Monitoramento concluído. Falhas: $failed_count"
}

# Executar monitoramento
monitor_system
'''
        return monitoring_script
    
    def save_report(self, results: List[Dict], analysis: Dict):
        """Salva relatório detalhado"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "domain": self.domain,
            "analysis": analysis,
            "detailed_results": results,
            "recommendations": self.get_recommendations(analysis)
        }
        
        filename = f"504_timeout_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.log_message(f"📄 Relatório salvo: {filename}")
        return filename
    
    def get_recommendations(self, analysis: Dict) -> List[str]:
        """Gera recomendações baseadas na análise"""
        recommendations = []
        
        if analysis["timeouts"] > 0:
            recommendations.append("🔧 Aumentar timeouts do nginx (proxy_read_timeout para 300s)")
            recommendations.append("🔧 Configurar retry automático no nginx")
        
        if analysis["errors"] > 0:
            recommendations.append("🔍 Verificar logs do backend para identificar erros")
            recommendations.append("🔄 Considerar restart do serviço backend")
        
        if analysis["slow_responses"] > 0:
            recommendations.append("⚡ Otimizar performance do backend")
            recommendations.append("📈 Aumentar recursos do container (CPU/RAM)")
        
        if analysis["avg_response_time"] > 10:
            recommendations.append("🚀 Implementar cache para reduzir tempo de resposta")
            recommendations.append("🔧 Otimizar queries do banco de dados")
        
        if len(analysis["problematic_endpoints"]) > 0:
            recommendations.append("🎯 Focar na correção dos endpoints problemáticos")
            recommendations.append("📊 Implementar monitoramento específico")
        
        return recommendations
    
    def run_diagnosis(self):
        """Executa diagnóstico completo"""
        self.log_message("🚀 Iniciando diagnóstico de Gateway Timeout 504...")
        self.log_message(f"🌐 Domínio: {self.domain}")
        
        # Executar testes
        results = self.diagnose_all_endpoints()
        
        # Analisar resultados
        analysis = self.analyze_results(results)
        
        # Exibir resumo
        self.log_message("\n📊 RESUMO DO DIAGNÓSTICO:")
        self.log_message(f"Total de testes: {analysis['total_tests']}")
        self.log_message(f"✅ Sucessos: {analysis['successful']}")
        self.log_message(f"⏰ Timeouts: {analysis['timeouts']}")
        self.log_message(f"❌ Erros: {analysis['errors']}")
        self.log_message(f"🐌 Respostas lentas: {analysis['slow_responses']}")
        self.log_message(f"⏱️ Tempo médio: {analysis['avg_response_time']}s")
        self.log_message(f"⏱️ Tempo máximo: {analysis['max_response_time']}s")
        
        # Endpoints problemáticos
        if analysis["problematic_endpoints"]:
            self.log_message("\n🚨 ENDPOINTS PROBLEMÁTICOS:")
            for endpoint in analysis["problematic_endpoints"]:
                self.log_message(f"❌ {endpoint['url']}: {endpoint['error']}")
        
        # Recomendações
        recommendations = self.get_recommendations(analysis)
        if recommendations:
            self.log_message("\n💡 RECOMENDAÇÕES:")
            for rec in recommendations:
                self.log_message(rec)
        
        # Salvar relatório
        report_file = self.save_report(results, analysis)
        
        # Gerar arquivos de correção
        self.log_message("\n🔧 Gerando arquivos de correção...")
        
        # Nginx config
        with open("nginx_504_fix.conf", "w") as f:
            f.write(self.generate_nginx_fix())
        self.log_message("📄 Configuração nginx salva: nginx_504_fix.conf")
        
        # Docker config
        with open("docker-compose_504_fix.yml", "w") as f:
            f.write(self.generate_docker_fix())
        self.log_message("📄 Configuração docker salva: docker-compose_504_fix.yml")
        
        # Monitoring script
        with open("monitor_504.sh", "w") as f:
            f.write(self.create_monitoring_script())
        self.log_message("📄 Script de monitoramento salvo: monitor_504.sh")
        
        self.log_message("\n✅ Diagnóstico concluído!")
        
        return analysis

def main():
    """Função principal"""
    print("🔍 Diagnóstico de Gateway Timeout 504 - 1Crypten.space")
    print("=" * 60)
    
    fixer = ProductionTimeoutFixer()
    analysis = fixer.run_diagnosis()
    
    # Status final
    if analysis["timeouts"] == 0 and analysis["errors"] == 0:
        print("\n🎉 Sistema funcionando normalmente!")
        return 0
    else:
        print("\n⚠️ Problemas detectados. Verifique as recomendações.")
        return 1

if __name__ == "__main__":
    sys.exit(main())