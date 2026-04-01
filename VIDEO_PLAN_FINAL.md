# 🎬 AuthClear Video Demo - Plan Final

**Duración:** 2:55 (bajo 3:00 requerido)
**Opción:** Con Web UI (MÁS PROFESIONAL) ⭐

---

## 🎯 Scene Breakdown

### Scene 1: Title Card (0:00-0:30) - 30 segundos

**Archivo:** `video_assets/title_card_final.html`

**Pasos:**
1. Abrir en Chrome → F11 (fullscreen)
2. Win+G → Grabar
3. **Narrar:**
   ```
   Physicians spend 12 hours per week on prior authorizations.
   That's 43 requests per physician, costing $31 billion annually.

   AuthClear solves this with two AI agents:
   a FHIR terminology engine and a prior authorization copilot.
   ```
4. Parar grabación

---

### Scene 2: Architecture (0:30-0:50) - 20 segundos

**Archivo:** `video_assets/architecture_responsive.html`

**Pasos:**
1. Abrir en Chrome → F11
2. Win+G → Grabar
3. **Narrar:**
   ```
   AuthClear consists of two agents.
   First, the MCP Server: a clinical terminology engine.
   Second, the A2A Agent: a prior authorization copilot.
   ```
4. Parar grabación

---

### Scene 3: Web UI Demo ⭐ (0:50-1:30) - 40 segundos

**NUEVO: Interfaz Web Profesional**

**Setup:**
```bash
# Terminal 1 (background, no mostrar):
python run_a2a_agent.py

# Terminal 2:
.\start_web_ui.bat
```

**Pasos:**
1. Browser abre en http://localhost:3000
2. F11 (fullscreen)
3. Win+G → Grabar
4. **Interactuar con la UI:**
   - Select "Maria González - Type 2 DM" del dropdown
   - Ver info del paciente aparecer
   - Medication ya dice "Ozempic (semaglutide)"
   - Payer: "Generic Insurance"
   - Click "Process Prior Authorization"
   - **Ver las 5 animaciones de pasos:**
     1. Loading FHIR bundle ✓
     2. Resolving codes ✓
     3. Retrieving criteria ✓
     4. Evaluating ✓
     5. Generating draft ✓
   - Ver resultados aparecer:
     - Confidence: 90% (HIGH)
     - Criteria Met: 4/4
     - Ready for Review
5. **Narrar mientras interactúas:**
   ```
   Let's see AuthClear in action.
   I select Maria González, a 50-year-old with Type 2 Diabetes.

   The system processes her case in real-time:
   loading her FHIR data, resolving clinical codes,
   retrieving prior auth criteria, evaluating requirements.

   Result: 90% confidence, all criteria met,
   ready for physician review.
   ```
6. Parar grabación (~40s)

**Alternativa si prefieres terminal:**
- Usar `run_live_demo.bat` en lugar del Web UI
- Mismo timing, pero menos visual

---

### Scene 4: Compliance + ROI (1:30-2:55) - 25 segundos

**Archivo:** `video_assets/compliance_roi_combined.html`

**Pasos:**
1. Abrir en Chrome → F11
2. Win+G → Grabar
3. **Narrar:**
   ```
   AuthClear is compliant with state AI laws:
   Texas SB 490, Arizona HB 2417, Maryland HB 1174.
   Human-in-the-loop is architecturally enforced.

   For a 10-physician practice, AuthClear saves
   8 hours per week. That's $83,000 per year.

   AuthClear: AI-powered authorization that keeps physicians in control.
   ```
4. Parar grabación

---

## ⚡ Quick Recording Guide

### Setup (5 minutos)

```bash
# 1. Verificar que todo funciona
.\start_web_ui.bat  # Se abre browser automáticamente

# 2. Probar el flujo completo una vez
# - Select patient
# - Click Process
# - Ver que funciona

# 3. Cerrar browser, listo para grabar
```

### Recording (15 minutos)

```bash
# Scene 1: Title Card
# - Abrir title_card_final.html
# - F11 → Win+G → Grabar → Narrar → Parar (30s)

# Scene 2: Architecture
# - Abrir architecture_responsive.html
# - F11 → Win+G → Grabar → Narrar → Parar (20s)

# Scene 3: Web UI Demo
# - .\start_web_ui.bat
# - F11 → Win+G → Grabar → Interactuar + Narrar → Parar (40s)

# Scene 4: Compliance
# - Abrir compliance_roi_combined.html
# - F11 → Win+G → Grabar → Narrar → Parar (25s)
```

### Post-Production (10 minutos)

```bash
# 1. Videos en: C:\Users\user\Videos\Captures\
# 2. Renombrar: scene1.mp4, scene2.mp4, scene3.mp4, scene4.mp4
# 3. Abrir Windows Video Editor
# 4. New Project → "AuthClear Demo"
# 5. Add 4 videos en orden
# 6. Export → 1080p
# 7. Guardar como: authclear_demo_final.mp4
```

---

## 🎨 Ventajas del Web UI

### VS Terminal Demo:

| Aspecto | Terminal | Web UI |
|---------|----------|--------|
| Visual | ❌ Texto plano | ✅ Interfaz profesional |
| Interactividad | ❌ Automático | ✅ Click buttons |
| Animaciones | ❌ Logs | ✅ Pasos animados |
| Resultados | ❌ JSON texto | ✅ Cards visuales |
| Impresión | 6/10 | 9/10 |

### Para los Jueces:

- ✅ Demuestra habilidades full-stack
- ✅ Producto "terminado" no solo backend
- ✅ Más fácil de entender visualmente
- ✅ Se ve como producto real, no prototipo

---

## 🎯 Recomendación Final

**USA EL WEB UI** para Scene 3.

Es más impresionante y toma el mismo tiempo grabar.

Si tienes algún problema con el Web UI, el fallback es `run_live_demo.bat` (también funciona perfecto).

---

## 📋 Checklist Pre-Grabación

**Web UI:**
- [ ] `.\start_web_ui.bat` funciona
- [ ] Browser abre en http://localhost:3000
- [ ] Dropdown de pacientes funciona
- [ ] Botón "Process" activa animaciones
- [ ] Resultados se muestran correctamente

**Otros HTMLs:**
- [ ] title_card_final.html se ve bien
- [ ] architecture_responsive.html se ve bien
- [ ] compliance_roi_combined.html se ve bien

**Recording:**
- [ ] Win+G funciona (Game Bar)
- [ ] Micrófono testeado
- [ ] Notificaciones silenciadas
- [ ] Script de narración listo

---

## 🚀 ¡Listo Para Grabar!

**Tiempo total:** ~30 minutos (setup + grabación + edición)

**Próximo paso:**
```bash
.\start_web_ui.bat
```

Prueba el Web UI y dime si se ve bien para grabar.
