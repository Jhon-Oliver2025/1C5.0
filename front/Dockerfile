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

# Estágio 2: Servir com Nginx
FROM nginx:alpine

# Instalar curl para health check
RUN apk add --no-cache curl

# Copiar arquivos buildados
COPY --from=0 /app/dist /usr/share/nginx/html

# Copiar manifest.json diretamente da pasta local
COPY public/manifest.json /usr/share/nginx/html/manifest.json

# Copiar configuração customizada do Nginx
COPY nginx.conf /etc/nginx/nginx.conf

# Criar fallback se necessário
RUN test -f /usr/share/nginx/html/index.html || echo '<h1>Build Error</h1>' > /usr/share/nginx/html/index.html

# Expor porta
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:80/ || exit 1

# Comando para iniciar Nginx
CMD ["nginx", "-g", "daemon off;"]