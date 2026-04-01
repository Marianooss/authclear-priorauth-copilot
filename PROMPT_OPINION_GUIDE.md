# 📢 Publicar en Prompt Opinion Marketplace - Guía Completa

**Tiempo Estimado:** 20 minutos  
**Prerequisito:** Railway deploy completado (URLs funcionando)

---

## 🎯 ¿QUÉ ES PROMPT OPINION MARKETPLACE?

Marketplace oficial donde se publican:
- **MCP Servers** (herramientas reutilizables)
- **A2A Agents** (agentes completos)

**Tu dual submission:**
1. `authclear-terminology` (MCP Server)
2. `authclear-agent` (A2A Agent)

Los jueces del hackathon van a buscar tu agent aquí para testearlo.

---

## 📋 PASO 1: Crear Cuenta en Prompt Opinion (3 min)

1. **Ir a:** https://promptopinion.com/
2. **Click:** "Sign Up" o "Get Started"
3. **Login con GitHub** (recomendado - auto-importa repos)
4. **Verificar email** si es primera vez

**✅ Verificar:** Estás en dashboard con opción "Submit Agent" o "Submit MCP"

---

## 📋 PASO 2: Preparar Información (5 min)

Antes de submitear, prepara esta información (copia/pega en Notepad):

### **URLs de Railway:**
```
MCP Server URL: https://authclear-mcp.railway.app
A2A Agent URL: https://authclear-agent.railway.app
Agent Card URL: https://authclear-agent.railway.app/.well-known/agent.json
GitHub Repo: https://github.com/TU_USUARIO/authclear-priorauth-copilot
```

### **Descripción Corta (para ambos):**
```
AI-powered prior authorization copilot for physicians. 
Reads FHIR patient data, identifies missing criteria, 
and generates complete auth drafts in 30 seconds.
```

### **Descripción Larga (A2A Agent):**
```
AuthClear eliminates 12 hours/week of prior authorization 
paperwork for physicians. The agent:

✅ Reads patient FHIR bundles automatically
✅ Resolves clinical codes (ICD-10, RxNorm, LOINC)
✅ Identifies documentation gaps before submission
✅ Generates complete auth drafts with confidence scoring
✅ Human-in-the-loop for regulatory compliance

ROI: $42K USD saved per physician per year.

Technical:
- Claude Sonnet 4 reasoning via AWS Bedrock
- ReAct pattern with 5-phase workflow
- Deterministic confidence scoring (4-section rubric)
- A2A v2.0 protocol compliant
```

### **Descripción MCP Server:**
```
FHIR clinical terminology resolution engine.

Tools provided:
- resolve_icd10(code) → SNOMED + description
- lookup_rxnorm(drug_name) → RxNorm ID + drug class
- check_drug_interactions(rxnorm_ids[]) → interactions[]
- get_loinc_code(test_name) → LOINC code + unit
- get_prior_auth_criteria(cpt_code, payer) → criteria{}

Uses public NIH NLM APIs. No auth required.
Perfect for healthcare AI agents needing medical coding.
```

### **Tags (keywords):**
```
healthcare, prior-authorization, FHIR, medical-coding, 
ICD-10, RxNorm, LOINC, clinical-ai, physician-copilot, 
healthcare-automation
```

### **Use Cases:**
```
- Prior authorization automation
- Clinical documentation review
- Medical coding assistance
- Healthcare workflow optimization
- EHR data extraction
```

---

## 📋 PASO 3: Submitear MCP Server (Path A) (5 min)

### **3.1 - Iniciar Submission**

1. **Dashboard de Prompt Opinion**
2. **Click:** "Submit MCP Server" o "New MCP"
3. **Seleccionar:** "Manual Entry" (si no auto-detecta)

### **3.2 - Llenar Form**

**Basic Information:**
- **Name:** `authclear-terminology`
- **Display Name:** "AuthClear FHIR Terminology Engine"
- **Short Description:** (copiar de arriba)
- **Category:** "Healthcare" o "Developer Tools"

**Technical Details:**
- **MCP Server URL:** `https://authclear-mcp.railway.app`
- **Transport:** SSE (Server-Sent Events)
- **Health Check Endpoint:** `/health`
- **Protocol Version:** MCP 1.0

**Tools Provided (listar):**
```
1. resolve_icd10
   - Input: {"code": "E11.9"}
   - Output: ICD-10 details + SNOMED mapping

2. lookup_rxnorm
   - Input: {"drug_name": "Ozempic"}
   - Output: RxNorm ID + drug class

3. check_drug_interactions
   - Input: {"rxnorm_ids": ["123", "456"]}
   - Output: Array of interactions with severity

4. get_loinc_code
   - Input: {"test_name": "HbA1c"}
   - Output: LOINC code + unit

5. get_prior_auth_criteria
   - Input: {"cpt_code": "J0173", "payer": "bcbs"}
   - Output: Criteria object with requirements
```

**Repository & Documentation:**
- **GitHub URL:** `https://github.com/TU_USUARIO/authclear-priorauth-copilot`
- **README URL:** `https://github.com/TU_USUARIO/authclear-priorauth-copilot/blob/main/README.md`
- **License:** MIT

**Tags:**
```
healthcare, FHIR, medical-coding, ICD-10, RxNorm, LOINC, terminology
```

### **3.3 - Test MCP Server**

Prompt Opinion va a hacer test automático:
- Health check
- Listar tools disponibles
- Invocar 1-2 tools de prueba

**Si falla:** Ver logs en Railway para debug

### **3.4 - Submit**

- **Click:** "Submit for Review"
- **Copiar URL del listing** (algo como): `promptopinion.com/mcp/authclear-terminology`

**✅ Verificar:** Tu MCP Server aparece en marketplace con status "Under Review" o "Live"

---

## 📋 PASO 4: Submitear A2A Agent (Path B) (7 min)

### **4.1 - Iniciar Submission**

1. **Dashboard de Prompt Opinion**
2. **Click:** "Submit Agent" o "New A2A Agent"
3. **Seleccionar:** "Manual Entry"

### **4.2 - Llenar Form**

**Basic Information:**
- **Name:** `authclear-agent`
- **Display Name:** "AuthClear Prior Auth Copilot"
- **Short Description:** (copiar de arriba)
- **Category:** "Healthcare" o "Business Automation"
- **Icon/Logo:** (opcional - si tienes un logo simple)

**Technical Details:**
- **Agent URL:** `https://authclear-agent.railway.app`
- **Agent Card URL:** `https://authclear-agent.railway.app/.well-known/agent.json`
- **Protocol:** A2A v2.0
- **Capabilities:**
  - ✅ State Transition History
  - ✅ Multi-turn Continuation
  - ❌ Streaming (false en tu agent)
  - ❌ Push Notifications (false)

**Input Schema (copiar/pegar):**
```json
{
  "type": "object",
  "required": ["fhir_bundle", "requested_item", "payer"],
  "properties": {
    "fhir_bundle": {
      "type": "object",
      "description": "FHIR R4 Bundle with patient data"
    },
    "requested_item": {
      "type": "object",
      "properties": {
        "type": {
          "type": "string",
          "enum": ["medication", "procedure", "dme"]
        },
        "name": {
          "type": "string",
          "description": "Drug/procedure name"
        },
        "code": {
          "type": "string",
          "description": "CPT/HCPCS code"
        }
      }
    },
    "payer": {
      "type": "string",
      "enum": ["generic", "bcbs", "medicare", "medicaid", "aetna", "united"],
      "description": "Insurance payer"
    }
  }
}
```

**Output Schema (copiar/pegar):**
```json
{
  "type": "object",
  "properties": {
    "confidence_score": {
      "type": "number",
      "description": "0.0-1.0 approval confidence"
    },
    "confidence_breakdown": {
      "type": "array",
      "description": "4-section scoring rubric"
    },
    "criteria_met": {
      "type": "array",
      "description": "List of satisfied criteria"
    },
    "criteria_gaps": {
      "type": "array",
      "description": "Missing documentation items"
    },
    "clinical_justification": {
      "type": "string",
      "description": "Generated auth narrative"
    },
    "human_review_required": {
      "type": "boolean",
      "description": "Always true - no auto-approval"
    }
  }
}
```

**Dependencies:**
- **MCP Server Used:** `authclear-terminology` (link to tu MCP submission)
- **External APIs:** NIH NLM RxNav, OpenFDA, HAPI FHIR Test Server

**Repository & Documentation:**
- **GitHub URL:** `https://github.com/TU_USUARIO/authclear-priorauth-copilot`
- **Demo Video URL:** (agregar después de grabar)
- **README:** Link to GitHub README

**Tags:**
```
healthcare, prior-authorization, physician-copilot, FHIR, 
medical-ai, healthcare-automation, compliance
```

**Use Cases:**
```
1. Prior authorization request generation
2. Clinical documentation gap analysis
3. Insurance criteria validation
4. Medical justification drafting
5. Healthcare workflow automation
```

### **4.3 - Test A2A Agent**

Prompt Opinion va a hacer test automático:
- Agent card fetch
- Health check
- Sample task invocation

**Test payload que usarán:**
```json
{
  "task": {
    "input": {
      "fhir_bundle": {
        "resourceType": "Bundle",
        "type": "collection",
        "entry": [...]
      },
      "requested_item": {
        "type": "medication",
        "name": "Test Drug",
        "code": "J0000"
      },
      "payer": "generic"
    }
  }
}
```

**Si falla:** Ver logs en Railway

### **4.4 - Submit**

- **Click:** "Submit for Review"
- **Copiar URL del listing:** `promptopinion.com/agents/authclear-agent`

**✅ Verificar:** Tu agent aparece en marketplace

---

## 📋 PASO 5: URLs para Devpost (1 min)

**Guardar estas URLs - las necesitarás para Devpost submission:**

```
Prompt Opinion URLs:

MCP Server:
https://promptopinion.com/mcp/authclear-terminology

A2A Agent:
https://promptopinion.com/agents/authclear-agent

Live Demo (Railway):
https://authclear-agent.railway.app

GitHub:
https://github.com/TU_USUARIO/authclear-priorauth-copilot
```

---

## 🎯 DESPUÉS DE SUBMISSION

### **Status de Review:**

**Immediate (Auto-approved):**
- Si health checks pasan
- Si agent card es válido
- Tu submission aparece "Live" inmediatamente

**Under Review (Manual):**
- Equipo de Prompt Opinion revisa en 24-48h
- Verifican que cumple guidelines
- Aprueban o piden cambios

**Para Hackathon:**
- Submission cuenta aunque esté "Under Review"
- Jueces tienen acceso early a submissions del hackathon
- Solo necesitas que esté submitido antes del deadline

---

## 📊 MÉTRICAS EN MARKETPLACE

**Una vez live, Prompt Opinion trackea:**
- Views del listing
- Agent invocations
- Success rate
- Average response time
- User ratings (si habilitas reviews)

**Esto ayuda para judging** - muestra que tu agent funciona en producción real.

---

## 🐛 TROUBLESHOOTING

### **Problema: Agent Card Fetch Failed**

**Causa:** URL del agent card no responde o formato incorrecto

**Solución:**
```bash
# Test manual
curl https://authclear-agent.railway.app/.well-known/agent.json

# Debe retornar JSON válido con:
# - "name": "AuthClear..."
# - "version": "2.0.0"
# - "capabilities": {...}
```

---

### **Problema: Health Check Failed**

**Causa:** `/health` endpoint no responde o retorna error

**Solución:**
```bash
# Test manual
curl https://authclear-agent.railway.app/health

# Debe retornar 200 OK con:
# {"status":"ok","service":"authclear-agent"}
```

---

### **Problema: Test Task Failed**

**Causa:** Agent retorna error al procesar test task

**Solución:**
1. Ver logs en Railway → Service → Deployments → View Logs
2. Verificar que `ANTHROPIC_API_KEY` o AWS credentials estén configurados
3. Verificar que `MCP_SERVER_URL` apunte al MCP correcto

---

### **Problema: Submission Rejected**

**Razones comunes:**
- Agent no cumple con A2A protocol spec
- Health checks fallan consistentemente
- Descripción/documentation incompleta

**Solución:**
- Leer feedback del equipo de Prompt Opinion
- Corregir issues
- Re-submitear

---

## ✅ CHECKLIST FINAL

Antes de continuar a video demo:

- [ ] MCP Server submiteado en Prompt Opinion
- [ ] A2A Agent submiteado en Prompt Opinion
- [ ] Health checks pasan en ambos
- [ ] Test tasks completan exitosamente
- [ ] URLs del marketplace copiadas
- [ ] GitHub repo es público y tiene README

**SI TODO ✅ → Listo para Video Demo (último bloqueante)**

---

## 💡 TIPS PARA DESTACAR EN MARKETPLACE

**Screenshots:**
- Captura de Web UI mostrando confidence breakdown
- Architecture diagram (MCP + A2A + Claude)
- Sample output con scores

**Demo Video:**
- Embed en listing (próximo paso a grabar)
- Max 3 minutos
- Muestra value proposition claro

**README en GitHub:**
- Professional formatting
- Clear setup instructions
- Architecture diagram
- Sample requests/responses

**Responsive to Feedback:**
- Si jueces dejan comments, responder rápido
- Update listing si encuentras bugs
- Engagement cuenta para judging

---

## ⏭️ SIGUIENTE PASO

**Una vez Prompt Opinion esté completo:**

➡️ **Grabar Video Demo** (1-2 horas)

Ver archivo: `VIDEO_DEMO_GUIDE.md` (próximo a crear)

---

**Tiempo total de este paso:** ~20 minutos  
**Progreso:** 2/3 bloqueantes completados ✅
