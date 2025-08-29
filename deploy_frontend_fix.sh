#!/bin/bash
# Script de Deploy Otimizado para Corrigir Frontend em Produção
# Data: 29/08/2025
# Objetivo: Resolver problemas de Gateway Timeout 504

set -e

echo "🚀 Iniciando deploy otimizado do frontend..."
echo "📅 Data: $(date)"
echo "🎯 Objetivo: Corrigir Gateway Timeout 504"

# Função de log
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Função de verificação de saúde
health_check() {
    local url=$1
    local max_attempts=10
    local attempt=1
    
    log_message "🔍 Verificando saúde do sistema: $url"
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s --max-time 30 "$url" > /dev/null; then
            log_message "✅ Sistema respondendo (tentativa $attempt)"
            return 0
        else
            log_message "❌ Sistema não responde (tentativa $attempt/$max_attempts)"
            sleep 10
            ((attempt++))
        fi
    done
    
    log_message "🚨 Sistema não respondeu após $max_attempts tentativas"
    return 1
}

# 1. Backup dos containers atuais
log_message "📦 Fazendo backup dos containers atuais..."
docker images | grep crypto > /tmp/backup_images_$(date +%Y%m%d_%H%M%S).txt
docker ps -a | grep crypto > /tmp/backup_containers_$(date +%Y%m%d_%H%M%S).txt

# 2. Parar containers gradualmente
log_message "⏹️ Parando containers gradualmente..."

# Parar nginx primeiro (para evitar requests para backend morto)
if docker ps | grep -q crypto-nginx; then
    log_message "🔄 Parando nginx..."
    docker stop crypto-nginx
    sleep 5
fi

# Parar frontend
if docker ps | grep -q crypto-frontend; then
    log_message "🔄 Parando frontend..."
    docker stop crypto-frontend
    sleep 5
fi

# 3. Limpar recursos
log_message "🧹 Limpando recursos..."
docker system prune -f
docker volume prune -f

# 4. Rebuild do frontend com otimizações
log_message "🔨 Rebuilding frontend com otimizações..."
cd front

# Limpar cache do npm
npm cache clean --force

# Reinstalar dependências
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps

# Build otimizado
log_message "⚡ Executando build otimizado..."
NODE_ENV=production npm run build

# Verificar se build foi bem-sucedido
if [ ! -f "dist/index.html" ]; then
    log_message "❌ Build falhou - index.html não encontrado"
    exit 1
fi

log_message "✅ Build concluído com sucesso"
cd ..

# 5. Rebuild dos containers
log_message "🐳 Rebuilding containers..."

# Frontend
log_message "🔨 Rebuilding frontend container..."
docker build -t crypto-frontend:latest ./front

# Nginx (se necessário)
log_message "🔨 Rebuilding nginx container..."
docker build -t crypto-nginx:latest -f nginx/Dockerfile .

# 6. Aplicar configurações otimizadas
log_message "⚙️ Aplicando configurações otimizadas..."

# Backup da configuração atual
cp docker-compose.prod.yml docker-compose.prod.yml.backup.$(date +%Y%m%d_%H%M%S)
cp nginx/nginx.prod.conf nginx/nginx.prod.conf.backup.$(date +%Y%m%d_%H%M%S)

# Aplicar configurações otimizadas (se existirem)
if [ -f "docker-compose_504_fix.yml" ]; then
    log_message "📋 Aplicando docker-compose otimizado..."
    cp docker-compose_504_fix.yml docker-compose.prod.yml
fi

if [ -f "nginx_504_fix.conf" ]; then
    log_message "📋 Aplicando nginx otimizado..."
    cp nginx_504_fix.conf nginx/nginx.prod.conf
fi

# 7. Iniciar serviços com configurações otimizadas
log_message "🚀 Iniciando serviços otimizados..."

# Iniciar backend primeiro
log_message "🔄 Iniciando backend..."
docker-compose -f docker-compose.prod.yml up -d backend
sleep 30

# Verificar se backend está respondendo
if ! health_check "http://localhost:5000/api/health"; then
    log_message "❌ Backend não está respondendo"
    # Tentar restart do backend
    log_message "🔄 Tentando restart do backend..."
    docker-compose -f docker-compose.prod.yml restart backend
    sleep 30
    
    if ! health_check "http://localhost:5000/api/health"; then
        log_message "🚨 Backend falhou após restart - abortando deploy"
        exit 1
    fi
fi

# Iniciar frontend
log_message "🔄 Iniciando frontend..."
docker-compose -f docker-compose.prod.yml up -d frontend
sleep 20

# Iniciar nginx
log_message "🔄 Iniciando nginx..."
docker-compose -f docker-compose.prod.yml up -d nginx
sleep 20

# 8. Verificações finais
log_message "🔍 Executando verificações finais..."

# Verificar se todos os containers estão rodando
log_message "📊 Status dos containers:"
docker-compose -f docker-compose.prod.yml ps

# Verificar logs para erros
log_message "📋 Verificando logs recentes..."
docker logs crypto-backend --tail 20
docker logs crypto-frontend --tail 20
docker logs crypto-nginx --tail 20

# Health check completo
log_message "🏥 Executando health check completo..."

endpoints=(
    "https://1crypten.space/"
    "https://1crypten.space/api/health"
    "https://1crypten.space/api/status"
    "https://1crypten.space/login"
    "https://1crypten.space/manifest.json"
)

failed_checks=0

for endpoint in "${endpoints[@]}"; do
    if health_check "$endpoint"; then
        log_message "✅ $endpoint: OK"
    else
        log_message "❌ $endpoint: FALHOU"
        ((failed_checks++))
    fi
done

# 9. Resultado final
if [ $failed_checks -eq 0 ]; then
    log_message "🎉 Deploy concluído com sucesso!"
    log_message "✅ Todos os endpoints estão respondendo"
    log_message "🌐 Sistema disponível em: https://1crypten.space"
    
    # Limpar backups antigos (manter apenas os 5 mais recentes)
    find /tmp -name "backup_*_*.txt" -mtime +5 -delete 2>/dev/null || true
    
    exit 0
else
    log_message "⚠️ Deploy concluído com $failed_checks falhas"
    log_message "🔍 Verifique os logs para mais detalhes"
    log_message "📞 Pode ser necessário intervenção manual"
    
    # Salvar logs de debug
    debug_file="/tmp/deploy_debug_$(date +%Y%m%d_%H%M%S).log"
    {
        echo "=== DEPLOY DEBUG LOG ==="
        echo "Data: $(date)"
        echo "Falhas: $failed_checks"
        echo ""
        echo "=== DOCKER PS ==="
        docker ps -a
        echo ""
        echo "=== BACKEND LOGS ==="
        docker logs crypto-backend --tail 50
        echo ""
        echo "=== FRONTEND LOGS ==="
        docker logs crypto-frontend --tail 50
        echo ""
        echo "=== NGINX LOGS ==="
        docker logs crypto-nginx --tail 50
    } > "$debug_file"
    
    log_message "📄 Logs de debug salvos em: $debug_file"
    
    exit 1
fi