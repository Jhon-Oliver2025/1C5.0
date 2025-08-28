import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig(({ mode }) => {
  // Forçar desenvolvimento local quando rodando npm run dev
  const isProduction = mode === 'production' && process.env.NODE_ENV === 'production';
  
  // Configurar target da API baseado no ambiente
  const apiTarget = isProduction 
    ? 'https://1crypten.space'  // HTTPS em produção
    : 'http://localhost:5000';  // HTTP em desenvolvimento local
  
  console.log(`🔧 Vite Mode: ${mode}`);
  console.log(`🎯 API Target: ${apiTarget}`);
  console.log(`🔍 Is Production: ${isProduction}`);

  return {
    plugins: [
      react(),
      VitePWA({
        registerType: 'autoUpdate',
        workbox: {
          globPatterns: ['**/*.{js,css,html,ico,png,svg,woff2}'],
          maximumFileSizeToCacheInBytes: 10 * 1024 * 1024, // 10MB
          runtimeCaching: [
            {
              urlPattern: /^https:\/\/api\./,
              handler: 'NetworkFirst',
              options: {
                cacheName: 'api-cache',
                expiration: {
                  maxEntries: 100,
                  maxAgeSeconds: 60 * 60 * 24 // 24 horas
                }
              }
            },
            {
              urlPattern: /\.(?:png|jpg|jpeg|svg|gif)$/,
              handler: 'CacheFirst',
              options: {
                cacheName: 'images-cache',
                expiration: {
                  maxEntries: 50,
                  maxAgeSeconds: 60 * 60 * 24 * 30 // 30 dias
                }
              }
            }
          ]
        },
        manifest: {
          name: '1Crypten - Trading Signals',
          short_name: '1Crypten',
          description: 'Plataforma avançada de sinais de trading para criptomoedas com análise técnica em tempo real',
          theme_color: '#646cff',
          background_color: '#000000',
          display: 'standalone',
          orientation: 'portrait-primary',
          scope: '/',
          start_url: '/app',
          icons: [
            {
              src: '/icons/icon-192x192.png',
              sizes: '192x192',
              type: 'image/png',
              purpose: 'any maskable'
            },
            {
              src: '/icons/icon-512x512.png',
              sizes: '512x512',
              type: 'image/png',
              purpose: 'any maskable'
            }
          ]
        }
      })
    ],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src')
      }
    },
    server: {
      port: 3000,
      host: true,

      proxy: {
        '/api': {
          target: apiTarget,
          changeOrigin: true,
          secure: isProduction, // true em produção para HTTPS
          ws: true,
          configure: (proxy, options) => {
            proxy.on('error', (err, req, res) => {
              console.log('proxy error', err);
            });
            proxy.on('proxyReq', (proxyReq, req, res) => {
              console.log('Enviando requisição para o alvo:', req.method, req.url);
            });
            proxy.on('proxyRes', (proxyRes, req, res) => {
              console.log('Recebida resposta do alvo:', proxyRes.statusCode, req.url);
            });
          }
        }
      }
    },
    build: {
      target: 'es2020',
      minify: 'esbuild', // Usar sempre esbuild para evitar problemas com terser no Docker
      sourcemap: false,
      chunkSizeWarningLimit: 1000,
      assetsInlineLimit: 0, // Não inlinear assets para evitar problemas com vídeos
      rollupOptions: {
        output: {
          manualChunks: {
            vendor: ['react', 'react-dom'],
            styled: ['styled-components'],
            router: ['react-router-dom']
          },
          assetFileNames: (assetInfo) => {
            // Manter nome original para vídeos na pasta public
            if (assetInfo.name && assetInfo.name.endsWith('.mp4')) {
              return '[name][extname]';
            }
            return 'assets/[name]-[hash][extname]';
          }
        }
      }
    }
  };
})