# CLAUDE.md — AuthClear: Prior Auth Copilot + FHIR Terminology Engine
> **Hackathon:** Agents Assemble — Healthcare AI Endgame (Prompt Opinion / Darena Health)
> **Deadline:** May 11, 2026 @ 11:59 PM ET
> **Solo dev** | Python | FastMCP | FastAPI | AWS Bedrock (Claude 3 Haiku) | Railway

---

## 🧠 PROJECT IDENTITY

**AuthClear** is a dual-submission healthcare AI system:

| Submission | Path | What It Is |
|---|---|---|
| `authclear-terminology` | Path A — MCP Server | FHIR clinical terminology resolution engine |
| `authclear-agent` | Path B — A2A Agent | Prior authorization copilot for physicians |

The MCP Server is the **infrastructure layer**. The A2A Agent **consumes** the MCP Server as a tool. Both are published independently to the Prompt Opinion Marketplace.

---

## 🏗️ ARCHITECTURE SUMMARY

```
[Physician / Synthetic EHR Input]
        │
        ▼
[A2A Prior Auth Agent]  ◄─────────────────────────────────────┐
  ├─ Reads patient FHIR bundle                                 │
  ├─ Identifies prior auth triggers                            │ MCP tool calls
  ├─ Extracts clinical justification                           │
  └─ Generates structured auth draft                           │
        │                                                      │
        ▼                                                      │
[FHIR Terminology MCP Server] ────────────────────────────────┘
  ├─ resolve_icd10(code) → SNOMED + description
  ├─ lookup_rxnorm(drug_name) → RxNorm ID + drug class
  ├─ check_drug_interactions(rxnorm_ids[]) → interactions[]
  ├─ get_loinc_code(test_name) → LOINC code + unit
  └─ get_prior_auth_criteria(cpt_code, payer) → criteria{}
        │
        ▼
[Public APIs: NIH NLM RxNav | OpenFDA | FHIR R4 | HAPI Test Server]
```

**Human-in-the-loop always**: The agent generates drafts. A physician reviews and submits. No auto-approval. No auto-denial. This is architecturally compliant with Texas SB 490, Arizona HB 2417, and Maryland HB 1174.

---

## 🗂️ CODEBASE MAP

```
authclear/
├── CLAUDE.md                    ← YOU ARE HERE
├── architecture.md              ← Full system design
├── agents.md                    ← Agent behavior specs
├── sdd.md                       ← Software Design Document
├── folderstructure.md           ← Annotated file tree
├── structure.md                 ← Module responsibilities
├── cot_react.md                 ← CoT/ReAct reasoning patterns
│
├── mcp_server/                  ← Path A submission
│   ├── server.py                ← FastMCP entrypoint
│   ├── config.py                ← Settings via pydantic-settings
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── icd10.py             ← resolve_icd10 tool
│   │   ├── rxnorm.py            ← lookup_rxnorm + check_interactions
│   │   ├── loinc.py             ← get_loinc_code tool
│   │   └── prior_auth.py        ← get_prior_auth_criteria tool
│   └── tests/
│       ├── test_icd10.py
│       ├── test_rxnorm.py
│       ├── test_loinc.py
│       └── test_prior_auth.py
│
├── a2a_agent/                   ← Path B submission
│   ├── main.py                  ← FastAPI entrypoint
│   ├── agent_card.py            ← /.well-known/agent.json
│   ├── task_handler.py          ← tasks/send handler
│   ├── orchestrator.py          ← ReAct loop + Claude API
│   ├── claude_client.py         ← Unified client (Anthropic + Bedrock)
│   ├── config.py
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── fhir_reader.py       ← Read patient FHIR bundle
│   │   └── mcp_client.py        ← Call MCP Server tools
│   ├── prompts/
│   │   ├── system.py            ← System prompt template
│   │   └── prior_auth.py        ← Prior auth draft template
│   └── tests/
│       ├── test_task_handler.py
│       ├── test_orchestrator.py
│       └── test_fhir_reader.py
│
├── web_ui/                      ← Web interface
│   ├── index.html               ← Patient selection UI
│   └── app.js                   ← Frontend logic (hybrid mode)
│
├── shared/
│   ├── fhir/
│   │   └── synthetic_patients/  ← 9 synthetic FHIR bundles (JSON)
│   └── models/
│       ├── patient.py           ← Pydantic FHIR patient models
│       └── prior_auth.py        ← PriorAuthRequest / PriorAuthDraft models
│
├── scripts/
│   ├── generate_patients.py     ← Synthea wrapper
│   └── seed_hapi.py             ← Upload bundles to HAPI test server
│
├── .env.example
├── pyproject.toml
├── Dockerfile.mcp
├── Dockerfile.agent
├── docker-compose.yml
├── railway.toml
└── README.md
```

---

## ⚙️ ENVIRONMENT VARIABLES

```bash
# .env (never commit)

# === CLAUDE PROVIDER ===
CLAUDE_PROVIDER=bedrock  # "anthropic" or "bedrock"

# === ANTHROPIC API (if CLAUDE_PROVIDER=anthropic) ===
ANTHROPIC_API_KEY=sk-ant-...

# === AWS BEDROCK (if CLAUDE_PROVIDER=bedrock) ===
AWS_REGION=us-east-1
AWS_BEDROCK_MODEL=anthropic.claude-3-haiku-20240307-v1:0
AWS_ACCESS_KEY_ID=AKIAXXXX              # Optional if using ~/.aws/credentials
AWS_SECRET_ACCESS_KEY=XXXX              # Optional

# === SERVERS ===
PORT_MCP=8001
PORT_AGENT=8000
MCP_SERVER_URL=http://localhost:8001          # local dev
MCP_SERVER_URL_PROD=https://...railway.app   # production

# === FHIR ===
HAPI_FHIR_BASE=https://hapi.fhir.org/baseR4

# === LOGGING ===
LOG_LEVEL=INFO
ENVIRONMENT=development
```

---

## 🔑 KEY TECHNICAL DECISIONS

| Decision | Choice | Reason |
|---|---|---|
| MCP framework | `fastmcp>=2.0` + HTTP wrapper | FastMCP stdio + run_mcp_http_server.py for REST API |
| LLM Provider | AWS Bedrock (fallback: Anthropic) | Claude 3 Haiku for cost-effective clinical reasoning |
| LLM Model | `claude-3-haiku-20240307-v1:0` | Fast, accurate, Bedrock on-demand availability |
| A2A framework | Raw FastAPI | Full control over agent card + task lifecycle |
| FHIR data | `fhir.resources` + HAPI public | No PHI, no auth required, 9 synthetic patients |
| Payer criteria | Hardcoded YAML (6 payers, 11 drugs) | Scope-limited; real system would call CoverMyMeds API |
| Web UI | Flask + Vanilla JS | Hybrid mode: real backend + simulated fallback |
| Async | Full `asyncio` + `httpx.AsyncClient` | All external calls are I/O bound |
| Testing | `pytest` + `pytest-asyncio` + `respx` | Mock all external APIs; no real network in CI |

---

## 🧪 TESTING CONTRACT

**All tests must pass before any feature is considered done.**

```bash
# Run everything
pytest --tb=short -q

# Run by module
pytest mcp_server/tests/ -v
pytest a2a_agent/tests/ -v

# Coverage (target: >85%)
pytest --cov=mcp_server --cov=a2a_agent --cov-report=term-missing
```

**Test naming convention:** `test_<function>_<scenario>_<expected>`  
Example: `test_lookup_rxnorm_valid_drug_returns_rxnorm_id`

---

## 🚀 DEPLOY CHECKLIST

### MCP Server (Railway service 1)
- [ ] `Dockerfile.mcp` builds cleanly
- [ ] `railway.toml` sets `PORT=8001`
- [ ] SSE endpoint live at `/sse`
- [ ] Health check at `/health` returns `{"status": "ok"}`
- [ ] Published to Prompt Opinion Marketplace with correct `mcp_url`

### A2A Agent (Railway service 2)
- [ ] `Dockerfile.agent` builds cleanly
- [ ] `/.well-known/agent.json` returns valid AgentCard
- [ ] `POST /tasks/send` returns A2A task response
- [ ] `MCP_SERVER_URL` points to production MCP service
- [ ] Published to Prompt Opinion Marketplace

---

## 📋 WORKFLOW FOR CLAUDE EXTENSION

When working on this project, always:

1. **Read the relevant spec file first** before generating code  
   (`sdd.md` → `agents.md` → then code)

2. **Follow ReAct skeleton in `cot_react.md`** for any agent logic

3. **Write the test first**, then the implementation (TDD)

4. **All external HTTP calls go through `httpx.AsyncClient`** with:
   - Timeout: 10s connect, 30s read
   - Retry: 3 attempts with exponential backoff
   - Mocked in tests via `respx`

5. **No hardcoded strings** — all config in `config.py` via `pydantic-settings`

6. **Type annotations on every function** — use `from __future__ import annotations`

7. **Docstrings on every public function** — Google style

8. **Log everything** — `structlog` with JSON output in production

---

## 🎯 JUDGING CRITERIA MAPPING

| Criterion | How We Win |
|---|---|
| **AI Factor** | Claude reasons over ambiguous clinical text → maps to structured codes. Rule-based is impossible here. |
| **Potential Impact** | 43 prior auth requests/physician/week × 12h staff time → measurable ROI demo |
| **Feasibility** | Human-in-the-loop, synthetic data only, regulatory compliance built in from day 1 |

---

## 🛑 HARD CONSTRAINTS (NEVER VIOLATE)

- ❌ No real PHI — all patient data is synthetic/de-identified
- ❌ No auto-approval or auto-denial of prior auth
- ❌ No hardcoded API keys in source
- ❌ No blocking I/O in async functions (use `await` everywhere)
- ✅ Every tool must have error handling + fallback message
- ✅ Every endpoint must validate input with Pydantic v2
- ✅ All tests must pass green before shipping

---

## 📊 CURRENT PROJECT STATUS (March 31, 2026)

### **✅ IMPLEMENTED & WORKING:**

**Backend:**
- ✅ MCP Server with HTTP wrapper (`run_mcp_http_server.py`)
- ✅ A2A Agent with FastAPI (`run_a2a_agent.py`)
- ✅ AWS Bedrock integration (`a2a_agent/claude_client.py`)
- ✅ Claude 3 Haiku configured and tested
- ✅ Orchestrator with ReAct loop
- ✅ FHIR parser (extracts 9 resource types)
- ✅ MCP client with 5 tools working
- ✅ Task store with TTL cleanup

**Frontend:**
- ✅ Web UI with Flask (`run_web_server.py`)
- ✅ Hybrid mode (real backend + simulated fallback)
- ✅ Patient selection dropdown (9 patients)
- ✅ Animated processing workflow
- ✅ Results display with confidence scores

**Data:**
- ✅ 9 synthetic FHIR bundles:
  - Maria González (T2DM complete)
  - John Smith (T2DM gaps)
  - Sarah Johnson (RA)
  - Robert Chen (Obesity)
  - William Martinez (AFib)
  - Juan Pérez (Hypertension)
  - Linda Thompson (HER2+ breast cancer)
  - Richard Davis (Severe COPD)
  - Angela Rodriguez (Lupus/SLE)
- ✅ 11 CPT/HCPCS codes with prior auth criteria:
  - J0173 (Ozempic), J1438 (Enbrel), J1745 (Remicade)
  - J2323 (Tysabri), J0897 (Prolia)
  - J9355 (Herceptin), J9299 (Opdivo), J9035 (Avastin), J9271 (Keytruda)
  - J7637 (Spiriva), J0490 (Benlysta)
- ✅ 6 payers: generic, bcbs, medicare, medicaid, aetna, united

**Tools & Utilities:**
- ✅ `test_real_backend.py` - End-to-end validation
- ✅ `test_integration.py` - Integration tests
- ✅ Video assets (HTML cards for demo)

### **🔄 HOW TO RUN:**

```bash
# Terminal 1: MCP Server
python run_mcp_http_server.py  # Port 8001

# Terminal 2: A2A Agent
python run_a2a_agent.py         # Port 8000

# Terminal 3: Web UI
python run_web_server.py        # Port 3000 → Opens browser

# Test real backend
python test_real_backend.py
```

### **✅ VALIDATED WORKFLOW:**

1. User selects patient (e.g., Richard Davis - COPD)
2. User selects medication (e.g., Spiriva)
3. User clicks "Process Prior Authorization"
4. System:
   - Loads FHIR bundle (9 resources)
   - Calls MCP Server (ICD-10, RxNorm, LOINC, prior auth criteria)
   - Claude reasoning via Bedrock (10-30s)
   - Generates PriorAuthDraft
   - Returns confidence score (e.g., 92% HIGH)
5. Physician reviews draft
6. Draft ready for submission

### **📈 PERFORMANCE METRICS (Observed):**

- Web UI response time: <1s (simulated) | 10-30s (real backend)
- Bedrock Claude 3 Haiku latency: ~15s average for complex cases
- MCP Server health check: <100ms
- FHIR bundle parsing: <200ms for 9 resources
- Confidence scores: 50-95% depending on documentation completeness

### **🎬 VIDEO DEMO PLAN:**

- Scene 1: Title card (30s)
- Scene 2: Architecture diagram (20s)
- Scene 3: Web UI demo with Richard Davis COPD case (40s)
- Scene 4: Compliance + ROI (25s)
- **Total:** <3 minutes

---

## 🚀 DEPLOYMENT READINESS

**Railway:**
- ✅ Dockerfile.mcp ready
- ✅ Dockerfile.agent ready
- ✅ railway.toml configured
- ✅ Environment variables documented

**Production Checklist:**
- ✅ Bedrock credentials configured
- ✅ Health checks on all services
- ✅ CORS configured for Web UI
- ✅ Human-in-the-loop enforced
- ✅ Pydantic validation on all inputs
- ⚠️  Rate limiting not implemented (add if deploying publicly)
- ⚠️  Authentication not implemented (add if deploying publicly)
