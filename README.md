# 1Crypten - Sistema de Sinais de Criptomoedas

Sistema completo de análise técnica e sinais de trading para criptomoedas, desenvolvido com React (frontend) e Flask (backend). Inclui PWA (Progressive Web App) para experiência mobile nativa.

## 🚀 Funcionalidades Principais

### 📱 PWA (Progressive Web App)
- **Instalação nativa**: Funciona como app no celular
- **Offline**: Cache inteligente para uso sem internet
- **Notificações**: Sistema de notificações push
- **Responsivo**: Design otimizado para todos os dispositivos
- **Service Worker**: Atualizações automáticas e cache eficiente

### 📊 Dashboard e Análises
- **Sinais de Trading**: Análise técnica automatizada
- **BTC Analysis**: Monitoramento avançado do Bitcoin
- **Simulação de Trading**: Investimentos simulados
- **CRM**: Gestão completa de usuários e vendas
- **Área de Membros**: Cursos e conteúdo exclusivo

### 🎨 Interface Moderna
- **Design responsivo**: Mobile-first approach
- **Containers motivacionais**: Mensagens inspiracionais
- **Navegação intuitiva**: UX otimizada
- **Notificações elegantes**: Toast notifications sutis

## 🛠️ Desenvolvimento Local

### Pré-requisitos
- Node.js 18+ e npm
- Python 3.9+ e pip
- Supabase configurado
- Arquivo `.env` configurado

### Como Executar

```bash
# 1. Clone o repositório
git clone <repo-url>
cd 1C5.0

# 2. Configure as variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env com suas configurações

# 3. Inicie o backend
cd back
pip install -r requirements.txt
python app_supabase.py

# 4. Inicie o frontend (novo terminal)
cd front
npm install
npm run dev
```

### Acessos Locais
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **PWA**: http://localhost:3000/app

## 🐳 Deploy com Docker

### Produção (Coolify)
```bash
# Deploy automático via Coolify
# Arquivo: docker-compose.coolify.yml
```

### Desenvolvimento
```bash
# Inicie com Docker
docker-compose -f docker-compose.dev.yml up -d

# Ver logs
docker logs crypto-frontend
docker logs crypto-backend
```

## 🏗️ Arquitetura

- **Backend**: Python Flask + PostgreSQL + Redis
- **Frontend**: React + TypeScript + Vite
- **Deploy**: Docker + Coolify
- **Automação**: n8n workflows

## 🚀 Deploy Rápido

```bash
# Clone o repositório
git clone <repo-url>
cd crypto-signals

# Configure variáveis de ambiente
cp .env.example .env

# Execute com Docker
docker-compose up -d
```

## 📊 Funcionalidades

- ✅ Análise técnica automatizada
- ✅ Sinais em tempo real
- ✅ Dashboard executivo
- ✅ Integração Binance
- ✅ Notificações Telegram
- ✅ Sistema de usuários

## 🔧 Desenvolvimento

### Backend
```bash
cd back
pip install -r requirements.txt
python app.py
```

### Frontend
```bash
cd front
npm install
npm run dev
```

## 📈 Roadmap

- [ ] Integração com mais exchanges
- [ ] IA para análise preditiva
- [ ] Mobile app
- [ ] API pública