# folderstructure.md — Annotated File Tree
> Every file has a purpose. Every directory has a clear owner.

---

```
authclear/
│
│  ──── ROOT DOCS (read these first) ────────────────────────────────────
├── CLAUDE.md              # Claude extension master config — start here
├── architecture.md        # System design, data flow, deployment
├── agents.md              # Agent behavior, tool specs, task lifecycle
├── sdd.md                 # Software Design Doc — models, contracts, tests
├── cot_react.md           # ReAct skeleton, prompt engineering, templates
├── folderstructure.md     # YOU ARE HERE
├── structure.md           # Module responsibilities summary
│
│  ──── MCP SERVER (Submission A: Path A) ───────────────────────────────
├── mcp_server/
│   ├── __init__.py
│   ├── server.py          # FastMCP app, tool registration, SSE transport
│   ├── config.py          # Pydantic Settings — NLM keys, cache TTLs, ports
│   ├── models.py          # Tool response Pydantic models (ICD10Resolution, etc.)
│   ├── cache.py           # TTLCache setup, cache_key helper, @cached decorator
│   ├── http_client.py     # httpx.AsyncClient factory with retry + timeout config
│   │
│   ├── tools/             # One file per tool — independently testable
│   │   ├── __init__.py    # Exports all 5 tool functions
│   │   ├── icd10.py       # resolve_icd10() → NLM VSAC ConceptMap API
│   │   ├── rxnorm.py      # lookup_rxnorm() + check_drug_interactions() → NLM RxNav
│   │   ├── loinc.py       # get_loinc_code() → FHIR LOINC terminology server
│   │   └── prior_auth.py  # get_prior_auth_criteria() → YAML data files
│   │
│   ├── data/              # Bundled reference data (no API calls needed)
│   │   └── criteria/      # Prior auth criteria YAML files (one per payer)
│   │       ├── generic.yaml
│   │       ├── medicare.yaml
│   │       ├── medicaid.yaml
│   │       ├── bcbs.yaml
│   │       ├── aetna.yaml
│   │       └── united.yaml
│   │
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py    # respx mock setup, NLM API fixtures
│       ├── test_icd10.py
│       ├── test_rxnorm.py
│       ├── test_loinc.py
│       └── test_prior_auth.py
│
│  ──── A2A AGENT (Submission B: Path B) ────────────────────────────────
├── a2a_agent/
│   ├── __init__.py
│   ├── main.py            # FastAPI app, route registration, lifespan hooks
│   ├── agent_card.py      # Builds AgentCard JSON — capabilities declaration
│   ├── task_handler.py    # POST /tasks/send handler — validates, dispatches
│   ├── task_store.py      # In-memory task store with TTL cleanup
│   ├── orchestrator.py    # ReAct loop with Claude API + tool dispatch
│   ├── config.py          # Pydantic Settings — ANTHROPIC_API_KEY, MCP_URL, etc.
│   ├── models.py          # Task, TaskState, TaskInput, SendTaskRequest/Response
│   │
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── fhir_reader.py # parse_fhir_bundle() → PatientBundle (pure, no I/O)
│   │   └── mcp_client.py  # MCPClient class — wraps MCP Server with retry
│   │
│   ├── prompts/
│   │   ├── __init__.py
│   │   ├── system.py      # build_system_prompt() — authoritative system prompt
│   │   └── prior_auth.py  # PRIOR_AUTH_LETTER_TEMPLATE — draft letter structure
│   │
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py    # FastAPI TestClient, MCP mock client, FHIR fixtures
│       ├── test_task_handler.py
│       ├── test_orchestrator.py
│       ├── test_fhir_reader.py
│       └── test_task_store.py
│
│  ──── SHARED (used by both services) ──────────────────────────────────
├── shared/
│   ├── __init__.py
│   ├── fhir/
│   │   └── synthetic_patients/     # 5 pre-built FHIR bundles (never real PHI)
│   │       ├── patient_t2dm_complete.json      # T2DM, all criteria met
│   │       ├── patient_t2dm_gaps.json          # T2DM, missing second trial
│   │       ├── patient_obesity_ozempic.json    # Obesity indication
│   │       ├── patient_rheumatoid_humira.json  # Biologic prior auth scenario
│   │       └── patient_cardiac_eliquis.json    # Anticoagulant scenario
│   │
│   └── models/
│       ├── __init__.py
│       ├── patient.py     # PatientBundle, PatientDemographics, Medication, LabResult
│       └── prior_auth.py  # PriorAuthDraft, MissingItem, SupportingDoc, ConfidenceLevel
│
│  ──── SCRIPTS ──────────────────────────────────────────────────────────
├── scripts/
│   ├── generate_patients.py   # Synthea CLI wrapper → generates FHIR bundles
│   ├── seed_hapi.py           # POSTs synthetic bundles to HAPI FHIR test server
│   └── validate_mcp.py        # End-to-end test: connects to MCP server, calls all tools
│
│  ──── DEPLOYMENT ────────────────────────────────────────────────────────
├── Dockerfile.mcp             # Multi-stage build for MCP server
├── Dockerfile.agent           # Multi-stage build for A2A agent
├── docker-compose.yml         # Local: runs both services + ngrok for Prompt Opinion
├── railway.toml               # Railway deployment config (2 services)
│
│  ──── PROJECT CONFIG ────────────────────────────────────────────────────
├── pyproject.toml             # Poetry config, all dependencies, tool versions
├── .env.example               # Template — copy to .env, never commit .env
├── .gitignore
├── pytest.ini                 # asyncio_mode=auto, testpaths, coverage config
└── README.md                  # Hackathon submission description + demo video link
```

---

## FILE SIZE EXPECTATIONS

| File | Lines (approx) | Note |
|---|---|---|
| `mcp_server/server.py` | 60-80 | Thin — just registers tools |
| `mcp_server/tools/icd10.py` | 80-100 | Tool + cache + HTTP call |
| `mcp_server/tools/rxnorm.py` | 120-150 | Two tools in one file |
| `a2a_agent/orchestrator.py` | 150-180 | Core ReAct loop |
| `a2a_agent/tools/fhir_reader.py` | 100-130 | Pure parser |
| `shared/models/prior_auth.py` | 80-100 | All Pydantic models |
| Each test file | 60-120 | ~8-12 test functions per file |

---

## IMPORT CONVENTIONS

```python
# Standard lib first
from __future__ import annotations
import asyncio
import json
from datetime import datetime

# Third party
import httpx
import structlog
from pydantic import BaseModel

# Internal — always use full path from project root
from mcp_server.tools.rxnorm import lookup_rxnorm
from shared.models.patient import PatientBundle
from a2a_agent.tools.mcp_client import MCPClient
```

---

## NAMING CONVENTIONS

| Thing | Convention | Example |
|---|---|---|
| Files | `snake_case.py` | `task_handler.py` |
| Classes | `PascalCase` | `PriorAuthDraft` |
| Functions | `snake_case` | `resolve_icd10` |
| Constants | `SCREAMING_SNAKE` | `MAX_ITERATIONS` |
| Test functions | `test_<unit>_<scenario>_<expected>` | `test_resolve_icd10_unknown_code_returns_error` |
| Env vars | `SCREAMING_SNAKE` | `MCP_SERVER_URL` |
| YAML criteria keys | `snake_case` | `required_diagnoses` |
