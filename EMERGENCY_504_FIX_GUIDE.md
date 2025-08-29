# 🚨 GUIA DE CORREÇÃO EMERGENCIAL - Gateway Timeout 504

## ⚠️ **SITUAÇÃO CRÍTICA IDENTIFICADA**

### 📊 **Diagnóstico Realizado em 29/08/2025 02:47-02:54:**
- ✅ **Total de testes**: 14 endpoints
- ❌ **Sucessos**: 0 (0%)
- ⏰ **Timeouts**: 14 (100%)
- 🚨 **Status**: SISTEMA COMPLETAMENTE INDISPONÍVEL

### 🎯 **Endpoints Afetados (TODOS):**
```
❌ /api/status - Request timeout (30s)
❌ /api/auth/check-admin - Request timeout (30s)
❌ /api/btc-signals/confirmed - Request timeout (30s)
❌ /api/market-status - Request timeout (30s)
❌ /health - Request timeout (30s)
❌ / - Request timeout (30s)
❌ /login - Request timeout (30s)
❌ /dashboard - Request timeout (30s)
❌ /app - Request timeout (30s)
❌ /btc-analysis - Request timeout (30s)
❌ /logo3.png - Request timeout (30s)
❌ /terra2.png - Request timeout (30s)
❌ /sw.js - Request timeout (30s)
❌ /manifest.json - Request timeout (30s)
```

---

## 🔥 **AÇÕES EMERGENCIAIS IMEDIATAS**

### 🚀 **1. VERIFICAR STATUS DOS CONTAINERS**

```bash
# Verificar se os containers estão rodando
docker ps -a

# Verificar logs dos containers
docker logs crypto-backend --tail 50
docker logs crypto-nginx --tail 50
docker logs crypto-frontend --tail 50

# Verificar recursos do sistema
free -h
df -h
top
```

### 🔄 **2. RESTART EMERGENCIAL DOS SERVIÇOS**

```bash
# Parar todos os serviços
docker-compose -f docker-compose.prod.yml down

# Limpar containers órfãos
docker system prune -f

# Reiniciar todos os serviços
docker-compose -f docker-compose.prod.yml up -d

# Verificar status após restart
docker-compose -f docker-compose.prod.yml ps
```

### 🔍 **3. DIAGNÓSTICO DETALHADO**

```bash
# Verificar conectividade de rede
ping 1crypten.space
nslookup 1crypten.space

# Verificar portas abertas
netstat -tlnp | grep :80
netstat -tlnp | grep :443
netstat -tlnp | grep :5000

# Verificar certificado SSL
openssl s_client -connect 1crypten.space:443 -servername 1crypten.space
```

---

## 🛠️ **CORREÇÕES ESPECÍFICAS PARA 504 TIMEOUT**

### ✅ **1. CONFIGURAÇÃO NGINX OTIMIZADA**

**Arquivo: `/etc/nginx/nginx.conf` ou `nginx/nginx.prod.conf`**

```nginx
http {
    # Timeouts MUITO mais altos para resolver 504
    client_body_timeout 300s;
    client_header_timeout 300s;
    send_timeout 300s;
    keepalive_timeout 120s;
    
    # Buffers maiores
    client_body_buffer_size 512k;
    client_header_buffer_size 8m;
    large_client_header_buffers 8 512k;
    client_max_body_size 200m;
    
    # Upstream com configuração robusta
    upstream backend {
        server backend:5000 max_fails=10 fail_timeout=120s;
        keepalive 128;
        keepalive_requests 10000;
        keepalive_timeout 300s;
    }
    
    server {
        listen 443 ssl http2;
        server_name 1crypten.space www.1crypten.space;
        
        # API com timeouts MUITO altos
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # TIMEOUTS EMERGENCIAIS - 10 MINUTOS
            proxy_connect_timeout 600s;
            proxy_send_timeout 600s;
            proxy_read_timeout 600s;
            
            # Buffers grandes
            proxy_buffering on;
            proxy_buffer_size 512k;
            proxy_buffers 16 512k;
            proxy_busy_buffers_size 1m;
            
            # Keep-alive agressivo
            proxy_http_version 1.1;
            proxy_set_header Connection "";
            
            # Retry automático agressivo
            proxy_next_upstream error timeout invalid_header http_500 http_502 http_503 http_504;
            proxy_next_upstream_tries 10;
            proxy_next_upstream_timeout 300s;
        }
        
        # Health check com timeout alto
        location /health {
            proxy_pass http://backend/api/health;
            proxy_connect_timeout 120s;
            proxy_send_timeout 120s;
            proxy_read_timeout 120s;
        }
        
        # Frontend
        location / {
            root /var/www/html;
            try_files $uri $uri/ /index.html;
            
            # Timeout para arquivos estáticos
            location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
                expires 1y;
                add_header Cache-Control "public, immutable";
                try_files $uri =404;
            }
        }
    }
}
```

### ✅ **2. CONFIGURAÇÃO DOCKER OTIMIZADA**

**Arquivo: `docker-compose.prod.yml`**

```yaml
version: '3.8'

services:
  backend:
    build: ./back
    container_name: crypto-backend
    environment:
      # CONFIGURAÇÕES EMERGENCIAIS DE PERFORMANCE
      - GUNICORN_WORKERS=8
      - GUNICORN_THREADS=8
      - GUNICORN_TIMEOUT=600        # 10 MINUTOS
      - GUNICORN_KEEPALIVE=30
      - GUNICORN_MAX_REQUESTS=10000
      - GUNICORN_MAX_REQUESTS_JITTER=1000
      
      # Configurações de aplicação
      - FLASK_ENV=production
      - PYTHONUNBUFFERED=1
      - PYTHONDONTWRITEBYTECODE=1
      
      # Timeouts de banco ALTOS
      - DB_CONNECT_TIMEOUT=120
      - DB_READ_TIMEOUT=300
      - DB_WRITE_TIMEOUT=300
      
    deploy:
      resources:
        limits:
          memory: 8G              # MÁXIMO POSSÍVEL
          cpus: '8.0'             # MÁXIMO POSSÍVEL
        reservations:
          memory: 2G
          cpus: '2.0'
    
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/api/health"]
      interval: 120s            # Menos overhead
      timeout: 60s              # Timeout alto
      retries: 10               # Mais tentativas
      start_period: 300s        # 5 minutos para inicializar
    
    restart: unless-stopped
    
    # Configurações de sistema
    ulimits:
      nofile:
        soft: 65536
        hard: 65536
      nproc:
        soft: 65536
        hard: 65536
```

### ✅ **3. SCRIPT DE MONITORAMENTO EMERGENCIAL**

**Arquivo: `emergency_monitor.sh`**

```bash
#!/bin/bash
# Monitoramento Emergencial para 504 Gateway Timeout

DOMAIN="https://1crypten.space"
LOG_FILE="/var/log/emergency_504.log"

log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a $LOG_FILE
}

# Função de teste rápido
quick_test() {
    local url="$DOMAIN/api/status"
    local response=$(curl -s -o /dev/null -w "%{http_code}" --max-time 60 "$url" 2>/dev/null)
    echo $response
}

# Função de restart emergencial
emergency_restart() {
    log_message "🚨 EXECUTANDO RESTART EMERGENCIAL"
    
    # Parar serviços
    docker-compose -f docker-compose.prod.yml down
    sleep 10
    
    # Limpar sistema
    docker system prune -f
    
    # Reiniciar
    docker-compose -f docker-compose.prod.yml up -d
    
    # Aguardar inicialização
    sleep 60
    
    log_message "✅ Restart emergencial concluído"
}

# Loop de monitoramento
while true; do
    status=$(quick_test)
    
    if [ "$status" = "200" ]; then
        log_message "✅ Sistema OK (HTTP 200)"
        sleep 60
    else
        log_message "❌ Sistema com problema (HTTP $status)"
        
        # Verificar se containers estão rodando
        if ! docker ps | grep -q crypto-backend; then
            log_message "🚨 Backend container não está rodando!"
            emergency_restart
        elif ! docker ps | grep -q crypto-nginx; then
            log_message "🚨 Nginx container não está rodando!"
            emergency_restart
        else
            log_message "⚠️ Containers rodando, mas sistema não responde"
            
            # Verificar logs
            docker logs crypto-backend --tail 10 >> $LOG_FILE
            docker logs crypto-nginx --tail 10 >> $LOG_FILE
            
            # Restart após 3 falhas consecutivas
            ((failures++))
            if [ $failures -ge 3 ]; then
                emergency_restart
                failures=0
            fi
        fi
        
        sleep 30
    fi
done
```

---

## 🔍 **DIAGNÓSTICO AVANÇADO**

### 📊 **1. VERIFICAR RECURSOS DO SERVIDOR**

```bash
# Memória
free -h
cat /proc/meminfo | grep -E "MemTotal|MemFree|MemAvailable"

# CPU
top -bn1 | head -20
cat /proc/loadavg

# Disco
df -h
du -sh /var/lib/docker

# Rede
ss -tlnp | grep -E ":80|:443|:5000"
iptables -L -n
```

### 📋 **2. VERIFICAR LOGS DETALHADOS**

```bash
# Logs do sistema
journalctl -u docker --since "1 hour ago" --no-pager
systemctl status docker

# Logs dos containers
docker logs crypto-backend --since 1h
docker logs crypto-nginx --since 1h
docker logs crypto-frontend --since 1h

# Logs do nginx dentro do container
docker exec crypto-nginx cat /var/log/nginx/error.log | tail -50
docker exec crypto-nginx cat /var/log/nginx/access.log | tail -50
```

### 🔧 **3. TESTES DE CONECTIVIDADE**

```bash
# Teste interno dos containers
docker exec crypto-nginx curl -f http://backend:5000/api/health
docker exec crypto-backend curl -f http://localhost:5000/api/health

# Teste de DNS
nslookup 1crypten.space
dig 1crypten.space

# Teste de SSL
openssl s_client -connect 1crypten.space:443 -servername 1crypten.space < /dev/null
```

---

## 🚀 **PLANO DE RECUPERAÇÃO STEP-BY-STEP**

### ✅ **FASE 1: DIAGNÓSTICO IMEDIATO (5 minutos)**

1. **Verificar containers:**
   ```bash
   docker ps -a
   docker-compose -f docker-compose.prod.yml ps
   ```

2. **Verificar recursos:**
   ```bash
   free -h && df -h && top -bn1 | head -10
   ```

3. **Verificar conectividade:**
   ```bash
   curl -I https://1crypten.space --max-time 10
   ```

### ✅ **FASE 2: RESTART CONTROLADO (10 minutos)**

1. **Backup dos logs:**
   ```bash
   mkdir -p /tmp/emergency_backup_$(date +%Y%m%d_%H%M%S)
   docker logs crypto-backend > /tmp/emergency_backup_*/backend.log
   docker logs crypto-nginx > /tmp/emergency_backup_*/nginx.log
   ```

2. **Restart gradual:**
   ```bash
   # Parar nginx primeiro
   docker stop crypto-nginx
   sleep 5
   
   # Parar backend
   docker stop crypto-backend
   sleep 10
   
   # Reiniciar backend
   docker start crypto-backend
   sleep 30
   
   # Reiniciar nginx
   docker start crypto-nginx
   sleep 10
   ```

3. **Verificar funcionamento:**
   ```bash
   curl -f https://1crypten.space/api/health --max-time 60
   ```

### ✅ **FASE 3: APLICAR CORREÇÕES (15 minutos)**

1. **Aplicar configuração nginx otimizada**
2. **Aplicar configuração docker otimizada**
3. **Reiniciar com novas configurações**
4. **Implementar monitoramento emergencial**

### ✅ **FASE 4: MONITORAMENTO (Contínuo)**

1. **Executar script de monitoramento**
2. **Verificar logs em tempo real**
3. **Monitorar métricas de performance**

---

## 📞 **CONTATOS DE EMERGÊNCIA**

### 🚨 **Se o problema persistir:**

1. **Verificar provedor de hospedagem**
2. **Verificar DNS e CDN**
3. **Verificar certificado SSL**
4. **Considerar migração temporária**

### 📊 **Métricas para monitorar:**

- **Response time** < 5s
- **Error rate** < 1%
- **Uptime** > 99.9%
- **Memory usage** < 80%
- **CPU usage** < 70%

---

## ✅ **CHECKLIST DE RECUPERAÇÃO**

- [ ] Containers rodando
- [ ] Logs sem erros críticos
- [ ] API /health respondendo
- [ ] Frontend carregando
- [ ] SSL funcionando
- [ ] DNS resolvendo
- [ ] Monitoramento ativo
- [ ] Backup dos logs
- [ ] Configurações otimizadas aplicadas
- [ ] Testes de carga realizados

---

**🚨 SITUAÇÃO CRÍTICA: TODOS OS ENDPOINTS COM TIMEOUT**
**⏰ AÇÃO IMEDIATA NECESSÁRIA**
**📞 ESCALAR PARA EQUIPE DE INFRAESTRUTURA SE NECESSÁRIO**

---

**Última atualização:** 29/08/2025 02:54  
**Status:** SISTEMA INDISPONÍVEL - CORREÇÃO EMERGENCIAL NECESSÁRIA