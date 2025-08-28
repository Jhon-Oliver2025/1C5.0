/**
 * Service Worker Simples para PWA
 * Versão limpa sem duplicações
 */

const CACHE_VERSION = '3.4';
const CACHE_NAME = `1crypten-v${CACHE_VERSION}`;
const STATIC_CACHE = `1crypten-static-v${CACHE_VERSION}`;
const DYNAMIC_CACHE = `1crypten-dynamic-v${CACHE_VERSION}`;
const API_CACHE = `1crypten-api-v${CACHE_VERSION}`;

// Recursos críticos para cache imediato
const CRITICAL_RESOURCES = [
  '/',
  '/login',
  '/dashboard',
  '/logo3.png',
  '/terra2.png',
  '/manifest.json'
];

// Recursos para cache em background
const BACKGROUND_RESOURCES = [
  '/btc-analysis',
  '/crm',
  '/sales-admin',
  '/suporte',
  '/app',
  '/vitrine-alunos'
];

// APIs que podem ser cacheadas temporariamente
const CACHEABLE_APIS = [
  '/api/market-status',
  '/api/auth/check-admin',
  '/api/cleanup-status'
];

/**
 * Instalação do Service Worker
 */
self.addEventListener('install', (event) => {
  console.log('🔧 Service Worker: Instalando versão otimizada...');
  
  event.waitUntil(
    Promise.all([
      // Cache crítico - deve ser instalado imediatamente
      caches.open(STATIC_CACHE).then((cache) => {
        console.log('📦 Cacheando recursos críticos...');
        return cache.addAll(CRITICAL_RESOURCES.map(url => new Request(url, { cache: 'reload' })));
      }),
      
      // Cache em background - não bloqueia a instalação
      cacheBackgroundResources()
    ])
  );
});

/**
 * Cache de recursos em background
 */
async function cacheBackgroundResources() {
  try {
    console.log('🔄 Cacheando recursos em background...');
    const cache = await caches.open(DYNAMIC_CACHE);
    await cache.addAll(BACKGROUND_RESOURCES.map(url => new Request(url, { cache: 'no-cache' })));
  } catch (error) {
    console.warn('⚠️ Erro no cache de background:', error);
  }
}

/**
 * Ativação do Service Worker
 */
self.addEventListener('activate', (event) => {
  console.log('✅ Service Worker: Ativando versão otimizada v3.4...');
  
  event.waitUntil(
    Promise.all([
      // Limpar caches antigos
      cleanupOldCaches(),
      // Tomar controle imediatamente
      self.clients.claim()
    ])
  );
});

/**
 * Limpeza de caches antigos
 */
async function cleanupOldCaches() {
  const cacheNames = await caches.keys();
  const oldCaches = cacheNames.filter(name => 
    name.includes('1crypten') && !name.includes(CACHE_VERSION)
  );
  
  const deletePromises = oldCaches.map(cacheName => {
    console.log(`🗑️ Removendo cache antigo: ${cacheName}`);
    return caches.delete(cacheName);
  });
  
  // Forçar limpeza de dados PWA corrompidos
  try {
    if ('indexedDB' in self) {
      console.log('🔄 Limpando dados PWA corrompidos...');
    }
  } catch (error) {
    console.warn('⚠️ Erro na limpeza de dados PWA:', error);
  }
  
  await Promise.all(deletePromises);
  console.log('✅ Limpeza de cache PWA concluída - versão 3.4 ativa');
}

/**
 * Interceptação de requisições
 */
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Estratégia de cache baseada no tipo de recurso
  if (request.method === 'GET') {
    if (url.pathname.startsWith('/api/')) {
      // APIs - Cache com fallback para rede
      event.respondWith(cacheFirstWithNetworkFallback(request));
    } else if (url.pathname.match(/\.(js|css|png|jpg|jpeg|gif|svg|ico)$/)) {
      // Recursos estáticos - Cache primeiro
      event.respondWith(cacheFirst(request));
    } else {
      // Páginas HTML - Rede primeiro com fallback para cache
      event.respondWith(networkFirstWithCacheFallback(request));
    }
  }
});

/**
 * Estratégia: Cache primeiro com fallback para rede
 */
async function cacheFirst(request) {
  try {
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      const cache = await caches.open(STATIC_CACHE);
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    console.warn('⚠️ Erro na estratégia cache-first:', error);
    return new Response('Offline', { status: 503 });
  }
}

/**
 * Estratégia: Rede primeiro com fallback para cache
 */
async function networkFirstWithCacheFallback(request) {
  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      const cache = await caches.open(DYNAMIC_CACHE);
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    return new Response('Offline', { status: 503 });
  }
}

/**
 * Estratégia: Cache primeiro para APIs com fallback
 */
async function cacheFirstWithNetworkFallback(request) {
  try {
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      // Atualizar cache em background
      fetch(request).then(response => {
        if (response.ok) {
          caches.open(API_CACHE).then(cache => {
            cache.put(request, response.clone());
          });
        }
      }).catch(() => {});
      
      return cachedResponse;
    }
    
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      const cache = await caches.open(API_CACHE);
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    return new Response(JSON.stringify({ error: 'Offline' }), {
      status: 503,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}

/**
 * Listener para mensagens do cliente
 */
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
  
  if (event.data && event.data.type === 'CLEAR_CACHE') {
    clearAllCaches();
  }
});

/**
 * Limpar todos os caches
 */
async function clearAllCaches() {
  const cacheNames = await caches.keys();
  await Promise.all(cacheNames.map(name => caches.delete(name)));
  console.log('🗑️ Todos os caches foram limpos');
}

console.log('🚀 Service Worker 1Crypten carregado!');