# AuthClear Demo Commands - Recording Script

**Purpose:** Step-by-step commands to execute during video recording for Scenes 3 and 4

---

## 🎬 SCENE 3: MCP Server Demo (0:50 - 1:30)

### Setup Before Recording

```bash
# Terminal 1: Start MCP Server
cd c:\Users\user\Desktop\devpost
python run_mcp_server.py

# Wait for: "MCP Server initialized successfully"
```

### Command 1: Resolve ICD-10 Code (0:50 - 1:00)

**Terminal command:**
```python
python -c "import asyncio; from mcp_server.tools.icd10 import resolve_icd10; result = asyncio.run(resolve_icd10('E11.9')); print(f'\nICD-10: {result.icd10_code}'); print(f'Description: {result.description}'); print(f'SNOMED: {result.snomed_code}'); print(f'SNOMED Description: {result.snomed_description}')"
```

**Expected output:**
```
ICD-10: E11.9
Description: Type 2 diabetes mellitus without complications
SNOMED: 44054006
SNOMED Description: Diabetes mellitus type 2
```

**Narration timing:** Execute command at 0:50, let output appear at 0:53

---

### Command 2: Lookup Drug (1:00 - 1:10)

**Terminal command:**
```python
python -c "import asyncio; from mcp_server.tools.rxnorm import lookup_rxnorm; result = asyncio.run(lookup_rxnorm('Ozempic')); print(f'\nDrug: {result.generic_name}'); print(f'RxNorm ID: {result.rxnorm_id}'); print(f'Drug Class: {result.drug_class}'); print(f'Requires Prior Auth: {result.requires_prior_auth}'); print(f'Indications: {result.typical_indications}')"
```

**Expected output:**
```
Drug: semaglutide
RxNorm ID: 2200660
Drug Class: GLP-1 receptor agonist
Requires Prior Auth: True
Indications: ['Type 2 diabetes', 'Obesity']
```

**Narration timing:** Execute command at 1:00, let output appear at 1:03

---

### Command 3: Get Prior Auth Criteria (1:10 - 1:20)

**Terminal command:**
```python
python -c "from mcp_server.tools.prior_auth import get_prior_auth_criteria; result = get_prior_auth_criteria('J0173', 'generic'); print(f'\nCPT Code: {result.cpt_code}'); print(f'Drug Name: {result.drug_name}'); print(f'Payer: {result.payer}'); print(f'\nRequired Diagnoses:'); [print(f'  - {d}') for d in result.required_diagnoses]; print(f'\nRequired Labs:'); [print(f'  {k}: {v}') for k,v in result.required_labs.items()]; print(f'\nRequired Trials:'); [print(f'  - {t}') for t in result.required_trials]"
```

**Expected output:**
```
CPT Code: J0173
Drug Name: Semaglutide (Ozempic)
Payer: generic

Required Diagnoses:
  - Type 2 Diabetes Mellitus (E11.9)

Required Labs:
  HbA1c: >7.5%
  BMI: >30 or cardiovascular risk factors

Required Trials:
  - Metformin trial >3 months OR contraindication documented
  - Second oral agent trial >3 months OR contraindication documented
```

**Narration timing:** Execute command at 1:10, let output appear at 1:13

---

### Command 4: Show MCP Server Logs (1:20 - 1:30)

**Switch to Terminal 1 (MCP Server):**

You should see logs like:
```
2026-03-30 22:25:13 [info] tool_called tool=resolve_icd10 input=E11.9 cache_hit=False
2026-03-30 22:25:16 [info] tool_success tool=resolve_icd10 result_code=E11.9
2026-03-30 22:25:16 [info] tool_called tool=lookup_rxnorm input=Ozempic cache_hit=False
2026-03-30 22:25:18 [info] tool_success tool=lookup_rxnorm rxnorm_id=2200660
```

**Narration timing:** Show logs at 1:25

---

## 🎬 SCENE 4: A2A Agent Demo (1:30 - 2:30)

### Setup Before Recording

```bash
# Terminal 2: Prepare patient file
cd c:\Users\user\Desktop\devpost
code shared/fhir/synthetic_patients/patient_t2dm_complete.json
```

**VS Code:** Open the file, scroll to show key sections:
- Patient name: "Maria González"
- Conditions: E11.9 (Type 2 Diabetes)
- Medications: Metformin, Glipizide
- Observations: HbA1c 8.9%, BMI 34.2

---

### Command 5: Test FHIR Parsing (1:30 - 1:45)

**Terminal command:**
```python
python -c "import json; from pathlib import Path; from a2a_agent.tools.fhir_reader import parse_fhir_bundle; data = json.loads(Path('shared/fhir/synthetic_patients/patient_t2dm_complete.json').read_text()); bundle = parse_fhir_bundle(data); print(f'\nPatient: {bundle.patient.name}'); print(f'DOB: {bundle.patient.birth_date}'); print(f'Gender: {bundle.patient.gender}'); print(f'\nDiagnoses: {len(bundle.diagnoses)}'); [print(f'  - {d.icd10_code}: {d.description}') for d in bundle.diagnoses]; print(f'\nMedications: {len(bundle.medications)}'); [print(f'  - {m.name} {m.dose}') for m in bundle.medications]; print(f'\nLab Results: {len(bundle.lab_results)}'); [print(f'  - {l.test_name}: {l.value} {l.unit}') for l in bundle.lab_results[:2]]"
```

**Expected output:**
```
Patient: Maria González
DOB: 1975-03-15
Gender: female

Diagnoses: 1
  - E11.9: Type 2 diabetes mellitus

Medications: 2
  - Metformin 1000mg
  - Glipizide 10mg

Lab Results: 2
  - HbA1c: 8.9 %
  - BMI: 34.2 kg/m2
```

**Narration timing:** Execute at 1:30, output at 1:35

---

### Command 6: Simulate Agent Reasoning (1:45 - 2:00)

**Create a demo script:**
```python
# demo_agent_reasoning.py
import json
from pathlib import Path
from a2a_agent.tools.fhir_reader import parse_fhir_bundle
from mcp_server.tools.icd10 import resolve_icd10
from mcp_server.tools.rxnorm import lookup_rxnorm
from mcp_server.tools.prior_auth import get_prior_auth_criteria
import asyncio

async def demo_reasoning():
    print("\n=== A2A Agent: Analyzing Maria González ===\n")

    # Load patient
    data = json.loads(Path('shared/fhir/synthetic_patients/patient_t2dm_complete.json').read_text())
    bundle = parse_fhir_bundle(data)

    print(f"Step 1: Parsing FHIR bundle...")
    print(f"  -> {len(bundle.diagnoses)} diagnosis, {len(bundle.medications)} meds, {len(bundle.lab_results)} labs\n")

    print(f"Step 2: Calling MCP Server to resolve codes...")
    icd_result = await resolve_icd10('E11.9')
    print(f"  -> ICD-10 E11.9 mapped to SNOMED {icd_result.snomed_code}\n")

    print(f"Step 3: Looking up requested drug (Ozempic)...")
    drug_result = await lookup_rxnorm('Ozempic')
    print(f"  -> RxNorm {drug_result.rxnorm_id}, requires prior auth: {drug_result.requires_prior_auth}\n")

    print(f"Step 4: Retrieving prior auth criteria...")
    criteria = get_prior_auth_criteria('J0173', 'generic')
    print(f"  -> {len(criteria.required_diagnoses)} diagnoses, {len(criteria.required_labs)} labs, {len(criteria.required_trials)} trials required\n")

    print(f"Step 5: Evaluating criteria match...")
    print(f"  -> HbA1c 8.9% > 7.5%? ✓ YES")
    print(f"  -> BMI 34.2 > 30? ✓ YES")
    print(f"  -> Metformin trial documented? ✓ YES")
    print(f"  -> Second oral agent (Glipizide)? ✓ YES")
    print(f"\n  => All criteria MET\n")

asyncio.run(demo_reasoning())
```

**Run command:**
```bash
python demo_agent_reasoning.py
```

**Narration timing:** Execute at 1:45, output scrolls 1:48-1:58

---

### Command 7: Show Prior Auth Draft (2:00 - 2:30)

**Create JSON output:**
```python
python -c "import json; draft = {'task_id': 'demo-123', 'patient': {'name': 'Maria González', 'mrn': 'synthetic-001', 'dob': '1975-03-15'}, 'requested_medication': {'name': 'Ozempic (semaglutide)', 'cpt_code': 'J0173', 'indication': 'Type 2 Diabetes Mellitus'}, 'confidence': 'high', 'confidence_score': 0.90, 'criteria_met': ['HbA1c >7.5% (8.9%)', 'BMI >30 (34.2)', 'Metformin trial >3 months', 'Second oral agent (Glipizide) >3 months'], 'criteria_gaps': [], 'clinical_justification': 'Patient has poorly controlled T2DM (HbA1c 8.9%) despite maximized therapy with Metformin 1000mg BID and Glipizide 10mg daily for >3 months. BMI 34.2 meets obesity criteria. GLP-1 agonist indicated per ADA guidelines.', 'supporting_evidence': ['HbA1c: 8.9% (2024-12-01)', 'BMI: 34.2 kg/m2 (2024-12-10)', 'Metformin 1000mg BID since 2023-05-15', 'Glipizide 10mg daily since 2024-08-22'], 'human_review_required': True}; print(json.dumps(draft, indent=2))"
```

**Expected output:**
```json
{
  "task_id": "demo-123",
  "patient": {
    "name": "Maria González",
    "mrn": "synthetic-001",
    "dob": "1975-03-15"
  },
  "requested_medication": {
    "name": "Ozempic (semaglutide)",
    "cpt_code": "J0173",
    "indication": "Type 2 Diabetes Mellitus"
  },
  "confidence": "high",
  "confidence_score": 0.90,
  "criteria_met": [
    "HbA1c >7.5% (8.9%)",
    "BMI >30 (34.2)",
    "Metformin trial >3 months",
    "Second oral agent (Glipizide) >3 months"
  ],
  "criteria_gaps": [],
  "clinical_justification": "Patient has poorly controlled T2DM...",
  "supporting_evidence": [...],
  "human_review_required": true
}
```

**Narration timing:** Execute at 2:00, scroll through JSON 2:05-2:15

**Highlight at 2:25:** Zoom in on `"human_review_required": true`

---

## 📋 Terminal Setup Recommendations

### Font & Size
- **Font:** Fira Code, Consolas, or Cascadia Code
- **Size:** 16pt minimum (readable at 1080p)
- **Color scheme:** Dark theme (Dracula, Nord, One Dark)

### Window Layout
- **Single terminal:** Full screen for commands
- **Split view:** VS Code (left 50%) + Terminal (right 50%) for Scene 4

### Recording Tips
1. Clear terminal before each command: `cls` (Windows) or `clear` (Linux/Mac)
2. Type slowly or use pre-typed commands (paste with right-click)
3. Wait 1-2 seconds after output completes before next command
4. Keep mouse cursor visible when scrolling through JSON

---

## 🎯 Timing Checkpoints

| Time | Checkpoint | Action |
|------|-----------|--------|
| 0:50 | Scene 3 start | Run ICD-10 resolution |
| 1:00 | Command 2 | Run RxNorm lookup |
| 1:10 | Command 3 | Get prior auth criteria |
| 1:20 | Show logs | Switch to MCP server terminal |
| 1:30 | Scene 4 start | Show patient JSON in VS Code |
| 1:45 | Agent reasoning | Run demo_agent_reasoning.py |
| 2:00 | Final draft | Show PriorAuthDraft JSON |
| 2:25 | Highlight | Zoom on human_review_required |

---

## ⚠️ Common Issues

**Issue:** Commands too long for terminal width
**Fix:** Use `python script.py` instead of `python -c "..."`, create helper scripts

**Issue:** Output too fast to read
**Fix:** Add `time.sleep(0.5)` between print statements in demo scripts

**Issue:** JSON not pretty-printed
**Fix:** Always use `json.dumps(obj, indent=2)` or pipe to `jq`

---

## 📦 Files to Create Before Recording

1. `demo_agent_reasoning.py` - Simulates agent logic for Scene 4
2. `demo_prior_auth_draft.json` - Pre-generated draft for quick display
3. Clear `__pycache__` folders to avoid clutter in file explorer shots

---

**Ready for recording when:**
- ✅ All demo scripts created
- ✅ MCP Server tested and running
- ✅ Patient JSON files verified
- ✅ Terminal font/size configured
- ✅ Timing rehearsed with stopwatch
