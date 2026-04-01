# 🎬 AuthClear Video - Escenas Actualizadas

**Duración total:** 2:55
**Archivos HTML mejorados:** 3 nuevos + 2 originales

---

## 📺 Plan de Grabación Actualizado

### ✅ Scene 1: Title Card (0:00-0:30) - 30 segundos
**Archivo:** `title_card_final.html`
**Acción:**
1. Abrir HTML en Chrome → F11 (fullscreen)
2. Win+G → Grabar
3. Narrar: "Physicians spend 12 hours per week on prior authorizations. That's 43 requests per physician, costing the healthcare system 31 billion dollars annually..."

---

### ✅ Scene 2A: Architecture Interactive (0:30-0:50) - 20 segundos
**Archivo:** `architecture_interactive.html` ⭐ NUEVO
**Características:**
- Animación de datos moviéndose entre componentes
- Métricas en tiempo real
- Status "LIVE • FUNCTIONAL"

**Acción:**
1. Abrir HTML → F11
2. Win+G → Grabar (la animación ya está corriendo)
3. Narrar: "AuthClear consists of two agents. First, the MCP Server... Second, the A2A Agent..."

**Alternativa:** `architecture_diagram.html` (versión estática simple)

---

### ✅ Scene 2B: Demo Flow Animado (0:50-1:30) - 40 segundos
**Archivo:** `demo_flow_animated.html` ⭐ NUEVO
**Características:**
- Timeline vertical con 5 pasos
- Auto-animado (aparece paso a paso)
- Muestra caso real de María González
- Barra de confianza 90%

**Acción:**
1. Abrir HTML → F11
2. Win+G → Grabar (déjalo correr 40s, se anima solo)
3. Narrar: "Let's see how AuthClear processes a real prior authorization. Step 1: Load patient FHIR bundle... Step 2: Call MCP Server..."

**O usa:** Terminal demo (como estaba planeado originalmente)

---

### Scene 3: Terminal Demo (1:30-2:10) - 40 segundos
**Archivo:** Terminal + comandos de `DEMO_COMMANDS.md`
**Acción:**
1. Abrir PowerShell/Terminal
2. Win+G → Grabar
3. Ejecutar comandos:
   ```bash
   # Comando 1: ICD-10
   python -c "import asyncio; from mcp_server.tools.icd10 import resolve_icd10; print(asyncio.run(resolve_icd10('E11.9')))"

   # Comando 2: RxNorm
   python -c "import asyncio; from mcp_server.tools.rxnorm import lookup_rxnorm; print(asyncio.run(lookup_rxnorm('Ozempic')))"

   # Comando 3: Prior Auth
   python -c "from mcp_server.tools.prior_auth import get_prior_auth_criteria; print(get_prior_auth_criteria('J0173', 'generic'))"
   ```

**Narración:** "The MCP Server resolves ICD-10 E11.9 to SNOMED... looks up Ozempic in RxNorm... retrieves prior auth criteria..."

---

### ✅ Scene 4: Compliance + ROI (2:10-2:55) - 45 segundos
**Archivos:** `compliance_badges.html` + `roi_calculator.html`
**Acción:**
1. Abrir ambos HTML en pestañas separadas
2. Organizar side-by-side (compliance izq, ROI der)
3. Win+G → Grabar
4. Narrar: "AuthClear is compliant with Texas SB 490, Arizona HB 2417, and Maryland HB 1174. For a 10-physician practice, AuthClear saves 8 hours per week, that's $83,000 per year in labor costs alone."

---

## 🎯 Recomendación Final

### Opción A: Todo HTML (Más Fácil) - 2:55 total
1. **title_card_final.html** (30s)
2. **architecture_interactive.html** (20s) ⭐
3. **demo_flow_animated.html** (40s) ⭐
4. **compliance + ROI** side by side (45s)
5. **title_card_final.html** fade out (20s)

**Ventaja:** Todo pre-animado, solo narras encima. No necesitas ejecutar comandos.

---

### Opción B: HTML + Terminal (Más Real) - 2:55 total
1. **title_card_final.html** (30s)
2. **architecture_interactive.html** (20s) ⭐
3. **Terminal ejecutando comandos** (40s) - Demo real
4. **demo_flow_animated.html** (40s) ⭐ - Muestra resultado
5. **compliance + ROI** (45s)

**Ventaja:** Muestra código real ejecutándose.

---

## 🚀 Ejecuta Esto Ahora

```bash
# Abre ambos demos nuevos para verlos:
C:\Users\user\Desktop\devpost\open_demos.bat
```

Este script abre:
1. `architecture_interactive.html` - Verás la animación de flujo de datos
2. `demo_flow_animated.html` - Verás los 5 pasos aparecer automáticamente

**Presiona F11 en cada uno para ver fullscreen** y decide cuál te gusta más.

---

## ⏱️ Timing Detallado

| Tiempo | Archivo | Duración | Narración |
|--------|---------|----------|-----------|
| 0:00 | title_card_final.html | 30s | Problema statement |
| 0:30 | architecture_interactive.html | 20s | Dual agent system |
| 0:50 | demo_flow_animated.html | 40s | Proceso paso a paso |
| 1:30 | Terminal (opcional) | 40s | Demo código real |
| 2:10 | compliance + ROI | 45s | Compliance + impacto |

---

## ✅ Checklist Pre-Grabación

- [ ] Run `open_demos.bat` para ver los HTMLs
- [ ] Decidir: ¿Opción A (todo HTML) u Opción B (HTML + Terminal)?
- [ ] Leer narración de `VIDEO_SCRIPT_3MIN.md` en voz alta
- [ ] Testear Win+G (Game Bar funciona)
- [ ] Silenciar notificaciones (Focus Assist)

---

**¿Listo para ver los demos?**

Ejecuta `open_demos.bat` y dime cuál de los 2 HTML nuevos te gusta más para usarlos en el video.
