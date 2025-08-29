#!/bin/bash
# Script para Recriar Sistema Docker Completo - 1Crypten
# Data: 29/08/2025
# Objetivo: Reconstruir todas as imagens após falha dos containers

set -e

echo "🚀 Iniciando reconstrução completa do sistema Docker..."
echo "📅 Data: $(date)"
echo "🎯 Objetivo: Recriar todas as imagens e containers"

# Função de log
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Função de verificação
check_command() {
    if command -v $1 >/dev/null 2>&1; then
        log_message "✅ $1 está disponível"
        return 0
    else
        log_message "❌ $1 não encontrado"
        return 1
    fi
}

# 1. Verificar dependências
log_message "🔍 Verificando dependências..."
check_command docker || { echo "❌ Docker não instalado"; exit 1; }
check_command docker-compose || { echo "❌ Docker Compose não instalado"; exit 1; }

# 2. Parar e remover todos os containers relacionados
log_message "🛑 Parando e removendo containers existentes..."

# Parar containers se estiverem rodando
docker ps -a --format "table {{.Names}}" | grep -E "(frontend|backend|redis|nginx|postgres)" | while read container; do
    if [ "$container" != "NAMES" ]; then
        log_message "🔄 Parando container: $container"
        docker stop "$container" 2>/dev/null || true
        docker rm "$container" 2>/dev/null || true
    fi
done

# Remover containers órfãos
log_message "🧹 Removendo containers órfãos..."
docker container prune -f

# 3. Remover imagens antigas
log_message "🗑️ Removendo imagens antigas..."

# Remover imagens relacionadas ao projeto
docker images --format "table {{.Repository}}:{{.Tag}}" | grep -E "(crypto|1crypten)" | while read image; do
    if [ "$image" != "REPOSITORY:TAG" ]; then
        log_message "🗑️ Removendo imagem: $image"
        docker rmi "$image" -f 2>/dev/null || true
    fi
done

# Remover imagens não utilizadas
log_message "🧹 Limpando imagens não utilizadas..."
docker image prune -f

# 4. Remover volumes órfãos
log_message "💾 Removendo volumes órfãos..."
docker volume prune -f

# 5. Remover redes órfãs
log_message "🌐 Removendo redes órfãs..."
docker network prune -f

# 6. Verificar espaço em disco
log_message "💽 Verificando espaço em disco..."
docker system df

# 7. Preparar ambiente
log_message "⚙️ Preparando ambiente..."

# Verificar se arquivos necessários existem
required_files=(
    "docker-compose.prod.yml"
    "front/Dockerfile"
    "back/Dockerfile"
    "nginx/nginx.prod.conf"
)

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        log_message "❌ Arquivo necessário não encontrado: $file"
        exit 1
    else
        log_message "✅ Arquivo encontrado: $file"
    fi
done

# 8. Build do Frontend
log_message "🔨 Construindo imagem do Frontend..."
cd front

# Limpar cache do npm
log_message "🧹 Limpando cache do npm..."
npm cache clean --force 2>/dev/null || true

# Verificar se node_modules existe
if [ ! -d "node_modules" ]; then
    log_message "📦 Instalando dependências do frontend..."
    npm install --legacy-peer-deps
else
    log_message "✅ node_modules já existe"
fi

# Build de produção
log_message "⚡ Executando build de produção..."
NODE_ENV=production npm run build

# Verificar se build foi bem-sucedido
if [ ! -f "dist/index.html" ]; then
    log_message "❌ Build do frontend falhou - index.html não encontrado"
    exit 1
fi

# Verificar se manifest.json está presente
if [ ! -f "dist/manifest.json" ]; then
    log_message "⚠️ manifest.json não encontrado, copiando..."
    cp public/manifest.json dist/ 2>/dev/null || true
fi

log_message "✅ Build do frontend concluído"
cd ..

# 9. Build das imagens Docker
log_message "🐳 Construindo imagens Docker..."

# Frontend
log_message "🔨 Construindo imagem do frontend..."
docker build -t crypto-frontend:latest ./front
if [ $? -eq 0 ]; then
    log_message "✅ Imagem do frontend construída com sucesso"
else
    log_message "❌ Falha ao construir imagem do frontend"
    exit 1
fi

# Backend
log_message "🔨 Construindo imagem do backend..."
docker build -t crypto-backend:latest ./back
if [ $? -eq 0 ]; then
    log_message "✅ Imagem do backend construída com sucesso"
else
    log_message "❌ Falha ao construir imagem do backend"
    exit 1
fi

# 10. Verificar imagens criadas
log_message "🔍 Verificando imagens criadas..."
docker images | grep crypto

# 11. Criar rede personalizada
log_message "🌐 Criando rede personalizada..."
docker network create crypto-network 2>/dev/null || log_message "ℹ️ Rede crypto-network já existe"

# 12. Iniciar serviços com docker-compose
log_message "🚀 Iniciando serviços com docker-compose..."

# Usar arquivo de produção otimizado se existir
if [ -f "docker-compose_504_fix.yml" ]; then
    log_message "📋 Usando configuração otimizada: docker-compose_504_fix.yml"
    COMPOSE_FILE="docker-compose_504_fix.yml"
else
    log_message "📋 Usando configuração padrão: docker-compose.prod.yml"
    COMPOSE_FILE="docker-compose.prod.yml"
fi

# Iniciar serviços em ordem
log_message "🔄 Iniciando PostgreSQL..."
docker-compose -f "$COMPOSE_FILE" up -d postgres
sleep 15

log_message "🔄 Iniciando Redis..."
docker-compose -f "$COMPOSE_FILE" up -d redis
sleep 10

log_message "🔄 Iniciando Backend..."
docker-compose -f "$COMPOSE_FILE" up -d backend
sleep 30

log_message "🔄 Iniciando Frontend..."
docker-compose -f "$COMPOSE_FILE" up -d frontend
sleep 20

log_message "🔄 Iniciando Nginx..."
docker-compose -f "$COMPOSE_FILE" up -d nginx
sleep 15

# 13. Verificar status dos containers
log_message "📊 Verificando status dos containers..."
docker-compose -f "$COMPOSE_FILE" ps

# 14. Verificar logs para erros
log_message "📋 Verificando logs recentes..."
echo "=== LOGS DO BACKEND ==="
docker logs crypto-backend --tail 20 2>/dev/null || echo "Container backend não encontrado"

echo "=== LOGS DO FRONTEND ==="
docker logs crypto-frontend --tail 20 2>/dev/null || echo "Container frontend não encontrado"

echo "=== LOGS DO NGINX ==="
docker logs crypto-nginx --tail 20 2>/dev/null || echo "Container nginx não encontrado"

# 15. Testes de conectividade
log_message "🔍 Executando testes de conectividade..."

# Função de teste de endpoint
test_endpoint() {
    local url=$1
    local name=$2
    local max_attempts=5
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s --max-time 10 "$url" > /dev/null 2>&1; then
            log_message "✅ $name: OK"
            return 0
        else
            log_message "⏳ $name: Tentativa $attempt/$max_attempts falhou"
            sleep 5
            ((attempt++))
        fi
    done
    
    log_message "❌ $name: FALHOU após $max_attempts tentativas"
    return 1
}

# Testes internos (dentro da rede Docker)
log_message "🔍 Testando conectividade interna..."
test_endpoint "http://localhost:5000/api/health" "Backend Health"
test_endpoint "http://localhost:3000/health" "Frontend Health" 
test_endpoint "http://localhost:80/health" "Nginx Health"

# 16. Informações finais
log_message "📊 Informações do sistema:"
echo "=== CONTAINERS ATIVOS ==="
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo "=== IMAGENS CRIADAS ==="
docker images --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}" | grep crypto

echo "=== USO DE RECURSOS ==="
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"

echo "=== ESPAÇO EM DISCO ==="
docker system df

# 17. Resultado final
running_containers=$(docker ps --format "{{.Names}}" | grep -c crypto || echo "0")
expected_containers=5  # postgres, redis, backend, frontend, nginx

if [ "$running_containers" -eq "$expected_containers" ]; then
    log_message "🎉 Sistema reconstruído com sucesso!"
    log_message "✅ Todos os $expected_containers containers estão rodando"
    log_message "🌐 Sistema disponível em: http://localhost"
    log_message "📊 Backend API: http://localhost:5000"
    log_message "📱 Frontend: http://localhost:3000"
    
    echo ""
    echo "🚀 PRÓXIMOS PASSOS:"
    echo "1. Testar o sistema localmente"
    echo "2. Verificar se todas as funcionalidades estão funcionando"
    echo "3. Fazer push das alterações para o repositório"
    echo "4. Fazer deploy no Coolify"
    echo ""
    echo "📋 COMANDOS ÚTEIS:"
    echo "- Ver logs: docker-compose -f $COMPOSE_FILE logs -f [service]"
    echo "- Restart: docker-compose -f $COMPOSE_FILE restart [service]"
    echo "- Parar tudo: docker-compose -f $COMPOSE_FILE down"
    echo "- Status: docker-compose -f $COMPOSE_FILE ps"
    
    exit 0
else
    log_message "⚠️ Sistema parcialmente reconstruído"
    log_message "🔍 $running_containers de $expected_containers containers rodando"
    log_message "📞 Verifique os logs para identificar problemas"
    
    echo ""
    echo "🔧 TROUBLESHOOTING:"
    echo "1. Verificar logs: docker-compose -f $COMPOSE_FILE logs"
    echo "2. Verificar recursos: docker stats"
    echo "3. Verificar portas: netstat -tulpn | grep :80"
    echo "4. Restart manual: docker-compose -f $COMPOSE_FILE up -d"
    
    exit 1
fi