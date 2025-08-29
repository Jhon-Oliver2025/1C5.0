# 🚀 Variáveis de Produção para Coolify - 1Crypten

## 📋 **CONFIGURAÇÃO COMPLETA PARA COOLIFY**

### **🔥 COPIE E COLE NO COOLIFY:**

```env
# ===== SUPABASE (OBRIGATÓRIO) =====
SUPABASE_URL=https://fvwdcsqucajnqupsprmo.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZ2d2Rjc3F1Y2FqbnF1cHNwcm1vIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTMyMTAzNzUsImV4cCI6MjA2ODc4NjM3NX0.h7cNPa_WtSn7s1DDPAdBhLqUZYQLJbn3wDoAIMEFYyQ
SUPABASE_DATABASE_URL=postgresql://postgres:Fh@xj_wgU-D2Vde@db.fvwdcsqucajnqupsprmo.supabase.co:5432/postgres

# ===== SEGURANÇA =====
SECRET_KEY=gZ4vNpWq8sB2kF6a10prasempre
JWT_SECRET=X9eR3cM7zL10prasempre1kP5f

# ===== BINANCE API (TRADING) =====
BINANCE_API_KEY=aUApdM0jyXeyI1HPxHymi9hSD6QZ3TXFORTknlyc1jADrkCJ7SNSayoZ6oiPCYEj
BINANCE_SECRET_KEY=YGt2MXqsIhgjk6EsCwRCUjB3LpZ0L8xGAt9w4JYK6wyX2LveLHBFvRjoyBfIVcZM

# ===== TELEGRAM BOT (NOTIFICAÇÕES) =====
TELEGRAM_BOT_TOKEN=7690455274:AAHB64l8csWoE5UpV1Pnn9c8chJzd5sZTXQ
TELEGRAM_CHAT_ID=1249100206

# ===== SENDPULSE (E-MAIL MARKETING) =====
SENDPULSE_CLIENT_ID=7b28b045d31c3d6d51591d7f56a26c99
SENDPULSE_CLIENT_SECRET=26393054ce0cd24fc16a73382a3d5eef
SENDPULSE_SENDER_EMAIL=crypten@portaldigital10.com
SENDPULSE_API_URL=https://api.sendpulse.com

# ===== MERCADO PAGO (PAGAMENTOS - TESTE) =====
MERCADO_PAGO_ACCESS_TOKEN=TEST-6555567678065222-081500-d19fea4c0e7513745e4aba7f14244ba4-150384131
MERCADO_PAGO_PUBLIC_KEY=TEST-49cb27ee-fe8c-4aa0-b055-092bf4616484

# ===== URLS DE PRODUÇÃO =====
FRONTEND_URL=https://1crypten.space
BACKEND_URL=https://api.1crypten.space
API_BASE_URL=https://api.1crypten.space
CORS_ORIGINS=https://1crypten.space,https://www.1crypten.space

# ===== FLASK =====
FLASK_ENV=production
FLASK_PORT=5000
```

---

## 🎯 **INFORMAÇÕES DO PROJETO**

### **📊 Supabase:**
- **Projeto ID**: `fvwdcsqucajnqupsprmo`
- **URL**: `https://fvwdcsqucajnqupsprmo.supabase.co`
- **Status**: ✅ Configurado e funcionando

### **📈 Binance:**
- **API Key**: Configurada para trading
- **Permissões**: Spot & Margin Trading
- **Status**: ✅ Ativa

### **🤖 Telegram:**
- **Bot Token**: Configurado
- **Chat ID**: `1249100206`
- **Status**: ✅ Notificações ativas

### **💳 Mercado Pago:**
- **Modo**: TESTE (Sandbox)
- **Link de Teste**: `https://mpago.la/1uTNfUw`
- **Status**: ⚠️ Em teste

### **🌐 URLs:**
- **Frontend**: `https://1crypten.space`
- **Backend**: `https://api.1crypten.space`
- **Status**: ✅ Configuradas

---

## 📋 **PASSO A PASSO NO COOLIFY**

### **1️⃣ Acesse o Coolify Dashboard**
- Faça login no seu Coolify
- Vá para o projeto 1Crypten

### **2️⃣ Configure Environment Variables**
- Clique em "Environment Variables"
- Adicione cada variável uma por uma
- OU copie e cole o bloco completo acima

### **3️⃣ Salve e Redeploy**
- Clique em "Save"
- Aguarde o redeploy automático
- Verifique os logs

### **4️⃣ Teste o Sistema**
```bash
# Health Check
curl https://1crypten.space/api/health

# Status da API
curl https://1crypten.space/api/status

# Frontend
https://1crypten.space/
```

---

## ✅ **CHECKLIST DE VERIFICAÇÃO**

### **🔍 Após Deploy:**
- [ ] **Supabase**: Conexão estabelecida
- [ ] **Frontend**: Carregando sem erros
- [ ] **Backend**: APIs respondendo
- [ ] **Binance**: Dados de mercado funcionando
- [ ] **Telegram**: Notificações sendo enviadas
- [ ] **SendPulse**: E-mails funcionando
- [ ] **Mercado Pago**: Checkout em teste

### **🚨 Se algo não funcionar:**
1. **Verifique os logs** no Coolify
2. **Confirme as variáveis** estão corretas
3. **Teste APIs individualmente**
4. **Verifique permissões** das chaves

---

## 🔄 **PRÓXIMOS PASSOS**

### **🎯 Mercado Pago - Produção:**
Quando estiver pronto para produção:
```env
# Substitua por:
MERCADO_PAGO_ACCESS_TOKEN=APP_USR-seu_access_token_de_producao
MERCADO_PAGO_PUBLIC_KEY=APP_USR-sua_public_key_de_producao
```

### **📊 Monitoramento:**
- Configure alertas no Coolify
- Monitore logs de erro
- Acompanhe métricas de performance

### **🔒 Segurança:**
- Rotacione chaves periodicamente
- Monitore acessos suspeitos
- Mantenha backups atualizados

---

**🎉 Sistema 1Crypten configurado e pronto para produção!**

**📅 Última atualização:** 29/08/2025  
**🔄 Status:** Todas as variáveis configuradas  
**🎯 Próximo:** Deploy no Coolify