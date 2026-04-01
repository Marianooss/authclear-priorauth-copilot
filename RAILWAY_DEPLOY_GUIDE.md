# 🚀 Guía de Deploy a Railway - AuthClear

**Tiempo Estimado:** 30 minutos  
**Prerequisitos:** Cuenta de Railway (gratis con GitHub)

---

## 📋 PASO 1: Inicializar Git (5 min)

Railway necesita Git para hacer deploy. Si ya tienes git configurado, salta al Paso 2.

```bash
# En la carpeta AuthClear
cd c:\Users\user\Desktop\AuthClear

# Inicializar git
git init

# Crear .gitignore
echo ".env
__pycache__/
*.pyc
.pytest_cache/
.coverage
htmlcov/
dist/
build/
*.egg-info/
.vscode/
.idea/
node_modules/" > .gitignore

# Commit inicial
git add .
git commit -m "feat: AuthClear system - 100% functional (agents.md compliant)"
```

**✅ Verificación:**
```bash
git log --oneline
# Deberías ver: "feat: AuthClear system - 100% functional..."
```

---

## 📋 PASO 2: Crear Cuenta en Railway (3 min)

1. **Ir a:** https://railway.app/
2. **Click:** "Start a New Project"
3. **Login con GitHub** (recomendado - deploy automático)
4. **Verificar email** si es primera vez

**✅ Verificación:**  
Deberías estar en el dashboard de Railway con botón "New Project"

---

## 📋 PASO 3: Crear Proyecto en GitHub (Opcional pero Recomendado) (5 min)

Railway puede hacer deploy directo desde tu repo de GitHub.

### **Opción A: GitHub (Recomendado)**

1. **Ir a:** https://github.com/new
2. **Repository name:** `authclear-priorauth-copilot`
3. **Description:** "AI-powered prior authorization copilot for physicians. Dual submission: MCP Server + A2A Agent."
4. **Public** (requerido para hackathon submission)
5. **NO crear README/gitignore** (ya los tienes)
6. **Click:** "Create repository"

7. **Conectar tu repo local:**
```bash
# Copiar el URL que te da GitHub (algo como):
# https://github.com/TU_USUARIO/authclear-priorauth-copilot.git

git remote add origin https://github.com/TU_USUARIO/authclear-priorauth-copilot.git
git branch -M main
git push -u origin main
```

### **Opción B: Sin GitHub (Deploy directo - más lento)**

Salta este paso y usa Railway CLI en Paso 4.

**✅ Verificación:**  
Tu código debería estar visible en `github.com/TU_USUARIO/authclear-priorauth-copilot`

---

## 📋 PASO 4: Deploy MCP Server (10 min)

### **4.1 - Crear Service 1 en Railway**

1. **En Railway Dashboard:** Click "New Project"
2. **Seleccionar:** "Deploy from GitHub repo"
3. **Autorizar Railway** si es primera vez
4. **Seleccionar repo:** `authclear-priorauth-copilot`
5. **Click:** "Deploy Now"

### **4.2 - Configurar MCP Service**

1. **Renombrar service:**
   - Click en el service que se creó
   - Click en nombre (arriba)
   - Cambiar a: `authclear-mcp`

2. **Configurar Dockerfile:**
   - Click "Settings" (ícono de tuerca)
   - Buscar "Build" section
   - En "Dockerfile Path" poner: `Dockerfile.mcp`
   - Click "Save"

3. **Configurar Variables de Entorno:**
   - Click "Variables" (ícono de lista)
   - Click "New Variable"
   - Agregar estas variables:

   ```
   PORT=8001
   ENVIRONMENT=production
   LOG_LEVEL=INFO
   ```

   **IMPORTANTE:** No necesitas ANTHROPIC_API_KEY en MCP Server (solo hace requests HTTP públicos)

4. **Trigger Deploy:**
   - Click "Deployments" (arriba)
   - Click "Deploy" (botón arriba derecha)
   - Espera 3-5 minutos (puedes ver logs en tiempo real)

### **4.3 - Obtener URL del MCP Server**

1. **Click "Settings"**
2. **Buscar "Networking" section**
3. **Click "Generate Domain"**
4. **Copiar la URL** (algo como): `authclear-mcp.railway.app`

**✅ Verificación:**
```bash
# En tu terminal local
curl https://authclear-mcp.railway.app/health

# Deberías ver:
{"status":"ok","service":"authclear-mcp-server"}
```

**Si falla:** Ver logs en Railway → Deployments → View Logs

---

## 📋 PASO 5: Deploy A2A Agent (10 min)

### **5.1 - Crear Service 2 en Railway**

1. **En el MISMO proyecto de Railway:**
   - Click "New" (botón + arriba derecha)
   - Click "GitHub Repo"
   - Seleccionar el mismo repo: `authclear-priorauth-copilot`

2. **Renombrar service:**
   - Click en el service nuevo
   - Cambiar nombre a: `authclear-agent`

### **5.2 - Configurar A2A Service**

1. **Configurar Dockerfile:**
   - Click "Settings"
   - En "Dockerfile Path" poner: `Dockerfile.agent`
   - Click "Save"

2. **Configurar Variables de Entorno:**
   - Click "Variables"
   - Agregar estas variables:

   ```
   PORT=8000
   ENVIRONMENT=production
   LOG_LEVEL=INFO
   CLAUDE_PROVIDER=bedrock
   AWS_REGION=us-east-1
   AWS_BEDROCK_MODEL=anthropic.claude-sonnet-4-20250514-v1:0
   MCP_SERVER_URL=https://authclear-mcp.railway.app
   ```

   **CRÍTICO - Agregar credenciales AWS Bedrock:**
   ```
   AWS_ACCESS_KEY_ID=AKIAXXXXXXXXXXXX
   AWS_SECRET_ACCESS_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

   **NOTA:** Necesitas tus credenciales de AWS Bedrock. Si usas Anthropic API en lugar de Bedrock:
   ```
   CLAUDE_PROVIDER=anthropic
   ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

3. **Trigger Deploy:**
   - Click "Deployments"
   - Click "Deploy"
   - Espera 3-5 minutos

### **5.3 - Obtener URL del A2A Agent**

1. **Click "Settings"**
2. **Buscar "Networking" section**
3. **Click "Generate Domain"**
4. **Copiar la URL** (algo como): `authclear-agent.railway.app`

**✅ Verificación:**
```bash
# Test health check
curl https://authclear-agent.railway.app/health

# Deberías ver:
{"status":"ok","service":"authclear-agent","task_store":{"total_tasks":0}}

# Test agent card (A2A protocol)
curl https://authclear-agent.railway.app/.well-known/agent.json

# Deberías ver JSON con:
{"name":"AuthClear Prior Auth Copilot","version":"2.0.0",...}
```

---

## 📋 PASO 6: Test End-to-End (2 min)

Ahora vamos a hacer un test completo para confirmar que todo funciona en producción.

```bash
# Test completo (cambiar URL por tu URL real)
curl -X POST https://authclear-agent.railway.app/tasks/send \
  -H "Content-Type: application/json" \
  -d '{
    "task": {
      "input": {
        "fhir_bundle": {
          "resourceType": "Bundle",
          "type": "collection",
          "entry": [
            {
              "resource": {
                "resourceType": "Patient",
                "name": [{"given": ["Test"], "family": "Patient"}],
                "birthDate": "1970-01-01"
              }
            }
          ]
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

**✅ Esperado:**
```json
{
  "task": {
    "id": "task-xxxxx",
    "state": "completed",
    "result": {
      "confidence_score": 0.XX,
      "confidence_breakdown": [...],
      ...
    }
  }
}
```

---

## 📋 PASO 7: URLs Finales (1 min)

**Guarda estas URLs - las necesitarás para Prompt Opinion:**

```
MCP Server:
https://authclear-mcp.railway.app

A2A Agent:
https://authclear-agent.railway.app

Agent Card (A2A Protocol):
https://authclear-agent.railway.app/.well-known/agent.json

Health Checks:
https://authclear-mcp.railway.app/health
https://authclear-agent.railway.app/health
```

---

## 🐛 TROUBLESHOOTING

### **Problema: Build falla con "poetry not found"**

**Solución:** Dockerfile ya tiene `RUN pip install poetry==1.8.4`. Si falla:
- Ver logs completos en Railway
- Verificar que `pyproject.toml` y `poetry.lock` existen en el repo

---

### **Problema: A2A Agent devuelve 500 Internal Server Error**

**Causa probable:** Falta `ANTHROPIC_API_KEY` o `AWS_ACCESS_KEY_ID`

**Solución:**
1. Click en `authclear-agent` service
2. Click "Variables"
3. Verificar que tienes:
   - `ANTHROPIC_API_KEY` (si usas Anthropic)
   - O `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY` (si usas Bedrock)

---

### **Problema: MCP Server health check falla**

**Causa probable:** Puerto incorrecto o Dockerfile path incorrecto

**Solución:**
1. Click en `authclear-mcp` service
2. Click "Settings"
3. Verificar:
   - "Dockerfile Path" = `Dockerfile.mcp`
   - Variables tienen `PORT=8001`
4. Redeploy

---

### **Problema: A2A Agent no puede llamar al MCP Server**

**Síntoma:** Logs dicen "Connection refused" o "Connection timeout"

**Solución:**
1. Verificar que `MCP_SERVER_URL` en A2A Agent tenga la URL correcta:
   ```
   MCP_SERVER_URL=https://authclear-mcp.railway.app
   ```
   **SIN trailing slash**

2. Test manualmente:
   ```bash
   curl https://authclear-mcp.railway.app/health
   ```

---

## 💰 COSTOS DE RAILWAY

**Plan Gratuito (Trial):**
- $5 USD de crédito gratis
- Suficiente para ~500 requests
- Services se suspenden después de inactividad (se despiertan automáticamente)

**Para Hackathon:**
- Deploy durante hackathon = gratis (créditos trial)
- Después del judging, puedes pausar services si no quieres pagar

**Costo Real (si decides mantenerlo):**
- ~$5-10/mes por ambos services
- Solo pagas por uptime + requests

---

## ✅ CHECKLIST FINAL

Antes de continuar a Prompt Opinion, verifica:

- [ ] MCP Server health check responde OK
- [ ] A2A Agent health check responde OK
- [ ] Agent card endpoint devuelve JSON válido
- [ ] Test end-to-end completa exitosamente
- [ ] URLs copiadas y guardadas
- [ ] Repo de GitHub es público (si usas GitHub)

**Si todo ✅ → Continuar a PASO 8: Publicar en Prompt Opinion**

---

## 📚 SIGUIENTES PASOS

Una vez que Railway esté funcionando:

1. **Publicar en Prompt Opinion Marketplace** (20 min)
2. **Grabar Video Demo** (1-2 horas)
3. **Submit a Devpost** (10 min)

**Tiempo total restante:** ~2-3 horas hasta submission completa

---

## 🆘 SI TIENES PROBLEMAS

**Railway Support:**
- Discord: https://discord.gg/railway
- Docs: https://docs.railway.app/

**En el proyecto:**
- Ver logs detallados en Railway → Service → Deployments → View Logs
- Si nada funciona, avisame y debugging juntos
