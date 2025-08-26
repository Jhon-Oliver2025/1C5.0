// Configuração para desenvolvimento local
window.APP_CONFIG = {
  API_URL: 'http://localhost:5000',
  DEFAULT_CREDENTIALS: {
    username: 'admin',
    password: 'admin123'
  },
  ENVIRONMENT: 'development'
};

console.log('🔧 Configuração carregada:', window.APP_CONFIG);