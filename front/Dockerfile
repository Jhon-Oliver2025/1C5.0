# Usar Node.js 20 Alpine (para compatibilidade com dependências)
FROM node:20-alpine

# Instalar dependências básicas
RUN apk add --no-cache git

WORKDIR /app

# Copiar package files
COPY package*.json ./

# Instalar todas as dependências (incluindo dev dependencies para build)
RUN npm ci --legacy-peer-deps

# Copiar arquivos de configuração
COPY tsconfig*.json ./
COPY vite.config.ts ./
COPY index.html ./

# Copiar código fonte
COPY src/ ./src/
COPY public/ ./public/

# Configurar ambiente
ENV NODE_ENV=production
ENV CI=true

# Build simples
RUN npm run build

# Estágio 2: Servir com Node.js (sem Nginx)
FROM node:20-alpine

# Instalar curl para health check e serve para servir arquivos
RUN apk add --no-cache curl && npm install -g serve

# Copiar arquivos buildados
COPY --from=0 /app/dist /app

# Criar fallback se necessário
RUN test -f /app/index.html || echo '<h1>Build Error</h1>' > /app/index.html

# Expor porta
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:80/ || exit 1

# Comando para servir arquivos estáticos
CMD ["serve", "-s", "/app", "-l", "80"]