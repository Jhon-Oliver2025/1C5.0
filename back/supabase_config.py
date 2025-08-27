import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class SupabaseConfig:
    """
    Configuração para conexão com Supabase
    """
    
    def __init__(self):
        # URL do projeto Supabase
        self.SUPABASE_URL = os.getenv('SUPABASE_URL')
        
        # Chave anônima do Supabase (para operações públicas)
        self.SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')
        
        # Chave de serviço do Supabase (para operações administrativas)
        self.SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        # URL de conexão direta com PostgreSQL do Supabase
        self.DATABASE_URL = os.getenv('SUPABASE_DATABASE_URL')
        
        # Configurações opcionais - validação manual
        self.is_configured = self._validate_config()
    
    def _validate_config(self):
        """
        Valida se todas as configurações necessárias estão presentes
        """
        print("\n🔍 === DIAGNÓSTICO SUPABASE DETALHADO ===")
        print(f"📍 Verificando variáveis de ambiente...")
        
        # Verificar cada variável individualmente
        print(f"\n📋 SUPABASE_URL:")
        if self.SUPABASE_URL:
            print(f"   ✅ Definida: {self.SUPABASE_URL}")
        else:
            print(f"   ❌ NÃO DEFINIDA ou VAZIA")
            
        print(f"\n📋 SUPABASE_ANON_KEY:")
        if self.SUPABASE_ANON_KEY:
            print(f"   ✅ Definida: {self.SUPABASE_ANON_KEY[:20]}...{self.SUPABASE_ANON_KEY[-10:]}")
            print(f"   📏 Tamanho: {len(self.SUPABASE_ANON_KEY)} caracteres")
        else:
            print(f"   ❌ NÃO DEFINIDA ou VAZIA")
            
        print(f"\n📋 SUPABASE_SERVICE_ROLE_KEY:")
        if self.SUPABASE_SERVICE_ROLE_KEY:
            print(f"   ✅ Definida: {self.SUPABASE_SERVICE_ROLE_KEY[:20]}...{self.SUPABASE_SERVICE_ROLE_KEY[-10:]}")
            print(f"   📏 Tamanho: {len(self.SUPABASE_SERVICE_ROLE_KEY)} caracteres")
        else:
            print(f"   ⚠️ NÃO DEFINIDA (opcional para algumas operações)")
            
        print(f"\n📋 SUPABASE_DATABASE_URL:")
        if self.DATABASE_URL:
            # Mascarar senha na URL
            masked_url = self.DATABASE_URL
            if '@' in masked_url and ':' in masked_url:
                parts = masked_url.split('@')
                if len(parts) == 2:
                    user_pass = parts[0].split('//')[-1]
                    if ':' in user_pass:
                        user, password = user_pass.split(':', 1)
                        masked_url = masked_url.replace(f':{password}@', ':***@')
            print(f"   ✅ Definida: {masked_url}")
        else:
            print(f"   ❌ NÃO DEFINIDA ou VAZIA")
        
        required_vars = {
            'SUPABASE_URL': self.SUPABASE_URL,
            'SUPABASE_ANON_KEY': self.SUPABASE_ANON_KEY,
            'DATABASE_URL': self.DATABASE_URL
        }
        
        missing_vars = [var for var, value in required_vars.items() if not value]
        
        print(f"\n📊 RESULTADO DA VALIDAÇÃO:")
        if missing_vars:
            print(f"   ❌ Variáveis faltando: {', '.join(missing_vars)}")
            print(f"   🔧 Executando em modo degradado")
            print(f"   ⚠️ O Supabase Auth NÃO funcionará!")
            return False
        
        print(f"   ✅ Todas as variáveis obrigatórias estão configuradas")
        print(f"   ✅ Supabase Auth inicializado com sucesso")
        print(f"   🚀 Sistema pronto para autenticação")
        print("🔍 === FIM DO DIAGNÓSTICO SUPABASE ===\n")
        return True
    
    def get_database_url(self):
        """
        Retorna a URL de conexão com o banco de dados
        """
        return self.DATABASE_URL
    
    def get_supabase_credentials(self):
        """
        Retorna as credenciais do Supabase para uso com o SDK
        """
        return {
            'url': self.SUPABASE_URL,
            'anon_key': self.SUPABASE_ANON_KEY,
            'service_role_key': self.SUPABASE_SERVICE_ROLE_KEY
        }

# Instância global da configuração
supabase_config = SupabaseConfig()