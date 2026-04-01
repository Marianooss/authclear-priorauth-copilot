# sdd.md — Software Design Document
> AuthClear v1.0 | Healthcare Prior Auth Copilot + FHIR Terminology Engine  
> Pattern: SDD (Software Design Document) | Methodology: TDD + CoT/ReAct

---

## 1. PURPOSE & SCOPE

This document defines the technical design for AuthClear — a dual-submission healthcare AI system for the "Agents Assemble" hackathon. It is the authoritative reference for:
- Module responsibilities
- Data models (Pydantic v2)
- Interface contracts
- Error handling patterns
- Testing specifications

---

## 2. PYDANTIC DATA MODELS

### 2.1 Shared Models (`shared/models/`)

```python
# shared/models/patient.py
from __future__ import annotations
from pydantic import BaseModel, Field
from datetime import date, datetime


class PatientDemographics(BaseModel):
    id: str
    name: str
    birth_date: date
    gender: str
    npi: str | None = None


class Diagnosis(BaseModel):
    icd10_code: str
    description: str
    onset_date: date | None = None
    status: str = "active"  # active | resolved | chronic


class Medication(BaseModel):
    name: str
    rxnorm_id: str | None = None
    dose: str
    frequency: str
    start_date: date | None = None
    status: str = "active"


class LabResult(BaseModel):
    test_name: str
    loinc_code: str | None = None
    value: float
    unit: str
    reference_range: str | None = None
    date: date
    is_critical: bool = False


class PatientBundle(BaseModel):
    """Parsed FHIR R4 Patient Bundle — synthetic data only."""
    patient: PatientDemographics
    diagnoses: list[Diagnosis] = Field(default_factory=list)
    medications: list[Medication] = Field(default_factory=list)
    lab_results: list[LabResult] = Field(default_factory=list)
    allergies: list[str] = Field(default_factory=list)
    raw_fhir: dict = Field(default_factory=dict)
```

```python
# shared/models/prior_auth.py
from __future__ import annotations
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class ConfidenceLevel(str, Enum):
    HIGH = "high"        # >= 0.90
    MEDIUM = "medium"    # >= 0.70
    LOW = "low"          # >= 0.50
    INSUFFICIENT = "insufficient"  # < 0.50


class SupportingDoc(BaseModel):
    doc_type: str          # lab_result | medication_history | clinical_note
    description: str
    date: str
    status: str            # present | missing | outdated
    value: str | None = None


class MissingItem(BaseModel):
    item: str
    reason: str
    required_by: str       # payer criterion reference
    suggestion: str        # what physician should do


class PatientSummary(BaseModel):
    patient_name: str
    patient_id: str
    primary_diagnosis: str
    icd10_code: str
    snomed_code: str | None = None
    relevant_labs: list[LabResult] = Field(default_factory=list)
    current_medications: list[str] = Field(default_factory=list)


class RequestedItemDetails(BaseModel):
    item_name: str
    rxnorm_id: str | None = None
    drug_class: str | None = None
    cpt_hcpcs_code: str | None = None
    typical_indications: list[str] = Field(default_factory=list)
    interactions_flagged: list[dict] = Field(default_factory=list)


class ClinicalJustification(BaseModel):
    diagnosis_meets_criteria: bool
    criteria_satisfied: list[str]
    criteria_not_satisfied: list[str]
    narrative: str                    # Human-readable justification


class PriorAuthDraft(BaseModel):
    task_id: str
    patient_summary: PatientSummary
    requested_item_details: RequestedItemDetails
    clinical_justification: ClinicalJustification
    supporting_documentation: list[SupportingDoc] = Field(default_factory=list)
    missing_items: list[MissingItem] = Field(default_factory=list)
    draft_letter: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    confidence_level: ConfidenceLevel
    human_review_required: bool = True    # ALWAYS True — hardcoded
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    model_version: str = "claude-sonnet-4-20250514"
    warnings: list[str] = Field(default_factory=list)
```

### 2.2 MCP Tool Response Models

```python
# mcp_server/models.py
from pydantic import BaseModel


class ICD10Resolution(BaseModel):
    icd10_code: str
    description: str
    snomed_code: str | None = None
    snomed_description: str | None = None
    category: str | None = None
    error: str | None = None


class RxNormLookup(BaseModel):
    rxnorm_id: str | None = None
    generic_name: str
    brand_names: list[str] = []
    drug_class: str | None = None
    requires_prior_auth: bool = False
    typical_indications: list[str] = []
    error: str | None = None


class DrugInteraction(BaseModel):
    drug_1: str
    drug_2: str
    severity: str          # none | minor | moderate | major | contraindicated
    description: str
    recommendation: str


class DrugInteractionCheck(BaseModel):
    interactions: list[DrugInteraction] = []
    total_interactions: int = 0
    error: str | None = None


class LOINCCode(BaseModel):
    loinc_code: str | None = None
    long_name: str | None = None
    short_name: str | None = None
    unit: str | None = None
    component: str | None = None
    error: str | None = None


class PriorAuthCriteria(BaseModel):
    cpt_code: str
    description: str
    payer: str
    required_diagnoses: list[str] = []
    required_labs: list[str] = []
    required_trials: list[str] = []
    documentation_required: list[str] = []
    typical_approval_duration: str | None = None
    error: str | None = None
```

### 2.3 A2A Task Models

```python
# a2a_agent/models.py
from __future__ import annotations
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
from shared.models.prior_auth import PriorAuthDraft


class TaskState(str, Enum):
    SUBMITTED = "submitted"
    WORKING = "working"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"
    NEEDS_CLARIFICATION = "needs_clarification"


class TaskInput(BaseModel):
    fhir_bundle: dict
    requested_item: str
    payer: str = "generic"
    urgency: str = "standard"
    submitter_npi: str | None = None
    additional_context: str | None = None   # For multi-turn continuation


class TaskMessage(BaseModel):
    role: str   # user | agent
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Task(BaseModel):
    id: str
    state: TaskState = TaskState.SUBMITTED
    input: TaskInput
    messages: list[TaskMessage] = Field(default_factory=list)
    result: PriorAuthDraft | None = None
    error: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime  # created_at + 24h


class SendTaskRequest(BaseModel):
    """POST /tasks/send body"""
    id: str | None = None      # None = new task, str = continue existing
    message: TaskMessage


class SendTaskResponse(BaseModel):
    """POST /tasks/send response"""
    task: Task
```

---

## 3. MODULE INTERFACE CONTRACTS

### 3.1 MCP Server Modules

```python
# mcp_server/tools/icd10.py
async def resolve_icd10(code: str) -> ICD10Resolution:
    """
    Calls NLM VSAC/UMLS API to resolve ICD-10-CM → SNOMED CT.
    
    External API: https://cts.nlm.nih.gov/fhir/ConceptMap
    Cache TTL: 3600s (codes are stable)
    Test mock: respx fixture `mock_icd10_response`
    
    Raises:
        httpx.TimeoutException: Caught internally, returns error model
        httpx.HTTPStatusError: Caught internally, returns error model
    """

# mcp_server/tools/rxnorm.py
async def lookup_rxnorm(drug_name: str) -> RxNormLookup:
    """
    Calls NLM RxNav API to find drug by name.
    
    External API: https://rxnav.nlm.nih.gov/REST/drugs.json
    Cache TTL: 3600s
    Test mock: respx fixture `mock_rxnorm_response`
    """

async def check_drug_interactions(rxnorm_ids: list[str]) -> DrugInteractionCheck:
    """
    Calls NLM RxNav interaction API.
    
    External API: https://rxnav.nlm.nih.gov/REST/interaction/list.json
    Cache TTL: 300s
    Min inputs: 2 RxNorm IDs (returns empty if < 2)
    """

# mcp_server/tools/loinc.py
async def get_loinc_code(test_name: str) -> LOINCCode:
    """
    Calls FHIR R4 LOINC terminology server.
    
    External API: https://fhir.loinc.org/CodeSystem/$lookup
    Cache TTL: 3600s
    Fallback: NLM LOINC search API
    """

# mcp_server/tools/prior_auth.py
async def get_prior_auth_criteria(cpt_code: str, payer: str = "generic") -> PriorAuthCriteria:
    """
    Loads from bundled YAML criteria database (no external API).
    
    Source: mcp_server/data/criteria/{payer}.yaml
    Supported payers: generic, medicare, medicaid, bcbs, aetna, united
    Fallback: generic if payer not found
    Cache TTL: infinite (in-memory, loaded at startup)
    """
```

### 3.2 A2A Agent Modules

```python
# a2a_agent/task_handler.py
async def handle_send_task(request: SendTaskRequest) -> SendTaskResponse:
    """
    Main task entry point. Validates input, creates/retrieves task, 
    triggers orchestrator, returns updated task.
    
    New task: id=None → generate UUID, state=submitted → working
    Existing task: id=str → retrieve from store, append context
    """

# a2a_agent/orchestrator.py
async def run_prior_auth_orchestration(task: Task) -> PriorAuthDraft:
    """
    Core ReAct loop. Calls Claude API with tools. Returns completed draft.
    
    Max iterations: 10 tool calls (prevents runaway loops)
    Timeout: 60s total
    On error: returns partial draft with error flags
    """

# a2a_agent/tools/fhir_reader.py
def parse_fhir_bundle(raw_bundle: dict) -> PatientBundle:
    """
    Parses FHIR R4 Bundle JSON into PatientBundle model.
    
    Handles: Patient, Condition, MedicationRequest, Observation resources
    Error: raises FHIRParseError with field-level detail
    Does NOT make external calls — pure parsing
    """

# a2a_agent/tools/mcp_client.py
class MCPClient:
    """
    Async client for the FHIR Terminology MCP Server.
    Wraps all 5 tools as typed async methods.
    Uses httpx.AsyncClient with retry logic.
    """
    async def resolve_icd10(self, code: str) -> ICD10Resolution: ...
    async def lookup_rxnorm(self, drug_name: str) -> RxNormLookup: ...
    async def check_drug_interactions(self, rxnorm_ids: list[str]) -> DrugInteractionCheck: ...
    async def get_loinc_code(self, test_name: str) -> LOINCCode: ...
    async def get_prior_auth_criteria(self, cpt_code: str, payer: str) -> PriorAuthCriteria: ...
```

---

## 4. ERROR HANDLING STRATEGY

### Pattern: Typed Error Responses (never raise through HTTP boundary)

```python
# All tools return models with optional `error` field
# HTTP endpoints return structured error responses
# LLM never sees raw exceptions — only formatted error messages

class ErrorResponse(BaseModel):
    error: str
    error_code: str
    detail: str | None = None
    recoverable: bool = True

# HTTP status mapping
# 400: Invalid input (validation error)
# 422: FHIR parse error
# 503: External API unavailable (retries exhausted)
# 500: Internal error (unexpected)
```

### Retry Configuration

```python
RETRY_CONFIG = {
    "max_attempts": 3,
    "backoff_factor": 2.0,
    "backoff_max": 10.0,
    "retry_on": [408, 429, 500, 502, 503, 504],
}
```

---

## 5. CACHE STRATEGY

```python
# In-memory cache using cachetools (no Redis needed for hackathon)
from cachetools import TTLCache

ICD10_CACHE = TTLCache(maxsize=1000, ttl=3600)
RXNORM_CACHE = TTLCache(maxsize=1000, ttl=3600)
INTERACTION_CACHE = TTLCache(maxsize=500, ttl=300)
LOINC_CACHE = TTLCache(maxsize=1000, ttl=3600)

# Cache key: function_name:input_hash
# Example: "resolve_icd10:E11.9"
```

---

## 6. CONFIGURATION MANAGEMENT

```python
# mcp_server/config.py and a2a_agent/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    
    # Required
    anthropic_api_key: str
    
    # MCP Server
    port_mcp: int = 8001
    nlm_api_key: str = ""    # Optional — increases rate limits
    
    # A2A Agent
    port_agent: int = 8000
    mcp_server_url: str = "http://localhost:8001"
    
    # Shared
    fhir_base_url: str = "https://hapi.fhir.org/baseR4"
    log_level: str = "INFO"
    environment: str = "development"
    
    # HTTP client
    http_connect_timeout: float = 10.0
    http_read_timeout: float = 30.0
    http_max_retries: int = 3
    
    # Task store
    task_ttl_hours: int = 24
    max_concurrent_tasks: int = 10
```

---

## 7. TESTING SPECIFICATIONS

### 7.1 Test Structure

```
mcp_server/tests/
├── conftest.py              # respx mocks, fixtures, synthetic data
├── test_icd10.py
├── test_rxnorm.py
├── test_loinc.py
└── test_prior_auth.py

a2a_agent/tests/
├── conftest.py              # FastAPI test client, MCP client mocks
├── test_task_handler.py
├── test_orchestrator.py
└── test_fhir_reader.py
```

### 7.2 Test Matrix — MCP Tools

| Test | Input | Expected Output | Type |
|---|---|---|---|
| `test_resolve_icd10_valid_code` | `"E11.9"` | SNOMED 44054006 | Happy path |
| `test_resolve_icd10_invalid_code` | `"XXXXX"` | `{error: "Code not found"}` | Error |
| `test_resolve_icd10_timeout` | `"E11.9"` + mock timeout | Error model, not exception | Resilience |
| `test_lookup_rxnorm_by_brand` | `"Ozempic"` | RxNorm 2200660, GLP-1 class | Happy path |
| `test_lookup_rxnorm_generic_name` | `"semaglutide"` | Same as above | Happy path |
| `test_lookup_rxnorm_not_found` | `"not_a_drug_xyz"` | `{error: "Drug not found"}` | Error |
| `test_check_interactions_multiple` | `["2200660", "860974"]` | Interaction list | Happy path |
| `test_check_interactions_single_drug` | `["2200660"]` | `{interactions: [], total: 0}` | Edge case |
| `test_get_loinc_hba1c` | `"HbA1c"` | LOINC 4548-4 | Happy path |
| `test_get_prior_auth_generic` | `"J0173", "generic"` | Criteria object | Happy path |
| `test_get_prior_auth_unknown_payer` | `"J0173", "unknownpayer"` | Falls back to generic | Fallback |

### 7.3 Test Matrix — A2A Agent

| Test | Input | Expected | Type |
|---|---|---|---|
| `test_send_new_task_valid_bundle` | Valid FHIR + "Ozempic" | task.state = working/completed | Happy path |
| `test_send_task_invalid_fhir` | Malformed JSON | 422 + FHIRParseError | Validation |
| `test_send_task_ambiguous_drug` | "diabetes medication" | needs_clarification state | Edge case |
| `test_draft_has_missing_items` | Patient missing second trial | missing_items populated | Business logic |
| `test_human_review_always_true` | Any input | result.human_review_required = True | Invariant |
| `test_confidence_score_range` | Any input | 0.0 <= score <= 1.0 | Invariant |
| `test_task_continuation` | Existing task_id + context | Updated draft | Multi-turn |

### 7.4 Fixtures

```python
# tests/conftest.py (shared)

SYNTHETIC_PATIENT_T2DM = {
    "resourceType": "Bundle",
    "type": "collection",
    "entry": [
        {
            "resource": {
                "resourceType": "Patient",
                "id": "synthetic-001",
                "name": [{"text": "Maria González"}],
                "birthDate": "1975-03-15",
                "gender": "female"
            }
        },
        {
            "resource": {
                "resourceType": "Condition",
                "code": {"coding": [{"system": "http://hl7.org/fhir/sid/icd-10", "code": "E11.9"}]},
                "clinicalStatus": {"coding": [{"code": "active"}]}
            }
        }
        # ... more resources
    ]
}

@pytest.fixture
def synthetic_patient_t2dm():
    return SYNTHETIC_PATIENT_T2DM

@pytest.fixture
def mock_rxnorm_ozempic():
    return {
        "rxnorm_id": "2200660",
        "generic_name": "semaglutide",
        "brand_names": ["Ozempic", "Wegovy"],
        "drug_class": "Glucagon-like peptide-1 receptor agonist",
        "requires_prior_auth": True
    }
```

---

## 8. LOGGING SPECIFICATION

```python
# structlog configuration
import structlog

structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer() if PRODUCTION else structlog.dev.ConsoleRenderer()
    ]
)

log = structlog.get_logger()

# Required log events (every tool call):
log.info("tool_called", tool="resolve_icd10", input=code, cache_hit=False)
log.info("tool_success", tool="resolve_icd10", result_preview=str(result)[:100], latency_ms=142)
log.error("tool_failed", tool="resolve_icd10", error=str(e), attempt=2)

# Required log events (every agent task):
log.info("task_started", task_id=task.id, patient_id=patient.id)
log.info("task_completed", task_id=task.id, confidence=draft.confidence_score, duration_s=elapsed)
```
