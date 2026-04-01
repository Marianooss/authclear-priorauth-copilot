# 🐛 Bug Fixes - Hora 0-2

## Resumen
Durante la ejecución inicial del proyecto AuthClear, se identificaron y corrigieron **5 bugs críticos** que impedían el funcionamiento del sistema.

---

## Bugs Encontrados y Arreglados

### **Bug #1: Pydantic Validation Error - Extra Fields**
**Error:**
```
ValidationError: 6 validation errors for Settings
anthropic_api_key: Extra inputs are not permitted
port_agent: Extra inputs are not permitted
...
```

**Causa:** Pydantic v2 tiene `extra='forbid'` por defecto. Los archivos de configuración (`mcp_server/config.py` y `a2a_agent/config.py`) cargaban TODAS las variables del `.env`, pero cada uno solo definía un subconjunto.

**Fix:** Agregado `extra="ignore"` al `SettingsConfigDict` en ambos archivos.

**Archivos modificados:**
- `mcp_server/config.py` (línea 19)
- `a2a_agent/config.py` (línea 19)

---

### **Bug #2: Import Errors - Empty __init__.py**
**Error:**
```
ImportError: cannot import name 'resolve_icd10' from 'mcp_server.tools'
```

**Causa:** Los archivos `__init__.py` en `mcp_server/tools/` y `a2a_agent/tools/` estaban vacíos, no exportaban las funciones.

**Fix:** Completado los exports en los `__init__.py`:
- `mcp_server/tools/__init__.py` - exporta las 5 tools
- `a2a_agent/tools/__init__.py` - exporta `parse_fhir_bundle`, `FHIRParseError`, `MCPClient`

**Archivos modificados:**
- `mcp_server/tools/__init__.py`
- `a2a_agent/tools/__init__.py`

---

### **Bug #3: FastMCP API Change - 'description' Parameter**
**Error:**
```
TypeError: FastMCP() got unexpected keyword argument(s): 'description'
```

**Causa:** FastMCP 3.2.0 cambió el nombre del parámetro de `description` a `instructions`.

**Fix:** Cambiado a usar `instructions` y hacer `version` keyword-only.

**Código anterior:**
```python
mcp = FastMCP(
    "authclear-terminology",
    version="1.0.0",
    description="..."
)
```

**Código corregido:**
```python
mcp = FastMCP(
    name="authclear-terminology",
    instructions="...",
    version="1.0.0"
)
```

**Archivos modificados:**
- `mcp_server/server.py` (línea 35-39)

---

### **Bug #4: FastMCP No Soporta HTTP Endpoints**
**Error:**
```
AttributeError: 'FastMCP' object has no attribute 'get'
```

**Causa:** FastMCP 3.x no tiene decoradores HTTP como FastAPI (`@mcp.get()`). Es un servidor MCP puro que usa el protocolo MCP (stdio/SSE), no HTTP REST.

**Fix:** Removido el endpoint `/health` que usaba `@mcp.get()`. FastMCP maneja health checks a través del protocolo MCP.

**Archivos modificados:**
- `mcp_server/server.py` (líneas 178-187)

---

### **Bug #5: httpx.Timeout API Change**
**Error:**
```
ValueError: httpx.Timeout must either include a default, or set all four parameters explicitly.
```

**Causa:** httpx 0.28.1 cambió la API de `Timeout`. Ahora requiere un valor por defecto O los 4 parámetros explícitos (connect, read, write, pool).

**Fix:** Agregado parámetros `write` y `pool` al `httpx.Timeout`.

**Código anterior:**
```python
timeout=httpx.Timeout(
    connect=settings.http_connect_timeout,
    read=settings.http_read_timeout
)
```

**Código corregido:**
```python
timeout=httpx.Timeout(
    connect=settings.http_connect_timeout,
    read=settings.http_read_timeout,
    write=settings.http_connect_timeout,
    pool=settings.http_connect_timeout,
)
```

**Archivos modificados:**
- `mcp_server/http_client.py` (línea 30-34)

---

## Test Results

Después de arreglar todos los bugs, ejecutamos el test de integración:

```
============================================================
AuthClear Integration Test Suite
============================================================

=== Test 1: FHIR Parsing ===
OK Parsed patient: Maria González
OK Diagnoses: 1
OK Medications: 2
OK Lab results: 2

=== Test 2: MCP Tools ===
OK ICD-10 E11.9 -> SNOMED 44054006
OK Metformin -> RxNorm 1043567
OK HbA1c -> LOINC 4548-4
OK J0173 (Semaglutide) criteria loaded

=== Test 3: Pydantic Models ===
OK PriorAuthDraft created
OK human_review_required invariant verified

============================================================
OK ALL TESTS PASSED
============================================================
```

---

## Estado Final

✅ **Todos los módulos core funcionan correctamente:**
- FHIR bundle parsing
- Clinical code resolution (ICD-10, RxNorm, LOINC)
- Prior auth criteria lookup (6 payers cargados)
- Pydantic model validation
- Human-in-the-loop invariant

✅ **Ambos servicios se pueden importar sin errores**
✅ **Configuración cargando correctamente**
✅ **External API calls funcionando** (NLM ICD-10, RxNav)

---

## Scripts Creados

Durante la depuración, se crearon:
- `requirements.txt` - Dependencias de pip (alternativa a Poetry)
- `run_mcp_server.py` - Script de inicio para MCP Server
- `run_a2a_agent.py` - Script de inicio para A2A Agent
- `test_integration.py` - Test suite de integración

---

**Total time:** 2 horas
**Bugs fixed:** 5
**Tests passing:** 100%
**Status:** ✅ **READY FOR NEXT PHASE**
