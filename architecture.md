# architecture.md — AuthClear System Architecture
> Version: 1.0 | Stack: Python 3.12 | FastMCP 2.x | FastAPI | Anthropic Claude

---

## 1. SYSTEM OVERVIEW

AuthClear consists of two independent but interoperable services published to the Prompt Opinion Marketplace.

```
┌─────────────────────────────────────────────────────────────────────┐
│                      PROMPT OPINION PLATFORM                         │
│                                                                       │
│   ┌──────────────────────────┐    ┌──────────────────────────────┐   │
│   │   authclear-terminology  │    │      authclear-agent          │   │
│   │   (Path A: MCP Server)   │◄───│   (Path B: A2A Agent)        │   │
│   │                          │    │                              │   │
│   │  Tools:                  │    │  Capabilities:               │   │
│   │  • resolve_icd10         │    │  • Read FHIR patient bundle  │   │
│   │  • lookup_rxnorm         │    │  • Identify auth triggers    │   │
│   │  • check_drug_interactions│   │  • Extract clinical docs     │   │
│   │  • get_loinc_code        │    │  • Generate auth draft       │   │
│   │  • get_prior_auth_criteria│   │  • Human review handoff      │   │
│   └──────────┬───────────────┘    └──────────────────────────────┘   │
└──────────────┼─────────────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        PUBLIC APIs (NO PHI)                          │
│                                                                       │
│  NIH NLM RxNav API          OpenFDA API         HAPI FHIR R4        │
│  rxnav.nlm.nih.gov          api.fda.gov         hapi.fhir.org       │
│  • Drug lookups             • Drug interactions  • Patient bundles   │
│  • RxNorm IDs               • Adverse events     • Clinical data     │
│                                                                       │
│  VSAC (NLM Terminology)                                              │
│  cts.nlm.nih.gov                                                     │
│  • ICD-10 → SNOMED                                                   │
│  • LOINC codes                                                        │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. MCP SERVER ARCHITECTURE (Path A)

### 2.1 Transport & Protocol
- **Framework:** `fastmcp>=2.0`
- **Transport:** SSE (Server-Sent Events) — required by Prompt Opinion
- **Protocol:** MCP 2024-11-05
- **Endpoint:** `GET /sse` (SSE stream), `POST /messages` (message relay)

### 2.2 Tool Definitions

```python
# Tool contract — each tool is independently testable

@mcp.tool()
async def resolve_icd10(code: str) -> dict:
    """
    Resolve an ICD-10-CM code to SNOMED CT equivalent.
    
    Args:
        code: ICD-10-CM code (e.g., "E11.9")
    
    Returns:
        {
            "icd10_code": "E11.9",
            "description": "Type 2 diabetes mellitus without complications",
            "snomed_code": "44054006",
            "snomed_description": "Diabetes mellitus type 2",
            "category": "Endocrine, nutritional and metabolic diseases"
        }
    """

@mcp.tool()
async def lookup_rxnorm(drug_name: str) -> dict:
    """
    Look up a drug by name and return RxNorm ID + drug class.
    
    Args:
        drug_name: Common or brand name (e.g., "Ozempic", "semaglutide")
    
    Returns:
        {
            "rxnorm_id": "2200660",
            "generic_name": "semaglutide",
            "brand_names": ["Ozempic", "Wegovy", "Rybelsus"],
            "drug_class": "Glucagon-like peptide-1 receptor agonist",
            "requires_prior_auth": true,  # common knowledge, not payer-specific
            "typical_indications": ["Type 2 diabetes", "Obesity"]
        }
    """

@mcp.tool()
async def check_drug_interactions(rxnorm_ids: list[str]) -> dict:
    """
    Check interactions between a list of drugs by RxNorm ID.
    
    Args:
        rxnorm_ids: List of RxNorm IDs (e.g., ["2200660", "1049502"])
    
    Returns:
        {
            "interactions": [
                {
                    "drug_1": "semaglutide",
                    "drug_2": "insulin glargine", 
                    "severity": "moderate",
                    "description": "Concurrent use may increase hypoglycemia risk",
                    "recommendation": "Monitor blood glucose closely"
                }
            ],
            "total_interactions": 1
        }
    """

@mcp.tool()
async def get_loinc_code(test_name: str) -> dict:
    """
    Look up LOINC code for a laboratory test or clinical observation.
    
    Args:
        test_name: Common test name (e.g., "HbA1c", "fasting glucose")
    
    Returns:
        {
            "loinc_code": "4548-4",
            "long_name": "Hemoglobin A1c/Hemoglobin.total in Blood",
            "short_name": "Hgb A1c MFr Bld",
            "unit": "%",
            "component": "Hemoglobin A1c",
            "property": "MFr",
            "system": "Bld"
        }
    """

@mcp.tool()
async def get_prior_auth_criteria(cpt_code: str, payer: str = "generic") -> dict:
    """
    Get prior authorization clinical criteria for a procedure/drug.
    
    Args:
        cpt_code: CPT or HCPCS code (e.g., "J0173" for semaglutide injection)
        payer: Payer name — one of: generic, medicare, medicaid, bcbs, aetna, united
    
    Returns:
        {
            "cpt_code": "J0173",
            "description": "Injection, semaglutide, 0.01 mg",
            "payer": "generic",
            "criteria": {
                "required_diagnoses": ["E11", "E66"],
                "required_labs": ["HbA1c >= 7.5%", "BMI >= 30 for obesity indication"],
                "required_trials": ["Metformin (unless contraindicated)", "1 other oral agent"],
                "documentation_required": [
                    "Current HbA1c within 90 days",
                    "BMI documentation",
                    "Previous medication trial records",
                    "Prescriber attestation of medical necessity"
                ],
                "typical_approval_duration": "1 year with renewal"
            }
        }
    """
```

### 2.3 HTTP Client Strategy

```
Tool called
    │
    ▼
Check in-memory cache (TTL: 1h for stable codes, 5min for interactions)
    │
    ├─ HIT → return cached result
    │
    └─ MISS → httpx.AsyncClient (10s connect timeout, 30s read timeout)
                    │
                    ├─ Success → cache + return
                    │
                    └─ Error → retry(3, exponential backoff)
                                    │
                                    ├─ Success → cache + return
                                    └─ Max retries exceeded → structured error response
```

---

## 3. A2A AGENT ARCHITECTURE (Path B)

### 3.1 A2A Protocol Compliance

```
GET  /.well-known/agent.json       → AgentCard (capabilities declaration)
POST /tasks/send                   → Start/continue task
GET  /tasks/{task_id}              → Task status + result
POST /tasks/{task_id}/cancel       → Cancel in-flight task
```

### 3.2 AgentCard Shape

```json
{
  "name": "AuthClear Prior Auth Copilot",
  "description": "Reads a patient FHIR bundle and generates a complete prior authorization request package for physician review. Human-in-the-loop: never auto-approves or auto-denies.",
  "version": "1.0.0",
  "url": "https://authclear-agent.railway.app",
  "capabilities": {
    "streaming": false,
    "pushNotifications": false,
    "stateTransitionHistory": true
  },
  "defaultInputModes": ["application/json"],
  "defaultOutputModes": ["application/json"],
  "skills": [
    {
      "id": "prior_auth_package",
      "name": "Generate Prior Auth Package",
      "description": "Given a FHIR patient bundle and a drug/procedure, produces a complete prior auth submission package",
      "inputSchema": {
        "type": "object",
        "required": ["fhir_bundle", "requested_item"],
        "properties": {
          "fhir_bundle": {"type": "object", "description": "FHIR R4 Patient Bundle"},
          "requested_item": {"type": "string", "description": "Drug name, CPT code, or procedure description"},
          "payer": {"type": "string", "description": "Payer name (optional, defaults to generic)"}
        }
      }
    }
  ]
}
```

### 3.3 ReAct Orchestration Loop

```
Input: { fhir_bundle, requested_item, payer }
    │
    ▼
┌── THOUGHT 1: Parse patient context ──────────────────────────────────┐
│   - Extract: diagnoses (ICD-10), medications (RxNorm), labs (LOINC)  │
│   - Identify: patient demographics, relevant history                  │
└──────────────────────────────────────────────────────────────────────┘
    │
    ▼
┌── ACTION 1: resolve_icd10(primary_diagnosis) ────────────────────────┐
│   → Get SNOMED equivalent for diagnosis validation                    │
└──────────────────────────────────────────────────────────────────────┘
    │
    ▼
┌── ACTION 2: lookup_rxnorm(requested_item) ───────────────────────────┐
│   → Get RxNorm ID, drug class, typical indications                   │
└──────────────────────────────────────────────────────────────────────┘
    │
    ▼
┌── ACTION 3: check_drug_interactions(current_meds + requested_drug) ──┐
│   → Identify any safety concerns to document                          │
└──────────────────────────────────────────────────────────────────────┘
    │
    ▼
┌── ACTION 4: get_prior_auth_criteria(cpt_code, payer) ────────────────┐
│   → Get exact documentation requirements                              │
└──────────────────────────────────────────────────────────────────────┘
    │
    ▼
┌── THOUGHT 2: Gap analysis ────────────────────────────────────────────┐
│   - Compare: what criteria requires vs. what patient record has       │
│   - Identify: missing documentation, labs out of date, gaps          │
└──────────────────────────────────────────────────────────────────────┘
    │
    ▼
┌── ACTION 5: generate_prior_auth_draft (internal, no MCP call) ───────┐
│   - Produce structured JSON + human-readable narrative                │
│   - Flag missing items for physician attention                        │
│   - Include confidence score per section                              │
└──────────────────────────────────────────────────────────────────────┘
    │
    ▼
Output: PriorAuthDraft {
    patient_summary,
    requested_item_details,
    clinical_justification,
    supporting_documentation,
    missing_items[],          ← what physician still needs to provide
    draft_letter,             ← ready-to-send narrative
    confidence_score,
    human_review_required: true  ← ALWAYS
}
```

---

## 4. DATA FLOW — COMPLETE SCENARIO

**Input:** Synthetic patient Maria González, T2DM, physician wants to prescribe Ozempic

```
1. Physician pastes FHIR bundle into Prompt Opinion UI
2. Platform sends POST /tasks/send to authclear-agent
3. Agent parses FHIR → extracts:
   - Diagnoses: [E11.9, E11.65]
   - Current meds: [Metformin 1000mg, Lisinopril 10mg]
   - Recent labs: [HbA1c 8.2% (90d ago), BMI 32]
   
4. Agent calls MCP Server:
   a. resolve_icd10("E11.9") → "Type 2 DM without complications" / SNOMED 44054006
   b. lookup_rxnorm("Ozempic") → RxNorm 2200660, GLP-1 agonist, requires_pa=true
   c. check_drug_interactions(["2200660", "860974"]) → moderate interaction w/ Metformin (hypoglycemia)
   d. get_prior_auth_criteria("J0173", "generic") → requires: HbA1c>=7.5, metformin trial, BMI doc

5. Agent runs gap analysis:
   ✅ HbA1c 8.2% (>7.5% threshold met, within 90 days)
   ✅ Metformin trial documented (current medication)
   ✅ BMI 32 documented
   ⚠️  Missing: second oral agent trial (criteria requires 1 more)
   ⚠️  Missing: prescriber attestation of medical necessity

6. Agent generates draft:
   - Clinical justification narrative
   - Documentation checklist (what's ready vs. missing)
   - Draft letter ready for physician to review and sign
   - Confidence: 78% (missing items flagged)

7. Returns PriorAuthDraft to Prompt Opinion UI
8. Physician reviews, fills gaps, submits to payer
```

---

## 5. DEPLOYMENT ARCHITECTURE

```
Railway.app
├── Service: authclear-mcp
│   ├── Docker: Dockerfile.mcp
│   ├── Port: 8001
│   ├── Start: fastmcp run mcp_server/server.py --transport sse --port 8001
│   └── Health: GET /health
│
└── Service: authclear-agent
    ├── Docker: Dockerfile.agent
    ├── Port: 8000
    ├── Start: uvicorn a2a_agent.main:app --host 0.0.0.0 --port 8000
    ├── Env: MCP_SERVER_URL=https://authclear-mcp.railway.app
    └── Health: GET /health
```

---

## 6. SECURITY & COMPLIANCE

| Concern | Mitigation |
|---|---|
| PHI exposure | 100% synthetic data (Synthea-generated) — HAPI public server |
| API key leakage | Env vars via Railway secrets, never in code |
| LLM hallucination | All clinical codes validated against authoritative APIs |
| Auto-decision risk | `human_review_required: true` hardcoded in all outputs |
| Rate limiting | httpx retry with backoff; in-memory cache for repeated lookups |
| Regulatory (TX/AZ/MD) | Human-in-the-loop architecture; no automated PA decisions |

---

## 7. PERFORMANCE TARGETS

| Metric | Target | How |
|---|---|---|
| MCP tool response | < 2s (p95) | In-memory cache (TTL 1h) |
| A2A task completion | < 30s | Parallel MCP calls (asyncio.gather) |
| Test suite runtime | < 60s | All external calls mocked |
| Docker build time | < 3 min | Multi-stage + pip cache layer |
