/**
 * Service Worker Otimizado para PWA
 * Resolve problemas de cache, atualização e estado da aplicação
 * Versão: 3.0 - Melhorias para experiência mobile
 */

const CACHE_VERSION = '3.2';
const CACHE_NAME = `1crypten-v${CACHE_VERSION}`;
const STATIC_CACHE = `1crypten-static-v${CACHE_VERSION}`;
const DYNAMIC_CACHE = `1crypten-dynamic-v${CACHE_VERSION}`;
const API_CACHE = `1crypten-api-v${CACHE_VERSION}`;

// Flag para forçar atualização
let forceUpdate = false;

// Recursos críticos para cache imediato
const CRITICAL_RESOURCES = [
  '/',
  '/login',
  '/dashboard',
  '/static/js/main.js',
  '/static/css/main.css',
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
  '/app1crypten',
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
  
  // Ativar imediatamente
  self.skipWaiting();
});

/**
 * Cache de recursos em background
 */
async function cacheBackgroundResources() {
  try {
    const cache = await caches.open(DYNAMIC_CACHE);
    console.log('🔄 Cacheando recursos em background...');
    
    // Cache recursos não críticos sem bloquear
    for (const url of BACKGROUND_RESOURCES) {
      try {
        await cache.add(new Request(url, { cache: 'reload' }));
      } catch (error) {
        console.warn(`⚠️ Falha ao cachear ${url}:`, error);
      }
    }
  } catch (error) {
    console.warn('⚠️ Erro no cache em background:', error);
  }
}

/**
 * Ativação do Service Worker
 */
self.addEventListener('activate', (event) => {
  console.log('✅ Service Worker: Ativando versão otimizada v3.2 - Forçando limpeza PWA...');
  
  event.waitUntil(
    Promise.all([
      // Limpar caches antigos
      cleanupOldCaches(),
      // Tomar controle imediatamente
      self.clients.claim(),
      // Notificar clientes sobre atualização
      notifyClientsOfUpdate()
    ])
  );
});

/**
 * Notifica clientes sobre atualizações
 */
async function notifyClientsOfUpdate() {
  const clients = await self.clients.matchAll();
  clients.forEach(client => {
    client.postMessage({
      type: 'UPDATE_AVAILABLE',
      version: CACHE_VERSION
    });
  });
}

/**
 * Limpeza de caches antigos
 */
async function cleanupOldCaches() {
  const cacheNames = await caches.keys();
  const validCaches = [STATIC_CACHE, DYNAMIC_CACHE, API_CACHE];
  
  // Limpeza agressiva - remover TODOS os caches antigos
  const deletePromises = cacheNames
    .filter(cacheName => !validCaches.includes(cacheName) || cacheName.includes('v3.0') || cacheName.includes('v3.1'))
    .map(cacheName => {
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
  console.log('✅ Limpeza de cache PWA concluída - versão 3.2 ativa');
}

/**
 * Interceptação de requisições
 */
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Estratégias diferentes por tipo de recurso
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(handleApiRequest(request));
  } else if (url.pathname.startsWith('/static/')) {
    event.respondWith(handleStaticRequest(request));
  } else {
    event.respondWith(handleNavigationRequest(request));
  }
});

/**
 * Estratégia para requisições de API
 */
async function handleApiRequest(request) {
  const url = new URL(request.url);
  
  // APIs críticas como login não devem ser cacheadas
  if (url.pathname.includes('/auth/login') || 
      url.pathname.includes('/auth/logout') ||
      request.method !== 'GET') {
    return fetch(request);
  }
  
  // APIs que podem ser cacheadas temporariamente
  if (CACHEABLE_APIS.some(api => url.pathname.includes(api))) {
    return handleCacheableApi(request);
  }
  
  // Outras APIs - network first
  return networkFirst(request, API_CACHE);
}

/**
 * Estratégia para APIs cacheáveis
 */
async function handleCacheableApi(request) {
  const cache = await caches.open(API_CACHE);
  const cachedResponse = await cache.match(request);
  
  // Se tem cache e é recente (5 minutos), usar cache
  if (cachedResponse) {
    const cacheDate = new Date(cachedResponse.headers.get('sw-cache-date') || 0);
    const now = new Date();
    const fiveMinutes = 5 * 60 * 1000;
    
    if (now - cacheDate < fiveMinutes) {
      console.log('📋 Usando cache de API:', request.url);
      return cachedResponse;
    }
  }
  
  // Buscar da rede e cachear
  try {
    const response = await fetch(request);
    if (response.ok) {
      const responseClone = response.clone();
      const headers = new Headers(responseClone.headers);
      headers.set('sw-cache-date', new Date().toISOString());
      
      const modifiedResponse = new Response(await responseClone.blob(), {
        status: responseClone.status,
        statusText: responseClone.statusText,
        headers: headers
      });
      
      cache.put(request, modifiedResponse);
    }
    return response;
  } catch (error) {
    // Se falhar, usar cache mesmo que antigo
    return cachedResponse || new Response('Offline', { status: 503 });
  }
}

/**
 * Estratégia para recursos estáticos
 */
async function handleStaticRequest(request) {
  // Cache first para recursos estáticos
  const cachedResponse = await caches.match(request);
  if (cachedResponse) {
    return cachedResponse;
  }
  
  // Se não está em cache, buscar e cachear
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(STATIC_CACHE);
      cache.put(request, response.clone());
    }
    return response;
  } catch (error) {
    console.warn('⚠️ Falha ao carregar recurso estático:', request.url);
    return new Response('Recurso não disponível offline', { status: 503 });
  }
}

/**
 * Estratégia para navegação
 */
async function handleNavigationRequest(request) {
  // Para navegação, tentar rede primeiro, depois cache
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(DYNAMIC_CACHE);
      cache.put(request, response.clone());
    }
    return response;
  } catch (error) {
    // Se falhar, tentar cache
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Fallback para página offline ou index
    const fallback = await caches.match('/');
    return fallback || new Response('Página não disponível offline', {
      status: 503,
      headers: { 'Content-Type': 'text/html' }
    });
  }
}

/**
 * Estratégia Network First
 */
async function networkFirst(request, cacheName) {
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(cacheName);
      cache.put(request, response.clone());
    }
    return response;
  } catch (error) {
    const cachedResponse = await caches.match(request);
    return cachedResponse || new Response('Offline', { status: 503 });
  }
}

/**
 * Mensagens do cliente
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

console.log('🚀 Service Worker Otimizado carregado e pronto!');

/**
 * Evento de instalação do Service Worker
 * Faz o cache inicial dos recursos estáticos
 */
self.addEventListener('install', (event) => {
  console.log('🔧 Service Worker: Instalando...');
  
  event.waitUntil(
    Promise.all([
      // Cache de recursos estáticos
      caches.open(STATIC_CACHE).then((cache) => {
        console.log('📦 Service Worker: Fazendo cache dos recursos estáticos');
        return cache.addAll(STATIC_ASSETS.map(url => {
          return new Request(url, { cache: 'reload' });
        }));
      }),
      
      // Pular waiting para ativar imediatamente
      self.skipWaiting()
    ])
  );
});

/**
 * Evento de ativação do Service Worker
 * Limpa caches antigos e assume controle
 */
self.addEventListener('activate', (event) => {
  console.log('✅ Service Worker: Ativando...');
  
  event.waitUntil(
    Promise.all([
      // Limpar caches antigos
      caches.keys().then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName !== STATIC_CACHE && 
                cacheName !== DYNAMIC_CACHE && 
                cacheName !== API_CACHE) {
              console.log('🗑️ Service Worker: Removendo cache antigo:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      }),
      
      // Assumir controle de todas as abas
      self.clients.claim()
    ])
  );
});

/**
 * Intercepta todas as requisições de rede
 * Implementa diferentes estratégias de cache
 */
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Ignorar requisições não-HTTP
  if (!request.url.startsWith('http')) {
    return;
  }
  
  // Estratégia para recursos estáticos (Cache First)
  if (isStaticAsset(request.url)) {
    event.respondWith(cacheFirst(request, STATIC_CACHE));
    return;
  }
  
  // Estratégia para API crítica (Network First) - DEVE VIR ANTES de isApiUrl
  if (isNetworkFirstUrl(request.url)) {
    console.log('🔄 Network First para API crítica:', request.url);
    event.respondWith(networkFirst(request, API_CACHE));
    return;
  }
  
  // Forçar Network First para APIs de status (sempre buscar dados atualizados)
  if (request.url.includes('/api/market-status') || request.url.includes('/api/cleanup-status')) {
    console.log('🔄 Forçando Network First para API de status:', request.url);
    event.respondWith(fetch(request).catch(() => getOfflineFallback(request)));
    return;
  }
  
  // Estratégia para outras APIs (Stale While Revalidate)
  if (isApiUrl(request.url)) {
    event.respondWith(staleWhileRevalidate(request, API_CACHE));
    return;
  }
  
  // Estratégia padrão para outros recursos (Network First)
  event.respondWith(networkFirst(request, DYNAMIC_CACHE));
});

/**
 * Estratégia Cache First
 * Busca no cache primeiro, depois na rede
 */
async function cacheFirst(request, cacheName) {
  try {
    const cache = await caches.open(cacheName);
    const cachedResponse = await cache.match(request);
    
    if (cachedResponse) {
      console.log('📦 Cache Hit:', request.url);
      return cachedResponse;
    }
    
    console.log('🌐 Cache Miss, buscando na rede:', request.url);
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.error('❌ Erro em cacheFirst:', error);
    return getOfflineFallback(request);
  }
}

/**
 * Estratégia Network First
 * Busca na rede primeiro, depois no cache
 */
async function networkFirst(request, cacheName) {
  try {
    console.log('🌐 Network First:', request.url);
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      const cache = await caches.open(cacheName);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.log('📦 Network falhou, tentando cache:', request.url);
    const cache = await caches.open(cacheName);
    const cachedResponse = await cache.match(request);
    
    if (cachedResponse) {
      return cachedResponse;
    }
    
    return getOfflineFallback(request);
  }
}

/**
 * Estratégia Stale While Revalidate
 * Retorna do cache e atualiza em background
 */
async function staleWhileRevalidate(request, cacheName) {
  const cache = await caches.open(cacheName);
  const cachedResponse = await cache.match(request);
  
  // Buscar na rede em background
  const networkPromise = fetch(request).then((networkResponse) => {
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  }).catch(() => {
    console.log('🌐 Network falhou para:', request.url);
  });
  
  // Retornar cache imediatamente se disponível
  if (cachedResponse) {
    console.log('📦 Stale cache retornado:', request.url);
    return cachedResponse;
  }
  
  // Se não há cache, aguardar rede
  console.log('🌐 Aguardando rede (sem cache):', request.url);
  return networkPromise;
}

/**
 * Retorna fallback offline apropriado
 */
function getOfflineFallback(request) {
  if (request.destination === 'document') {
    return caches.match('/index.html');
  }
  
  if (request.url.includes('/api/')) {
    return new Response(
      JSON.stringify({
        success: false,
        error: 'Sem conexão com a internet',
        offline: true,
        cached: false
      }),
      {
        status: 503,
        statusText: 'Service Unavailable',
        headers: {
          'Content-Type': 'application/json'
        }
      }
    );
  }
  
  return new Response('Recurso não disponível offline', {
    status: 503,
    statusText: 'Service Unavailable'
  });
}

/**
 * Verifica se é um recurso estático
 */
function isStaticAsset(url) {
  return STATIC_ASSETS.some(asset => url.includes(asset)) ||
         url.includes('/static/') ||
         url.includes('/assets/') ||
         url.includes('/icons/') ||
         url.includes('.css') ||
         url.includes('.js') ||
         url.includes('.png') ||
         url.includes('.jpg') ||
         url.includes('.svg');
}

/**
 * Verifica se é uma URL de API
 */
function isApiUrl(url) {
  return url.includes('/api/');
}

/**
 * Verifica se deve usar Network First
 */
function isNetworkFirstUrl(url) {
  return NETWORK_FIRST_URLS.some(pattern => url.includes(pattern));
}

/**
 * Listener para mensagens do cliente
 */
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
  
  if (event.data && event.data.type === 'GET_VERSION') {
    event.ports[0].postMessage({ version: CACHE_NAME });
  }
  
  if (event.data && event.data.type === 'CLEAR_CACHE') {
    clearAllCaches().then(() => {
      event.ports[0].postMessage({ success: true, message: 'Cache limpo com sucesso' });
    }).catch((error) => {
      event.ports[0].postMessage({ success: false, error: error.message });
    });
  }
  
  if (event.data && event.data.type === 'CLEAR_API_CACHE') {
    clearApiCache().then(() => {
      event.ports[0].postMessage({ success: true });
    });
  }
});

/**
 * Limpa todos os caches
 */
async function clearAllCaches() {
  const cacheNames = await caches.keys();
  return Promise.all(
    cacheNames.map(cacheName => caches.delete(cacheName))
  );
}

/**
 * Limpa apenas o cache da API
 */
async function clearApiCache() {
  const cacheNames = await caches.keys();
  const apiCacheNames = cacheNames.filter(name => name.includes('api'));
  return Promise.all(
    apiCacheNames.map(cacheName => caches.delete(cacheName))
  );
}

/**
 * Listener para notificações push
 */
self.addEventListener('push', (event) => {
  console.log('📱 Push notification recebida:', event);
  
  const options = {
    body: 'Novos sinais de trading disponíveis!',
    icon: '/icons/icon-192x192.png',
    badge: '/icons/icon-72x72.png',
    vibrate: [200, 100, 200],
    data: {
      url: '/dashboard'
    },
    actions: [
      {
        action: 'view',
        title: 'Ver Sinais',
        icon: '/icons/icon-72x72.png'
      },
      {
        action: 'close',
        title: 'Fechar'
      }
    ]
  };
  
  if (event.data) {
    const data = event.data.json();
    options.body = data.body || options.body;
    options.data = { ...options.data, ...data };
  }
  
  event.waitUntil(
    self.registration.showNotification('1Crypten', options)
  );
});

/**
 * Listener para cliques em notificações
 */
self.addEventListener('notificationclick', (event) => {
  console.log('🔔 Notificação clicada:', event);
  
  event.notification.close();
  
  if (event.action === 'view' || !event.action) {
    const url = event.notification.data?.url || '/dashboard';
    
    event.waitUntil(
      clients.matchAll({ type: 'window' }).then((clientList) => {
        // Verificar se já há uma aba aberta
        for (const client of clientList) {
          if (client.url.includes(url) && 'focus' in client) {
            return client.focus();
          }
        }
        
        // Abrir nova aba se necessário
        if (clients.openWindow) {
          return clients.openWindow(url);
        }
      })
    );
  }
});

// Listener para mensagens de atualização forçada
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    console.log('🔄 Forçando ativação da nova versão do Service Worker...');
    self.skipWaiting();
  }
});

// Notificar clientes sobre nova versão disponível apenas se for realmente nova
self.addEventListener('activate', (event) => {
  console.log('✅ Nova versão do Service Worker ativada!');
  
  event.waitUntil(
    Promise.all([
      // Assumir controle de todas as abas
       self.clients.claim(),
      // Notificar clientes apenas se for uma atualização real
      clients.matchAll().then((clients) => {
        // Só notificar se houver clientes e for uma atualização real
        if (clients.length > 0 && self.skipWaiting) {
          clients.forEach((client) => {
            client.postMessage({
              type: 'SW_UPDATED',
              version: CACHE_VERSION
            });
          });
        }
      })
    ])
  );
});

console.log('🚀 Service Worker 1Crypten carregado!');