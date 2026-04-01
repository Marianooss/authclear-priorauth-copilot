# ✅ Checklist de Deploy a Railway - 30 Minutos

**Objetivo:** Deploy de AuthClear a producción en Railway  
**Resultado:** URLs públicas funcionando para Prompt Opinion submission

---

## 🚀 PREPARACIÓN (5 min)

### **1. Git Setup**
```bash
cd c:\Users\user\Desktop\AuthClear

# Inicializar git
git init

# Agregar todos los archivos
git add .

# Primer commit
git commit -m "feat: AuthClear system - 100% functional (agents.md compliant)"
```

**✅ Verificar:** `git log --oneline` muestra tu commit

---

### **2. Crear Repo en GitHub**

1. Ir a: https://github.com/new
2. Repository name: `authclear-priorauth-copilot`
3. **Public** ← IMPORTANTE
4. NO crear README ni .gitignore (ya los tienes)
5. Click "Create repository"

```bash
# Conectar repo (usar TU URL)
git remote add origin https://github.com/TU_USUARIO/authclear-priorauth-copilot.git
git branch -M main
git push -u origin main
```

**✅ Verificar:** Tu código visible en GitHub

---

## 🚂 RAILWAY SETUP (3 min)

### **3. Crear Cuenta Railway**

1. Ir a: https://railway.app/
2. "Start a New Project"
3. **Login con GitHub**
4. Verificar email si es nueva cuenta

**✅ Verificar:** Estás en Railway dashboard

---

## 🔧 DEPLOY SERVICE 1: MCP Server (10 min)

### **4. Deploy MCP Server**

1. **Railway Dashboard** → "New Project"
2. "Deploy from GitHub repo"
3. Autorizar Railway (primera vez)
4. Seleccionar: `authclear-priorauth-copilot`
5. Click "Deploy Now"

---

### **5. Configurar MCP Service**

**Renombrar:**
- Click en el service → Click nombre arriba → Cambiar a: `authclear-mcp`

**Configurar Dockerfile:**
- Settings → Build section
- Dockerfile Path: `Dockerfile.mcp`
- Save

**Variables de Entorno:**
- Click "Variables"
- New Variable (agregar estas 3):
  ```
  PORT=8001
  ENVIRONMENT=production
  LOG_LEVEL=INFO
  ```

**Deploy:**
- Deployments → Deploy
- Esperar 3-5 min (ver logs)

---

### **6. Generar URL del MCP**

- Settings → Networking
- "Generate Domain"
- **Copiar URL:** `authclear-mcp.railway.app`

**✅ Test:**
```bash
curl https://authclear-mcp.railway.app/health
# Esperado: {"status":"ok","service":"authclear-mcp-server"}
```

---

## 🤖 DEPLOY SERVICE 2: A2A Agent (10 min)

### **7. Deploy A2A Agent**

**En el MISMO proyecto:**
- Click "New" (+)
- "GitHub Repo"
- Mismo repo: `authclear-priorauth-copilot`

**Renombrar:**
- Click service → Cambiar nombre a: `authclear-agent`

---

### **8. Configurar A2A Service**

**Configurar Dockerfile:**
- Settings → Build
- Dockerfile Path: `Dockerfile.agent`
- Save

**Variables de Entorno:**
- Click "Variables"
- Copiar/pegar esto (llenar TU API KEY):

**Si usas Anthropic API:**
```
PORT=8000
ENVIRONMENT=production
LOG_LEVEL=INFO
MCP_SERVER_URL=https://authclear-mcp.railway.app
CLAUDE_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-TU_KEY_AQUI
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
AWS_ACCESS_KEY_ID=TU_KEY_AQUI
AWS_SECRET_ACCESS_KEY=TU_SECRET_AQUI
```

**Deploy:**
- Deployments → Deploy
- Esperar 3-5 min

---

### **9. Generar URL del Agent**

- Settings → Networking
- "Generate Domain"
- **Copiar URL:** `authclear-agent.railway.app`

**✅ Test:**
```bash
# Health check
curl https://authclear-agent.railway.app/health

# Agent card
curl https://authclear-agent.railway.app/.well-known/agent.json
```

---

## 🎯 TEST FINAL (2 min)

### **10. Test End-to-End**

```bash
curl -X POST https://authclear-agent.railway.app/tasks/send \
  -H "Content-Type: application/json" \
  -d '{
    "task": {
      "input": {
        "fhir_bundle": {
          "resourceType": "Bundle",
          "type": "collection",
          "entry": [{
            "resource": {
              "resourceType": "Patient",
              "name": [{"given": ["Test"], "family": "Patient"}],
              "birthDate": "1970-01-01"
            }
          }]
        },
        "requested_item": {
          "type": "medication",
          "name": "Ozempic",
          "code": "J0173"
        },
        "payer": "generic"
      }
    }
  }'
```

**✅ Esperado:** JSON con `"task_id"` y `"state":"completed"`

---

## 📋 URLs FINALES

**Guarda estas URLs para Prompt Opinion:**

```
MCP Server:
https://authclear-mcp.railway.app

A2A Agent:
https://authclear-agent.railway.app

Agent Card:
https://authclear-agent.railway.app/.well-known/agent.json
```

---

## ✅ CHECKLIST FINAL

Antes de continuar a Prompt Opinion:

- [ ] Git inicializado y pusheado a GitHub
- [ ] Cuenta Railway creada
- [ ] MCP Server deployed (health check OK)
- [ ] A2A Agent deployed (health check OK)
- [ ] Agent card responde JSON válido
- [ ] Test end-to-end completa
- [ ] URLs copiadas

**SI TODO ✅ → Listo para Prompt Opinion (siguiente paso)**

---

## 🐛 PROBLEMAS COMUNES

**Build falla:**
- Ver logs completos en Railway
- Verificar Dockerfile Path correcto

**500 Error en Agent:**
- Revisar API key en Variables
- Ver logs del service

**Connection refused entre services:**
- Verificar `MCP_SERVER_URL` en Agent
- Debe ser: `https://authclear-mcp.railway.app` (sin trailing slash)

---

## 💰 COSTOS

- **Trial de Railway:** $5 USD gratis (suficiente para hackathon)
- **Anthropic API:** $5 USD crédito gratis al crear cuenta
- **Total costo real para hackathon:** $0 USD

---

## ⏭️ SIGUIENTE PASO

**Una vez Railway esté funcionando:**

➡️ **Publicar en Prompt Opinion Marketplace** (20 min)

Ver archivo: `PROMPT_OPINION_GUIDE.md` (próximo a crear)

---

**Tiempo total de este paso:** ~30 minutos  
**Progreso:** 1/3 bloqueantes completados ✅
