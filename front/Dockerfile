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

# Remover configuração padrão e copiar nossa configuração
RUN rm -f /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/nginx.conf

# Criar manifest.json se não existir
RUN test -f /usr/share/nginx/html/manifest.json || echo '{"name":"1Crypten - Trading Signals","short_name":"1Crypten","description":"Plataforma avançada de sinais de trading para criptomoedas","start_url":"/","display":"standalone","background_color":"#000000","theme_color":"#646cff","orientation":"portrait-primary","scope":"/","lang":"pt-BR","icons":[{"src":"/icons/icon-192x192.png","sizes":"192x192","type":"image/png","purpose":"any maskable"},{"src":"/icons/icon-512x512.png","sizes":"512x512","type":"image/png","purpose":"any maskable"}]}' > /usr/share/nginx/html/manifest.json

# Criar fallback se necessário
RUN test -f /usr/share/nginx/html/index.html || echo '<h1>Build Error</h1>' > /usr/share/nginx/html/index.html

# Expor porta
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:80/ || exit 1

# Comando para iniciar Nginx
CMD ["nginx", "-g", "daemon off;"]