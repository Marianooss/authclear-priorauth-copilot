# AuthClear — AI-Powered Prior Authorization Copilot

> **Hackathon:** Agents Assemble — Healthcare AI Endgame
> **Sponsor:** Prompt Opinion (Darena Health)
> **Submission:** Dual Path A (MCP Server) + Path B (A2A Agent)
> **Tech Stack:** Python | FastMCP | FastAPI | Claude (Bedrock) | FHIR R4

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🎯 The Problem

Physicians spend **12+ hours per week** on prior authorization paperwork — 43 requests each, costing **$31 billion annually** in administrative burden. Manual PA processing leads to:

- ❌ 30-50% first-pass denial rates
- ❌ Treatment delays of 7-14 days
- ❌ Physician burnout and staff turnover
- ❌ Compliance challenges with new regulations (TX SB 490, AZ HB 2417, MD HB 1174)

**AuthClear** uses AI to automate 90% of PA documentation while keeping physicians in control.

---

## 🏗️ Architecture

```
┌─────────────────┐
│   Web UI        │ ← Physician Interface (Flask + JavaScript)
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│  A2A Prior Auth Agent (FastAPI)         │
│  ├─ Reads patient FHIR bundle           │
│  ├─ Calls MCP Server for terminology    │ ◄─┐
│  ├─ Runs gap analysis vs payer criteria │   │
│  └─ Generates structured PA draft       │   │
└─────────────────────────────────────────┘   │
                                               │
┌──────────────────────────────────────────┐  │
│  FHIR Terminology MCP Server (HTTP API) │◄─┘
│  ├─ resolve_icd10: ICD-10 → SNOMED      │
│  ├─ lookup_rxnorm: Drug → RxNorm + class│
│  ├─ check_drug_interactions             │
│  ├─ get_loinc_code: Lab test → LOINC    │
│  └─ get_prior_auth_criteria             │
└──────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────┐
│  Public APIs                             │
│  ├─ NIH NLM RxNav (drug data)            │
│  ├─ HAPI FHIR R4 (test server)           │
│  └─ Hardcoded payer criteria (6 payers)  │
└──────────────────────────────────────────┘
```

**Key Features:**
- ✅ **Human-in-the-loop**: No auto-approval, physician always reviews
- ✅ **AWS Bedrock**: Claude 3 Haiku for clinical reasoning
- ✅ **9 synthetic patients**: Diabetes, RA, COPD, breast cancer, lupus, etc.
- ✅ **11 medications**: Ozempic, Herceptin, Spiriva, Benlysta, etc.
- ✅ **6 payers**: Generic, BCBS, Medicare, Medicaid, Aetna, United

---

## 🚀 Quick Start

### **Prerequisites**
- Python 3.11+
- AWS credentials configured (`~/.aws/credentials` or environment variables)
- Access to AWS Bedrock (Claude 3 models)

### **Installation**

```bash
# Clone repository
git clone https://github.com/yourusername/authclear
cd authclear

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env - Set CLAUDE_PROVIDER=bedrock and AWS credentials
```

### **Run Locally**

**Option 1: All-in-one Web UI (Recommended)**

```bash
# Terminal 1: Start MCP Server
python run_mcp_http_server.py

# Terminal 2: Start A2A Agent
python run_a2a_agent.py

# Terminal 3: Start Web UI
python run_web_server.py
# Opens browser at http://localhost:3000
```

**Option 2: API Only**

```bash
# Start services
python run_mcp_http_server.py  # Port 8001
python run_a2a_agent.py         # Port 8000

# Test with curl
curl -X POST http://localhost:8000/tasks/send \
  -H "Content-Type: application/json" \
  -d @test_payloads/herceptin_request.json
```

### **Run Tests**

```bash
# Test real backend end-to-end
python test_real_backend.py

# Unit tests
pytest --tb=short -q

# Integration tests
python test_integration.py
```

---

## 📹 Demo

**Web UI Demo:**
- Select patient (e.g., Linda Thompson - HER2+ Breast Cancer)
- Choose medication (e.g., Herceptin)
- Click "Process Prior Authorization"
- Review AI-generated draft with 92% confidence

**Demo Video:** [YouTube link - added before submission]

---

## 🧬 Synthetic Patients (9 FHIR Bundles)

1. **Maria González** - Type 2 DM (complete criteria)
2. **John Smith** - Type 2 DM (gaps in documentation)
3. **Sarah Johnson** - Rheumatoid Arthritis
4. **Robert Chen** - Obesity/Prediabetes
5. **William Martinez** - Atrial Fibrillation
6. **Juan Pérez** - Hypertension
7. **Linda Thompson** - HER2+ Breast Cancer (Stage IIB)
8. **Richard Davis** - Severe COPD (GOLD Stage 3)
9. **Angela Rodriguez** - Systemic Lupus Erythematosus

---

## 💊 Supported Medications (11 CPT/HCPCS Codes)

| Code | Drug | Indication |
|---|---|---|
| J0173 | Ozempic (semaglutide) | Type 2 Diabetes |
| J1438 | Enbrel (etanercept) | Rheumatoid Arthritis |
| J9355 | Herceptin (trastuzumab) | HER2+ Breast Cancer |
| J9299 | Opdivo (nivolumab) | Melanoma/NSCLC |
| J9035 | Avastin (bevacizumab) | Colorectal/Lung Cancer |
| J9271 | Keytruda (pembrolizumab) | Melanoma/NSCLC |
| J7637 | Spiriva (tiotropium) | Severe COPD |
| J0490 | Benlysta (belimumab) | Lupus (SLE) |
| J1745 | Remicade (infliximab) | IBD/RA |
| J2323 | Tysabri (natalizumab) | Multiple Sclerosis |
| J0897 | Prolia (denosumab) | Osteoporosis |

---

## 🏥 Compliance & Regulations

AuthClear is designed to comply with:

- ✅ **Texas SB 490** - AI transparency + human review required
- ✅ **Arizona HB 2417** - No AI-only clinical decisions
- ✅ **Maryland HB 1174** - Human-in-the-loop mandated
- ✅ **CMS FHIR API mandate** - FHIR R4 interoperability by 2027

**Human review is architecturally enforced** - `human_review_required` field is frozen to `true` in all PriorAuthDraft outputs.

---

## 📊 ROI Calculator

For a **10-physician practice**:

| Metric | Before | After | Savings |
|---|---|---|---|
| Time per PA | 30 min | 3 min | 27 min |
| PAs per week | 430 | 430 | - |
| Staff hours/week | 215h | 21.5h | 193.5h |
| **Annual cost** | $558,000 | $55,800 | **$502,200** |

---

## 🛠️ Tech Stack

- **LLM**: Claude 3 Haiku via AWS Bedrock
- **Backend**: FastAPI + FastMCP (HTTP wrapper)
- **Frontend**: Flask + Vanilla JavaScript
- **FHIR**: fhir.resources (Pydantic models)
- **Testing**: pytest + pytest-asyncio + respx
- **Deploy**: Railway / Docker Compose

---

## 📂 Repository Structure

```
authclear/
├── mcp_server/              # Path A: FHIR Terminology MCP Server
│   ├── server.py            # FastMCP server (stdio)
│   ├── tools/               # 5 MCP tools
│   └── data/criteria/       # Payer-specific PA criteria (YAML)
├── a2a_agent/               # Path B: Prior Auth A2A Agent
│   ├── main.py              # FastAPI server
│   ├── orchestrator.py      # ReAct loop with Claude
│   ├── claude_client.py     # Bedrock integration
│   └── prompts/             # System prompts
├── web_ui/                  # Web interface
│   ├── index.html           # UI
│   └── app.js               # Frontend logic
├── shared/
│   ├── fhir/synthetic_patients/  # 9 FHIR bundles
│   └── models/              # Pydantic models
├── run_mcp_http_server.py   # MCP Server HTTP wrapper
├── run_a2a_agent.py         # A2A Agent runner
├── run_web_server.py        # Flask web server
├── test_real_backend.py     # End-to-end test
└── .env                     # Configuration (not committed)
```

---

## 🔐 Environment Variables

```bash
# .env
CLAUDE_PROVIDER=bedrock                              # or "anthropic"
AWS_REGION=us-east-1
AWS_BEDROCK_MODEL=anthropic.claude-3-haiku-20240307-v1:0
# AWS_ACCESS_KEY_ID=AKIAXXXX                         # Optional if using ~/.aws/credentials
# AWS_SECRET_ACCESS_KEY=XXXX                         # Optional

# Anthropic API (if CLAUDE_PROVIDER=anthropic)
ANTHROPIC_API_KEY=sk-ant-...

# Ports
PORT_MCP=8001
PORT_AGENT=8000

# MCP Server URL
MCP_SERVER_URL=http://localhost:8001
```

---

## 🚢 Deployment

**Railway (Production):**

```bash
# Deploy MCP Server
railway up --service authclear-mcp

# Deploy A2A Agent
railway up --service authclear-agent

# Environment variables in Railway dashboard:
# CLAUDE_PROVIDER=bedrock
# AWS_REGION=us-east-1
# AWS_ACCESS_KEY_ID=...
# AWS_SECRET_ACCESS_KEY=...
```

**Docker Compose (Local):**

```bash
docker-compose up --build
```

---

## 🧪 Testing

```bash
# End-to-end test with real Bedrock
python test_real_backend.py

# Unit tests
pytest mcp_server/tests/
pytest a2a_agent/tests/

# Integration test
python test_integration.py
```

---

## 📝 License

MIT License - See LICENSE file for details.

---

## 🙏 Acknowledgments

- **Prompt Opinion / Darena Health** for hosting the hackathon
- **Anthropic** for Claude via AWS Bedrock
- **NIH NLM** for RxNorm/LOINC public APIs
- **HL7 FHIR** for interoperability standards

---

## 📧 Contact

For questions or demo requests: [Your contact]

**Built for Agents Assemble Healthcare AI Endgame Hackathon**
May 2026
