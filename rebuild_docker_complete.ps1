#!/usr/bin/env pwsh
# Script para reconstruir completamente o sistema Docker
# Autor: Assistente AI
# Data: 2025-08-30

Write-Host "REBUILD COMPLETO DO SISTEMA DOCKER" -ForegroundColor Red
Write-Host "Iniciado em: $(Get-Date)" -ForegroundColor Yellow

# Funcao para executar comandos com log
function Invoke-CommandWithLog {
    param(
        [string]$Command,
        [string]$Description
    )
    
    Write-Host "\n$Description" -ForegroundColor Cyan
    Write-Host "Executando: $Command" -ForegroundColor Gray
    
    try {
        Invoke-Expression $Command
        Write-Host "Sucesso: $Description" -ForegroundColor Green
    }
    catch {
        Write-Host "Erro: $Description - $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "Continuando mesmo assim..." -ForegroundColor Yellow
    }
}

# Parar todos os containers
Write-Host "\nParando todos os containers..." -ForegroundColor Cyan
try { docker stop $(docker ps -aq) } catch { Write-Host "Nenhum container para parar" }

# Remover todos os containers
Write-Host "Removendo todos os containers..." -ForegroundColor Cyan
try { docker rm -f $(docker ps -aq) } catch { Write-Host "Nenhum container para remover" }

# Remover imagens do projeto
Write-Host "Removendo imagens do projeto..." -ForegroundColor Cyan
try { 
    docker images | Select-String "1c5|crypto|front|back" | ForEach-Object {
        $imageId = ($_ -split "\s+")[2]
        docker rmi -f $imageId
    }
} catch { Write-Host "Erro ao remover imagens" }

# Limpar volumes
Write-Host "Limpando volumes orfaos..." -ForegroundColor Cyan
try { docker volume prune -f } catch { Write-Host "Erro ao limpar volumes" }

# Limpar networks
Write-Host "Limpando networks orfaas..." -ForegroundColor Cyan
try { docker network prune -f } catch { Write-Host "Erro ao limpar networks" }

# Limpar build cache
Write-Host "Limpando build cache..." -ForegroundColor Cyan
try { docker builder prune -af } catch { Write-Host "Erro ao limpar cache" }

# Limpar sistema completo
Write-Host "Limpeza completa do sistema..." -ForegroundColor Cyan
try { docker system prune -af --volumes } catch { Write-Host "Erro na limpeza completa" }

Write-Host "\nLIMPEZA COMPLETA FINALIZADA" -ForegroundColor Green

# Aguardar um pouco
Write-Host "\nAguardando 5 segundos para estabilizar..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Verificar se Docker esta funcionando
Write-Host "\nVerificando status do Docker..." -ForegroundColor Cyan
try {
    docker version | Out-Null
    Write-Host "Docker esta funcionando" -ForegroundColor Green
}
catch {
    Write-Host "Docker nao esta respondendo" -ForegroundColor Red
    Write-Host "Tentando reiniciar Docker Desktop..." -ForegroundColor Yellow
    
    try {
        Stop-Process -Name "Docker Desktop" -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 10
        Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
        Write-Host "Docker Desktop reiniciado" -ForegroundColor Green
        Write-Host "Aguardando Docker inicializar (60 segundos)..." -ForegroundColor Yellow
        Start-Sleep -Seconds 60
    }
    catch {
        Write-Host "Erro ao reiniciar Docker Desktop: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "\nINICIANDO REBUILD DO SISTEMA" -ForegroundColor Blue

# Navegar para o diretorio do projeto
Set-Location "C:\Users\spcom\Desktop\1C5.0"

# Build e start do sistema local
Write-Host "\nConstruindo sistema local..." -ForegroundColor Cyan
try {
    docker-compose -f docker-compose.local.yml build --no-cache
    Write-Host "Build completo sem cache - SUCESSO" -ForegroundColor Green
}
catch {
    Write-Host "Erro no build: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "\nIniciando sistema local..." -ForegroundColor Cyan
try {
    docker-compose -f docker-compose.local.yml up -d
    Write-Host "Containers iniciados - SUCESSO" -ForegroundColor Green
}
catch {
    Write-Host "Erro ao iniciar containers: $($_.Exception.Message)" -ForegroundColor Red
}

# Aguardar containers iniciarem
Write-Host "\nAguardando containers iniciarem (30 segundos)..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Verificar status dos containers
Write-Host "\nStatus dos containers:" -ForegroundColor Cyan
docker-compose -f docker-compose.local.yml ps

# Verificar logs
Write-Host "\nLogs do backend:" -ForegroundColor Cyan
docker-compose -f docker-compose.local.yml logs --tail=20 backend

Write-Host "\nLogs do frontend:" -ForegroundColor Cyan
docker-compose -f docker-compose.local.yml logs --tail=20 frontend

# Testar APIs
Write-Host "\nTestando APIs..." -ForegroundColor Cyan

Write-Host "\nTestando API Status:" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:5000/api/status" -Method GET -TimeoutSec 10
    Write-Host "API Status: $($response | ConvertTo-Json)" -ForegroundColor Green
}
catch {
    Write-Host "API Status falhou: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "\nTestando API Signals:" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:5000/api/signals" -Method GET -TimeoutSec 10
    Write-Host "API Signals: $($response.Count) sinais retornados" -ForegroundColor Green
}
catch {
    Write-Host "API Signals falhou: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "\nTestando Frontend:" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8080" -Method GET -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Host "Frontend: Carregando corretamente" -ForegroundColor Green
    }
}
catch {
    Write-Host "Frontend falhou: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "\nREBUILD COMPLETO FINALIZADO" -ForegroundColor Green
Write-Host "Finalizado em: $(Get-Date)" -ForegroundColor Yellow
Write-Host "\nURLs para testar:" -ForegroundColor Cyan
Write-Host "   Frontend: http://localhost:8080" -ForegroundColor White
Write-Host "   Backend:  http://localhost:5000" -ForegroundColor White
Write-Host "   API:      http://localhost:5000/api/status" -ForegroundColor White
Write-Host "\nPara ver logs em tempo real:" -ForegroundColor Cyan
Write-Host "   docker-compose -f docker-compose.local.yml logs -f" -ForegroundColor White
Write-Host "\nPara parar o sistema:" -ForegroundColor Cyan
Write-Host "   docker-compose -f docker-compose.local.yml down" -ForegroundColor White