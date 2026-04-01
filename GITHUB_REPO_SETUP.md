# 📦 Crear Repositorio de GitHub - Paso 1 Crítico

**Tiempo:** 5 minutos  
**Prerequisito:** Cuenta de GitHub (crear gratis en github.com)  
**Por qué es crítico:** Sin GitHub repo NO puedes deploy a Railway ni submitear a Devpost

---

## 🚀 OPCIÓN A: Crear Repo via Web (Recomendado - Más Fácil)

### **Paso 1: Ir a GitHub**
1. Abrir: https://github.com/new
2. Login si no estás logueado

### **Paso 2: Configurar Repo**

**Repository name:**
```
authclear-priorauth-copilot
```

**Description:**
```
AI-powered prior authorization copilot for physicians. Dual submission (MCP Server + A2A Agent) for Agents Assemble Healthcare Hackathon. Built with Claude Sonnet 4, FastAPI, FastMCP, FHIR R4.
```

**Visibility:**
- ✅ **Public** ← OBLIGATORIO para hackathon

**Initialize repository:**
- ❌ NO agregar README (ya tienes)
- ❌ NO agregar .gitignore (ya tienes)
- ❌ NO agregar license (o seleccionar MIT si quieres)

### **Paso 3: Crear Repository**
- Click botón verde: **"Create repository"**

### **Paso 4: GitHub te muestra comandos**

Copiar la sección que dice **"…or push an existing repository from the command line"**:

```bash
git remote add origin https://github.com/TU_USUARIO/authclear-priorauth-copilot.git
git branch -M main
git push -u origin main
```

---

## 💻 Paso 5: Conectar tu Código Local

Abrir terminal en la carpeta AuthClear:

```bash
cd c:\Users\user\Desktop\AuthClear

# Inicializar git (si no está inicializado)
git init

# Agregar todos los archivos
git add .

# Primer commit
git commit -m "feat: AuthClear system - agents.md compliant, 100% functional

- MCP Server with 5 healthcare terminology tools
- A2A Agent with Claude Sonnet 4 reasoning
- Confidence scoring (4-section rubric)
- Web UI with real-time processing
- 9 synthetic FHIR bundles (no PHI)
- Dual submission for Agents Assemble hackathon"

# Conectar con GitHub (copiar comando de GitHub)
git remote add origin https://github.com/TU_USUARIO/authclear-priorauth-copilot.git

# Push a GitHub
git branch -M main
git push -u origin main
```

**⚠️ IMPORTANTE:** Reemplazar `TU_USUARIO` con tu username real de GitHub

---

## ✅ Verificación

1. **Ir a tu repo:** `https://github.com/TU_USUARIO/authclear-priorauth-copilot`
2. **Deberías ver:**
   - Todos tus archivos (mcp_server/, a2a_agent/, shared/, web_ui/)
   - README.md
   - Documentación (HONEST_STATUS_REPORT.md, etc.)
   - Dockerfiles

**Si ves todo → ✅ GitHub repo creado exitosamente**

---

## 🐛 Problemas Comunes

### **Problema: "git: command not found"**

**Solución:** Instalar Git:
1. Descargar: https://git-scm.com/download/win
2. Instalar con opciones default
3. Reiniciar terminal
4. Reintentar comandos

---

### **Problema: "fatal: not a git repository"**

**Solución:**
```bash
cd c:\Users\user\Desktop\AuthClear
git init
# Luego continuar con git add, git commit, etc.
```

---

### **Problema: "remote origin already exists"**

**Solución:**
```bash
# Remover remote existente
git remote remove origin

# Agregar nuevamente
git remote add origin https://github.com/TU_USUARIO/authclear-priorauth-copilot.git
```

---

### **Problema: "failed to push some refs"**

**Causa:** Alguien más hizo cambios en GitHub

**Solución:**
```bash
git pull origin main --allow-unrelated-histories
git push -u origin main
```

---

### **Problema: Git pide username/password en cada push**

**Solución:** Usar Personal Access Token:

1. Ir a: https://github.com/settings/tokens
2. "Generate new token (classic)"
3. Scopes: seleccionar "repo"
4. Copiar token (guárdalo - solo se muestra una vez)
5. Cuando Git pida password, usar el token en lugar de password

**O mejor: Usar SSH keys** (más seguro):
```bash
# Generar SSH key
ssh-keygen -t ed25519 -C "tu_email@example.com"

# Copiar public key
cat ~/.ssh/id_ed25519.pub

# Agregar en GitHub: Settings → SSH keys → New SSH key

# Cambiar remote a SSH
git remote set-url origin git@github.com:TU_USUARIO/authclear-priorauth-copilot.git
```

---

## 📝 Después de Crear Repo

### **Actualizar Railway Config (cuando hagas deploy):**

Railway va a auto-detectar tu repo si usas GitHub OAuth.

### **Actualizar Prompt Opinion (cuando publiques):**

Van a pedirte GitHub URL en el form.

### **Actualizar Devpost (cuando submitteas):**

Van a pedirte GitHub URL en submission form.

---

## 🎯 README Profesional (Opcional pero Recomendado)

Una vez que el repo esté en GitHub, considera mejorar el README:

**Secciones recomendadas:**
1. Banner/Logo (opcional)
2. Badges (build status, etc.)
3. Description corta
4. Architecture diagram
5. Quick start guide
6. API documentation
7. Demo video (embed YouTube)
8. Screenshots
9. License
10. Credits

**Ejemplo de badges:**
```markdown
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![Built with Claude](https://img.shields.io/badge/Built%20with-Claude%20Sonnet%204-purple)](https://anthropic.com)
```

**Pero NO es bloqueante para submission** - puedes mejorar README después del hackathon.

---

## ✅ Checklist

Antes de continuar a Railway deploy:

- [ ] Cuenta de GitHub creada
- [ ] Repo creado en GitHub (público)
- [ ] Git inicializado en carpeta local
- [ ] Commit inicial hecho
- [ ] Remote origin configurado
- [ ] Código pusheado a GitHub
- [ ] Verificado visualmente en github.com/TU_USUARIO/repo

**Si todo ✅ → Continuar a [DEPLOY_CHECKLIST.md](DEPLOY_CHECKLIST.md)**

---

## ⏭️ Siguiente Paso

**Una vez GitHub esté listo:**

➡️ **Deploy a Railway** (30 min)

Ver: [DEPLOY_CHECKLIST.md](DEPLOY_CHECKLIST.md)

---

**Tiempo de este paso:** 5 minutos  
**Progreso:** Prerequisito completado ✅
