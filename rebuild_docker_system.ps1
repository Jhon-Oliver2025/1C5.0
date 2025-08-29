# Script PowerShell para Recriar Sistema Docker Completo - 1Crypten
# Data: 29/08/2025
# Objetivo: Reconstruir todas as imagens após falha dos containers

Write-Host "Iniciando reconstrução completa do sistema Docker..." -ForegroundColor Green
Write-Host "Data: $(Get-Date)" -ForegroundColor Cyan
Write-Host "Objetivo: Recriar todas as imagens e containers" -ForegroundColor Yellow

# Função de log
function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$timestamp] $Message" -ForegroundColor White
}

# 1. Parar e remover todos os containers
Write-Log "Parando e removendo containers existentes..."
try {
    # Parar todos os containers
    docker stop $(docker ps -aq) 2>$null
    # Remover todos os containers
    docker rm $(docker ps -aq) 2>$null
    # Remover containers órfãos
    docker container prune -f
    Write-Log "Containers removidos com sucesso"
}
catch {
    Write-Log "Erro ao remover containers: $($_.Exception.Message)"
}

# 2. Remover imagens antigas
Write-Log "Removendo imagens antigas..."
try {
    # Remover todas as imagens
    docker rmi $(docker images -q) -f 2>$null
    # Remover imagens não utilizadas
    docker image prune -f
    Write-Log "Imagens removidas com sucesso"
}
catch {
    Write-Log "Erro ao remover imagens: $($_.Exception.Message)"
}

# 3. Limpeza geral
Write-Log "Executando limpeza geral..."
docker volume prune -f
docker network prune -f
docker system prune -f

# 4. Verificar arquivos necessários
Write-Log "Verificando arquivos necessários..."
$requiredFiles = @(
    "docker-compose.prod.yml",
    "front\Dockerfile",
    "back\Dockerfile"
)

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Log "Arquivo encontrado: $file"
    } else {
        Write-Host "ERRO: Arquivo necessário não encontrado: $file" -ForegroundColor Red
        exit 1
    }
}

# 5. Build do Frontend
Write-Log "Construindo build do Frontend..."
Set-Location "front"

try {
    # Limpar cache do npm
    Write-Log "Limpando cache do npm..."
    npm cache clean --force 2>$null
    
    # Instalar dependências se necessário
    if (-not (Test-Path "node_modules")) {
        Write-Log "Instalando dependências do frontend..."
        npm install --legacy-peer-deps
    }
    
    # Build de produção
    Write-Log "Executando build de produção..."
    $env:NODE_ENV = "production"
    npm run build
    
    # Verificar se build foi bem-sucedido
    if (-not (Test-Path "dist\index.html")) {
        Write-Host "ERRO: Build do frontend falhou" -ForegroundColor Red
        exit 1
    }
    
    # Copiar manifest.json se necessário
    if (-not (Test-Path "dist\manifest.json") -and (Test-Path "public\manifest.json")) {
        Copy-Item "public\manifest.json" "dist\" -Force
    }
    
    Write-Log "Build do frontend concluído com sucesso"
}
catch {
    Write-Host "ERRO no build do frontend: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
finally {
    Set-Location ".."
}

# 6. Build das imagens Docker
Write-Log "Construindo imagens Docker..."

# Frontend
Write-Log "Construindo imagem do frontend..."
docker build -t crypto-frontend:latest ./front
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERRO: Falha ao construir imagem do frontend" -ForegroundColor Red
    exit 1
}
Write-Log "Imagem do frontend construída com sucesso"

# Backend
Write-Log "Construindo imagem do backend..."
docker build -t crypto-backend:latest ./back
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERRO: Falha ao construir imagem do backend" -ForegroundColor Red
    exit 1
}
Write-Log "Imagem do backend construída com sucesso"

# 7. Verificar imagens criadas
Write-Log "Verificando imagens criadas..."
docker images

# 8. Iniciar serviços com docker-compose
Write-Log "Iniciando serviços com docker-compose..."

# Escolher arquivo de configuração
if (Test-Path "docker-compose_504_fix.yml") {
    $composeFile = "docker-compose_504_fix.yml"
    Write-Log "Usando configuração otimizada: $composeFile"
} else {
    $composeFile = "docker-compose.prod.yml"
    Write-Log "Usando configuração padrão: $composeFile"
}

# Iniciar todos os serviços
Write-Log "Iniciando todos os serviços..."
docker-compose -f $composeFile up -d

# Aguardar inicialização
Write-Log "Aguardando inicialização dos serviços..."
Start-Sleep -Seconds 30

# 9. Verificar status dos containers
Write-Log "Verificando status dos containers..."
docker-compose -f $composeFile ps

# 10. Verificar containers rodando
$runningContainers = (docker ps --format "{{.Names}}").Count
Write-Log "Containers rodando: $runningContainers"

# 11. Mostrar logs recentes
Write-Log "Verificando logs recentes..."
Write-Host "=== CONTAINERS ATIVOS ===" -ForegroundColor Yellow
docker ps

Write-Host "=== IMAGENS CRIADAS ===" -ForegroundColor Yellow
docker images

# 12. Resultado final
if ($runningContainers -gt 0) {
    Write-Host "Sistema reconstruído com sucesso!" -ForegroundColor Green
    Write-Log "$runningContainers containers estão rodando"
    Write-Log "Sistema disponível em: http://localhost"
    Write-Log "Backend API: http://localhost:5000"
    Write-Log "Frontend: http://localhost:3000"
    
    Write-Host ""
    Write-Host "PRÓXIMOS PASSOS:" -ForegroundColor Cyan
    Write-Host "1. Testar o sistema localmente"
    Write-Host "2. Verificar se todas as funcionalidades estão funcionando"
    Write-Host "3. Fazer push das alterações para o repositório"
    Write-Host "4. Fazer deploy no Coolify"
    
    Write-Host ""
    Write-Host "COMANDOS ÚTEIS:" -ForegroundColor Cyan
    Write-Host "- Ver logs: docker-compose -f $composeFile logs -f [service]"
    Write-Host "- Restart: docker-compose -f $composeFile restart [service]"
    Write-Host "- Parar tudo: docker-compose -f $composeFile down"
    Write-Host "- Status: docker-compose -f $composeFile ps"
    
} else {
    Write-Host "AVISO: Sistema parcialmente reconstruído" -ForegroundColor Yellow
    Write-Log "Verifique os logs para identificar problemas"
    
    Write-Host ""
    Write-Host "TROUBLESHOOTING:" -ForegroundColor Red
    Write-Host "1. Verificar logs: docker-compose -f $composeFile logs"
    Write-Host "2. Verificar recursos: docker stats"
    Write-Host "3. Restart manual: docker-compose -f $composeFile up -d"
}

Write-Host ""
Write-Host "Script de reconstrução concluído!" -ForegroundColor Green