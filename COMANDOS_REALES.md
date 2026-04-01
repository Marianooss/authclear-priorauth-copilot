# 🚀 AuthClear - Comandos Reales Para Video Demo

**Actualizado:** 2026-03-30

---

## 📋 Opción 1: Demo Simulado (MÁS FÁCIL para video)

**Usa esto si quieres grabar rápido sin levantar servers:**

```bash
cd C:\Users\user\Desktop\devpost
run_live_demo.bat
```

Este script:
- ✅ Ejecuta código real (parse FHIR, resolve códigos)
- ✅ Muestra output paso a paso con delays
- ✅ Perfecto para narrar encima
- ✅ Duración: ~40 segundos
- ⚠️ No levanta el server completo

**Para grabar:**
1. Abre PowerShell en pantalla completa
2. Ejecuta `run_live_demo.bat`
3. Win+G → Empezar grabación
4. Narrar mientras se ejecuta

---

## 📋 Opción 2: Sistema Completo (MÁS REAL)

**Si quieres mostrar la app funcionando end-to-end:**

### Paso 1: Levantar MCP Server (Terminal 1)

```bash
cd C:\Users\user\Desktop\devpost
python run_mcp_server.py
```

**Verás:**
```
INFO starting_mcp_server port=8001 environment=development
```

**Dejar corriendo.**

---

### Paso 2: Levantar A2A Agent (Terminal 2)

```bash
cd C:\Users\user\Desktop\devpost
python run_a2a_agent.py
```

**Verás:**
```
INFO starting_agent_server port=8000
INFO: Uvicorn running on http://0.0.0.0:8000
INFO: Application startup complete
```

**Dejar corriendo.**

---

### Paso 3: Ejecutar Demo (Terminal 3)

```bash
cd C:\Users\user\Desktop\devpost
python demo_full_system.py
```

**Verás:**
```
================================================================================
  AuthClear - Full System Demo
================================================================================

Patient: Maria Gonzalez, 50F
Medication: Ozempic (semaglutide)

================================================================================
  Step 1: Check System Status
================================================================================

  Checking A2A Agent (http://localhost:8000)...
  [OK] A2A Agent is RUNNING
      Service: AuthClear Prior Auth Copilot
      Version: 1.0.0
...
```

---

## 🎬 Para el Video - Recomendación

### Opción A: Simulado (Recomendado)
**Pros:**
- ✅ Más fácil de grabar (1 solo terminal)
- ✅ Ejecuta código real
- ✅ Timing perfecto para narración

**Comando:**
```bash
run_live_demo.bat
```

---

### Opción B: Sistema Completo
**Pros:**
- ✅ Muestra arquitectura real client-server
- ✅ Demo end-to-end con HTTP requests

**Comandos:**
```bash
# Terminal 1
python run_mcp_server.py

# Terminal 2 (esperar 2 segundos)
python run_a2a_agent.py

# Terminal 3 (esperar 2 segundos)
python demo_full_system.py
```

---

## 🎥 Layout de Pantalla Para Grabar

### Si usas Opción A (1 terminal):
```
┌─────────────────────────────────────┐
│                                     │
│     Terminal (pantalla completa)    │
│                                     │
│   > run_live_demo.bat               │
│                                     │
│   Output del demo...                │
│                                     │
└─────────────────────────────────────┘
```

### Si usas Opción B (3 terminales):
```
┌──────────────┬──────────────┬──────────────┐
│              │              │              │
│ Terminal 1   │ Terminal 2   │ Terminal 3   │
│ MCP Server   │ A2A Agent    │ Demo Client  │
│              │              │              │
│ (logs)       │ (logs)       │ (output)     │
│              │              │              │
└──────────────┴──────────────┴──────────────┘
```

**Para Opción B:** Usa Windows Terminal con 3 panes o tmux

---

## ✅ Verificar Que Todo Funciona

Antes de grabar, prueba:

```bash
# Test 1: Verificar dependencias
python -c "import fastmcp, fastapi, fhir.resources; print('OK')"

# Test 2: Verificar archivos FHIR
python -c "from pathlib import Path; import json; json.loads(Path('shared/fhir/synthetic_patients/patient_t2dm_complete.json').read_text()); print('OK')"

# Test 3: Ejecutar demo simulado
run_live_demo.bat
```

Si todo imprime "OK", estás listo.

---

## 🎬 Plan de Video Final

### Scene 1: Title Card (30s)
- HTML: `title_card_final.html`

### Scene 2: Architecture (20s)
- HTML: `architecture_responsive.html`

### Scene 3: **DEMO REAL** (40s) ⭐
**Opción Recomendada:**
```bash
run_live_demo.bat
```

**O si prefieres sistema completo:**
```bash
# Levantar servers primero (no mostrar en video)
python run_mcp_server.py  # background
python run_a2a_agent.py   # background

# Mostrar esto en video:
python demo_full_system.py
```

### Scene 4: Compliance + ROI (25s)
- HTML: `compliance_roi_combined.html`

---

## 🐛 Troubleshooting

### Error: "A2A Agent is NOT RUNNING"
```bash
# Asegúrate de levantar el agent primero:
python run_a2a_agent.py
```

### Error: "Port 8000 already in use"
```bash
# Mata el proceso:
netstat -ano | findstr :8000
taskkill /PID <pid> /F
```

### Error: "ModuleNotFoundError: No module named 'fastmcp'"
```bash
# Instala dependencias:
pip install -r requirements.txt
```

### Error: UnicodeEncodeError en terminal
```bash
# Usa PowerShell en lugar de CMD
# O ejecuta: chcp 65001
```

---

## 📝 Resumen

**Para el video, usa:**

```bash
run_live_demo.bat
```

**Es la opción más simple y muestra código real ejecutándose.**

Si quieres mostrar el sistema completo con servers, necesitas 3 terminales y es más complejo de grabar.

**Mi recomendación:** Usa `run_live_demo.bat` para la Scene 3 del video.
