# 🎬 Guía Rápida: Graba tu Video en 30 Minutos

**Todo está listo. Solo necesitas grabar y narrar.**

---

## ⚡ PASO 1: Abre los Demos (1 minuto)

Ejecuta esto:

```bash
C:\Users\user\Desktop\devpost\open_demos.bat
```

Se abrirán 3 pestañas en tu navegador:
1. **Title Card** - Portada AuthClear
2. **Architecture** - Arquitectura animada con flujo de datos
3. **Demo Flow** - Proceso completo paso a paso (auto-animado)

---

## 🎥 PASO 2: Graba Cada Escena con Game Bar

### Escena 1: Title Card (30 segundos)

1. **Cambiar a pestaña:** `title_card_final.html`
2. **Presiona F11** (fullscreen)
3. **Win + G** → Click en grabar (círculo rojo)
4. **Narrar:**

```
"Physicians spend 12 hours per week on prior authorizations.
That's 43 requests per physician, costing the healthcare system
31 billion dollars annually.

The problem? Clinical data is locked in fragmented EHR systems,
and payers require extensive documentation.

AuthClear solves this with two AI agents:
a FHIR terminology engine and a prior authorization copilot."
```

5. **Win + G → Parar grabación** (después de 30s)

---

### Escena 2: Architecture (20 segundos)

1. **Cambiar a pestaña:** `architecture_responsive.html`
2. **F11** (fullscreen)
3. **Win + G** → Grabar
4. **Narrar:**

```
"AuthClear consists of two agents.

First, the MCP Server: a clinical terminology engine that
translates ICD-10, RxNorm, and LOINC codes using FHIR R4 standards.

Second, the A2A Agent: a prior authorization copilot that
reads patient data, identifies requirements, and generates
structured authorization drafts."
```

5. **Parar** (20s)

**NOTA:** Verás la animación de datos moviéndose entre componentes. ¡Déjala correr!

---

### Escena 3: Demo Flow (40 segundos)

1. **Cambiar a pestaña:** `demo_flow_responsive.html`
2. **F11** (fullscreen)
3. **Win + G** → Grabar
4. **Narrar:**

```
"Let's see how AuthClear processes a real prior authorization
for Maria González, a 50-year-old patient with Type 2 Diabetes
requesting Ozempic.

Step 1: The A2A Agent loads her FHIR bundle. She has HbA1c 8.9%,
BMI 34, and has tried Metformin and Glipizide.

Step 2: The agent calls the MCP Server to resolve clinical codes.

Step 3: It retrieves prior auth criteria: HbA1c must be above 7.5%,
BMI above 30, and two medication trials documented.

Step 4: Using Claude's reasoning, the agent evaluates:
all criteria are met.

Step 5: The agent generates a structured prior auth draft
with 90% confidence, ready for human review."
```

5. **Parar** (40s)

**NOTA:** Los pasos aparecen automáticamente. Solo narra mientras ves la animación.

---

### Escena 4: Compliance + ROI (25 segundos)

**Opción A: Usar los HTMLs existentes**

1. Abrir `compliance_badges.html` y `roi_calculator.html` en pestañas separadas
2. Organizar ventanas lado a lado (50% cada una)
3. Win + G → Grabar ambas
4. **Narrar:**

```
"AuthClear is compliant with state AI transparency laws:
Texas SB 490, Arizona HB 2417, and Maryland HB 1174.
Human-in-the-loop is architecturally enforced.

The impact? For a 10-physician practice processing
430 prior auths per week, AuthClear saves 8 hours per week
in staff time. That's 83,000 dollars per year in labor costs alone.

AuthClear: AI-powered prior authorization that keeps
physicians in control."
```

5. Parar (25s)

**Opción B: Si quieres más fácil, te creo un HTML combinado** - dime y lo hago en 2 min

---

## 🎬 PASO 3: Encontrar tus Videos

Los videos se guardan automáticamente en:

```
C:\Users\user\Videos\Captures\
```

Verás archivos como:
- `Desktop 2026-03-30 23-45-12.mp4`
- `Desktop 2026-03-30 23-46-30.mp4`
- etc.

Renómbralos a:
- `scene1_title.mp4`
- `scene2_architecture.mp4`
- `scene3_demo.mp4`
- `scene4_compliance.mp4`

---

## ✂️ PASO 4: Unir los Videos (10 minutos)

### Opción A: Windows Video Editor (Pre-instalado)

1. Busca "Video Editor" en el menú inicio
2. New Project → "AuthClear Demo"
3. Add → Agregar los 4 videos en orden
4. Arrastra cada uno al timeline
5. File → Export → 1080p
6. Guardar como `authclear_demo_final.mp4`

### Opción B: Online (rápido)

1. Ve a https://www.kapwing.com/tools/join-videos
2. Upload los 4 videos
3. Organízalos en orden
4. Export → Download

---

## 📤 PASO 5: Subir a YouTube (5 minutos)

1. Ve a https://studio.youtube.com
2. Click "Create" → "Upload video"
3. Select `authclear_demo_final.mp4`

**Detalles:**
- **Title:** `AuthClear - AI Prior Authorization Copilot (Agents Assemble 2026)`
- **Description:**
```
AuthClear: AI-powered prior authorization for healthcare

🏆 Agents Assemble Hackathon 2026
🔗 GitHub: https://github.com/yourusername/authclear
🏗️ MCP Server + A2A Agent

Tech: FastMCP, Claude Sonnet 4, FHIR R4, Python
Compliant: TX SB 490, AZ HB 2417, MD HB 1174
```
- **Visibility:** Unlisted
- **Subtitles:** Upload `authclear_demo_subtitles.srt`

4. Click "Publish"
5. Copy URL → Add to Devpost

---

## ⏱️ Tiempo Total Estimado

| Paso | Tiempo |
|------|--------|
| Abrir demos | 1 min |
| Grabar 4 escenas | 10 min (2-3 takes cada una) |
| Unir videos | 10 min |
| Upload YouTube | 5 min |
| **TOTAL** | **~30 minutos** |

---

## 💡 Tips Pro

### Si te equivocas narrando:
- No pares la grabación
- Pausa 2 segundos en silencio
- Repite desde donde te equivocaste
- Luego cortas el error en Video Editor

### Si los HTMLs no se ven bien:
- **Zoom del navegador:** Ctrl + "+" o Ctrl + "-"
- Ajusta hasta que todo quepa en pantalla
- Luego F11 para fullscreen

### Si Game Bar no funciona:
- Ve a Settings → Gaming → Game Bar
- Activa "Record game clips..."
- O usa: Win + Alt + R (shortcut directo)

---

## 🎯 Orden Final de Escenas

1. **Title Card** (30s) - Problema
2. **Architecture** (20s) - Solución
3. **Demo Flow** (40s) - Cómo funciona
4. **Compliance** (25s) - Impacto + compliance

**Total:** 2:55 ✅ (bajo 3:00 requerido)

---

## ✅ Checklist Pre-Grabación

- [ ] Ejecutar `open_demos.bat`
- [ ] Verificar que los 3 HTMLs se abren correctamente
- [ ] Testear Win+G (Game Bar funciona)
- [ ] Leer narración de cada escena en voz alta (práctica)
- [ ] Silenciar notificaciones (Focus Assist)
- [ ] Tener script impreso o en segundo monitor

---

## 🆘 Si Algo Falla

**Game Bar no graba:**
- Alt: OBS Studio (https://obsproject.com)
- Alt: Loom (https://loom.com) - online, gratis

**Videos muy largos:**
- En Video Editor, usa "Trim" para cortar
- Target: 30s, 20s, 40s, 25s

**Calidad baja:**
- Settings → Gaming → Captures
- Video quality: "Standard" o "High"

---

## 🚀 ¡EMPIEZA AHORA!

```bash
C:\Users\user\Desktop\devpost\open_demos.bat
```

**Los demos ya están animados. Solo necesitas:**
1. Presionar F11
2. Presionar Win+G
3. Narrar mientras grabas

**¡Suerte! En 30 minutos tendrás tu video listo para Devpost.** 🎬
