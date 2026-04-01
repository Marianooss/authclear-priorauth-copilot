# 🔐 Variables de Entorno para Railway

**IMPORTANTE:** Copia estas variables exactamente como están en Railway Dashboard

---

## 📦 SERVICE 1: authclear-mcp

```
PORT=8001
ENVIRONMENT=production
LOG_LEVEL=INFO
```

**NOTA:** MCP Server NO necesita API keys - solo hace requests HTTP públicos

---

## 📦 SERVICE 2: authclear-agent

### **Variables Básicas:**
```
PORT=8000
ENVIRONMENT=production
LOG_LEVEL=INFO
```

### **MCP Server Connection:**
```
MCP_SERVER_URL=https://authclear-mcp.railway.app
```
**⚠️ IMPORTANTE:** Reemplazar con tu URL real del MCP Server después de deploy

---

### **Claude Provider - OPCIÓN A: Anthropic API**

Si usas Anthropic API directamente:

```
CLAUDE_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-api03-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

**Dónde conseguir tu API key:**
1. Ir a: https://console.anthropic.com/
2. Login
3. Click "API Keys" (menú izquierdo)
4. Click "Create Key"
5. Copiar key (empieza con `sk-ant-`)

---

### **Claude Provider - OPCIÓN B: AWS Bedrock**

Si usas AWS Bedrock (recomendado para producción):

```
CLAUDE_PROVIDER=bedrock
AWS_REGION=us-east-1
AWS_BEDROCK_MODEL=anthropic.claude-sonnet-4-20250514-v1:0
AWS_ACCESS_KEY_ID=AKIAXXXXXXXXXXXXXXXX
AWS_SECRET_ACCESS_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Dónde conseguir credenciales AWS:**
1. Ir a: https://console.aws.amazon.com/iam/
2. Click "Users" → Tu usuario
3. Click "Security credentials"
4. Click "Create access key"
5. Seleccionar "Application running outside AWS"
6. Copiar Access Key ID y Secret Access Key

**IMPORTANTE:** Necesitas tener acceso a Bedrock:
- Ir a: https://console.aws.amazon.com/bedrock/
- Click "Model access" (menú izquierdo)
- Request access to "Anthropic Claude Sonnet 4"

---

## 📋 TEMPLATE PARA COPIAR/PEGAR

### **authclear-mcp (copiar esto):**
```
PORT=8001
ENVIRONMENT=production
LOG_LEVEL=INFO
```

---

### **authclear-agent (copiar esto y llenar tus keys):**

**Si usas Anthropic API:**
```
PORT=8000
ENVIRONMENT=production
LOG_LEVEL=INFO
MCP_SERVER_URL=https://authclear-mcp.railway.app
CLAUDE_PROVIDER=anthropic
ANTHROPIC_API_KEY=TU_KEY_AQUI
```

**Si usas AWS Bedrock:**
```
PORT=8000
ENVIRONMENT=production
LOG_LEVEL=INFO
MCP_SERVER_URL=https://authclear-mcp.railway.app
CLAUDE_PROVIDER=bedrock
AWS_REGION=us-east-1
AWS_BEDROCK_MODEL=anthropic.claude-sonnet-4-20250514-v1:0
AWS_ACCESS_KEY_ID=TU_ACCESS_KEY_AQUI
AWS_SECRET_ACCESS_KEY=TU_SECRET_KEY_AQUI
```

---

## 🔒 SEGURIDAD

**NUNCA commitear a Git:**
- API Keys
- AWS Credentials
- Secrets de cualquier tipo

**Railway maneja esto automáticamente:**
- Las variables que agregues en Railway Dashboard NO van a Git
- Se inyectan como environment variables en runtime
- Son encriptadas en Railway

---

## ✅ VERIFICACIÓN

Después de agregar variables:

```bash
# Test que A2A Agent puede llamar a Claude
curl -X POST https://authclear-agent.railway.app/tasks/send \
  -H "Content-Type: application/json" \
  -d '{"task":{"input":{"fhir_bundle":{"resourceType":"Bundle","type":"collection","entry":[]},"requested_item":{"type":"medication","name":"Test"},"payer":"generic"}}}'

# Si ves response JSON con task_id → ✅ Funciona
# Si ves 500 error → Revisar API keys
```

---

## 📊 CUÁNTO CUESTA

**Anthropic API:**
- Claude Sonnet 4: ~$3 / 1M input tokens, ~$15 / 1M output tokens
- 1 prior auth request = ~5K tokens = $0.03 USD
- 1000 requests = $30 USD

**AWS Bedrock:**
- Similar pricing pero con on-demand capacity
- Mejor para producción (más stable)

**Railway Hosting:**
- $5 USD gratis trial (suficiente para hackathon)
- Después: ~$5-10/mes por servicio

---

## 🆘 SI NO TIENES API KEYS

**No tienes cuenta Anthropic/AWS y quieres hacer deploy rápido:**

1. **Crear cuenta Anthropic** (5 min):
   - https://console.anthropic.com/
   - $5 USD crédito gratis al crear cuenta
   - Suficiente para hackathon judging

2. **O usar modo simulado (NO RECOMENDADO para submission):**
   - Agrega variable: `SIMULATED_MODE=true`
   - Agent retornará respuestas simuladas (no real Claude)
   - Solo para testing, jueces se van a dar cuenta

---

**RECOMENDACIÓN:** Usa Anthropic API (más fácil setup) para hackathon. Cambiar a Bedrock después si quieres productizar.
