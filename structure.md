# structure.md — Module Responsibilities
> Quick reference for "what does X do and what does it NOT do"

---

## PRINCIPLE: Single Responsibility, Clear Boundaries

Each module has exactly one job. Cross-cutting concerns (logging, config, HTTP retry) live in dedicated modules.

---

## MCP SERVER MODULES

### `mcp_server/server.py`
**Does:** Registers all 5 FastMCP tools. Configures SSE transport. Exposes `/health` endpoint.  
**Does NOT:** Contain any business logic. No HTTP calls. No caching.  
**Depends on:** `mcp_server/tools/*`, `mcp_server/config.py`

```python
# What server.py looks like (simplified)
from fastmcp import FastMCP
from mcp_server.tools import resolve_icd10, lookup_rxnorm, check_drug_interactions, get_loinc_code, get_prior_auth_criteria

mcp = FastMCP("authclear-terminology")
mcp.tool()(resolve_icd10)
mcp.tool()(lookup_rxnorm)
mcp.tool()(check_drug_interactions)
mcp.tool()(get_loinc_code)
mcp.tool()(get_prior_auth_criteria)
```

---

### `mcp_server/tools/icd10.py`
**Does:** One function — `resolve_icd10(code)`. Calls NLM API. Caches result. Returns `ICD10Resolution`.  
**Does NOT:** Know about SNOMED in depth. Does not validate whether the code is clinically appropriate.  
**External API:** `https://cts.nlm.nih.gov/fhir/ConceptMap/$translate`  
**Cache TTL:** 3600s (ICD-10 codes change annually at most)

---

### `mcp_server/tools/rxnorm.py`
**Does:** Two functions — `lookup_rxnorm(drug_name)` and `check_drug_interactions(rxnorm_ids)`.  
**Does NOT:** Know about prior auth criteria (that's `prior_auth.py`). Does not validate clinical appropriateness.  
**External API:** `https://rxnav.nlm.nih.gov/REST/`  
**Cache TTL:** 3600s for lookups, 300s for interactions

---

### `mcp_server/tools/loinc.py`
**Does:** One function — `get_loinc_code(test_name)`. Maps common lab test names to LOINC codes.  
**Does NOT:** Validate lab values or reference ranges. Does not interpret results.  
**External API:** `https://fhir.loinc.org/CodeSystem/$lookup` with NLM fallback  
**Cache TTL:** 3600s

---

### `mcp_server/tools/prior_auth.py`
**Does:** One function — `get_prior_auth_criteria(cpt_code, payer)`. Reads from YAML files at startup.  
**Does NOT:** Call any external API. Does not make clinical judgments.  
**Data source:** `mcp_server/data/criteria/*.yaml` — loaded into memory at startup  
**Cache TTL:** Infinite (loaded once at startup)

---

### `mcp_server/cache.py`
**Does:** Provides `TTLCache` instances for each tool. Provides `cache_key()` helper.  
**Does NOT:** Store anything outside process memory. No Redis. No disk.  
**Pattern:**
```python
def cache_key(fn_name: str, *args) -> str:
    return f"{fn_name}:{':'.join(str(a) for a in args)}"
```

---

### `mcp_server/http_client.py`
**Does:** Creates and configures `httpx.AsyncClient` with timeout and retry logic.  
**Does NOT:** Know what the client is being used for.  
**Pattern:**
```python
async def get_http_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(
        timeout=httpx.Timeout(connect=10.0, read=30.0),
        follow_redirects=True,
        headers={"User-Agent": "AuthClear/1.0 (Hackathon; synthetic data only)"}
    )
```

---

## A2A AGENT MODULES

### `a2a_agent/main.py`
**Does:** Creates FastAPI app. Registers routes. Configures lifespan (startup/shutdown for MCPClient).  
**Does NOT:** Contain business logic. No Claude calls.  
**Routes registered:**
- `GET /.well-known/agent.json` → agent_card
- `POST /tasks/send` → task_handler
- `GET /tasks/{task_id}` → task_store lookup
- `POST /tasks/{task_id}/cancel` → task_store cancel
- `GET /health` → `{"status": "ok"}`

---

### `a2a_agent/agent_card.py`
**Does:** Returns the A2A AgentCard JSON. Reads `MCP_SERVER_URL` to include tool URLs.  
**Does NOT:** Change behavior. Pure data declaration.  
**Output:** Static JSON matching A2A AgentCard schema

---

### `a2a_agent/task_handler.py`
**Does:** Validates `SendTaskRequest`. Looks up or creates task in store. Triggers orchestrator. Returns `SendTaskResponse`.  
**Does NOT:** Run the ReAct loop directly. No Claude calls. No MCP calls.  
**Pattern:**
```python
async def handle_send_task(request: SendTaskRequest, mcp: MCPClient) -> SendTaskResponse:
    task = task_store.get(request.id) if request.id else task_store.create(request)
    task = await orchestrator.run_prior_auth_orchestration(task, mcp)
    task_store.update(task)
    return SendTaskResponse(task=task)
```

---

### `a2a_agent/task_store.py`
**Does:** In-memory dict of tasks with TTL. Create, get, update, cancel operations. Background cleanup.  
**Does NOT:** Persist to disk or database. Tasks are ephemeral (24h TTL).  
**Thread safety:** Uses `asyncio.Lock` for all mutations

---

### `a2a_agent/orchestrator.py`
**Does:** The ReAct loop. Sends messages to Claude API. Dispatches tool calls. Returns `PriorAuthDraft`.  
**Does NOT:** Validate input (that's task_handler). Update the task store (that's task_handler). Define tools (that's `tools/`).  
**See:** `cot_react.md` for the full implementation

---

### `a2a_agent/tools/fhir_reader.py`
**Does:** Parses raw FHIR R4 Bundle JSON → `PatientBundle` model. Pure function, no I/O.  
**Does NOT:** Call HAPI FHIR server. Does not validate clinical content.  
**Handles:** Patient, Condition, MedicationRequest, Observation, AllergyIntolerance resources  
**Error:** Raises `FHIRParseError` with field-level detail

---

### `a2a_agent/tools/mcp_client.py`
**Does:** Wraps MCP Server HTTP calls. Retry logic. Returns typed response models.  
**Does NOT:** Know about FHIR or prior auth logic.  
**Pattern:**
```python
class MCPClient:
    def __init__(self, base_url: str):
        self._base_url = base_url
        self._client = None  # initialized in async context manager
    
    async def resolve_icd10(self, code: str) -> ICD10Resolution:
        response = await self._post("/tools/resolve_icd10", {"code": code})
        return ICD10Resolution.model_validate(response)
```

---

### `a2a_agent/prompts/system.py`
**Does:** Builds the system prompt string for Claude. Single source of truth for agent behavior.  
**Does NOT:** Change based on patient data (that's the user message). No dynamic content.  
**Rule:** Any change to agent behavior must go through this file.

---

## SHARED MODULES

### `shared/models/patient.py`
**Does:** Pydantic models for parsed patient data: `PatientBundle`, `PatientDemographics`, `Medication`, `LabResult`, `Diagnosis`.  
**Does NOT:** Parse FHIR JSON (that's `fhir_reader.py`). Does not validate clinical logic.

---

### `shared/models/prior_auth.py`
**Does:** Pydantic models for the prior auth draft: `PriorAuthDraft`, `MissingItem`, `SupportingDoc`, `ClinicalJustification`, `ConfidenceLevel`.  
**Does NOT:** Generate content. Pure data containers.  
**Critical invariant:** `PriorAuthDraft.human_review_required` defaults to `True` and cannot be set to `False`.

---

## WHAT GOES WHERE — DECISION TREE

```
New functionality needed?
    │
    ├─ "Calls an external clinical API (NLM, OpenFDA)"
    │   └─ → mcp_server/tools/<new_tool>.py
    │
    ├─ "Manipulates FHIR data"
    │   └─ → a2a_agent/tools/fhir_reader.py
    │
    ├─ "Changes how Claude reasons about prior auth"
    │   └─ → a2a_agent/prompts/system.py
    │
    ├─ "New data field in the output"
    │   └─ → shared/models/prior_auth.py
    │
    ├─ "New HTTP endpoint"
    │   └─ → a2a_agent/main.py (route) + a2a_agent/task_handler.py (logic)
    │
    └─ "Cross-cutting (retry, logging, config)"
        └─ → mcp_server/http_client.py or a2a_agent/config.py
```
