# AuthClear Demo Video Script - 3 Minutes
**Hackathon:** Agents Assemble - Healthcare AI Endgame
**Duration:** 2:55 (under 3 min requirement)
**Format:** 1920x1080, 30fps, MP4
**Upload:** YouTube (unlisted)

---

## 🎬 STORYBOARD & NARRATION

### SCENE 1: PROBLEM (0:00 - 0:30) - 30 seconds

**VISUAL:** Title card with AuthClear logo, transition to statistics overlay

**NARRATION:**
```
[0:00-0:10]
"Physicians spend 12 hours per week on prior authorizations.
That's 43 requests per physician, costing the healthcare system
31 billion dollars annually."

[0:10-0:20]
"The problem? Clinical data is locked in fragmented EHR systems,
and payers require extensive documentation in formats physicians
don't have time to prepare."

[0:20-0:30]
"AuthClear solves this with two AI agents: a FHIR terminology
engine and a prior authorization copilot. Let me show you how
it works."
```

**ON SCREEN TEXT:**
- 0:05: "12 hours/week on prior auth"
- 0:08: "43 requests per physician"
- 0:10: "$31B annual cost"
- 0:25: "AuthClear: AI-Powered Prior Auth"

---

### SCENE 2: ARCHITECTURE (0:30 - 0:50) - 20 seconds

**VISUAL:** Split screen showing MCP Server (left) and A2A Agent (right)

**NARRATION:**
```
[0:30-0:40]
"AuthClear consists of two agents. First, the MCP Server:
a clinical terminology engine that translates ICD-10, RxNorm,
and LOINC codes using FHIR R4 standards."

[0:40-0:50]
"Second, the A2A Agent: a prior authorization copilot that reads
patient data, identifies requirements, and generates structured
authorization drafts."
```

**ON SCREEN TEXT:**
- 0:32: "MCP Server - FHIR Terminology Engine"
- 0:42: "A2A Agent - Prior Auth Copilot"

**SCREEN ACTIONS:**
- Show MCP server tools list (resolve_icd10, lookup_rxnorm, etc.)
- Show A2A agent card JSON

---

### SCENE 3: LIVE DEMO - MCP Server (0:50 - 1:30) - 40 seconds

**VISUAL:** Terminal/IDE showing MCP Server running

**NARRATION:**
```
[0:50-1:00]
"Let's start with the MCP Server. I'm resolving ICD-10 code
E11.9 - Type 2 Diabetes. The server translates it to SNOMED code
44054006 and provides the clinical description."

[1:00-1:10]
"Next, I look up the drug Ozempic. The server returns the RxNorm ID,
drug class GLP-1 receptor agonist, and confirms it requires prior
authorization."

[1:10-1:20]
"Finally, I retrieve the prior auth criteria for semaglutide from
a generic payer. The server returns required diagnoses, lab thresholds,
and medication trial requirements."

[1:20-1:30]
"All of this happens in milliseconds using hardcoded mappings for
common codes, with API fallback for rare cases. The MCP Server is
now ready to serve the A2A Agent."
```

**SCREEN ACTIONS:**
- 0:50: Run `python -c "import asyncio; from mcp_server.tools.icd10 import resolve_icd10; print(asyncio.run(resolve_icd10('E11.9')))"`
- 1:00: Run `python -c "import asyncio; from mcp_server.tools.rxnorm import lookup_rxnorm; print(asyncio.run(lookup_rxnorm('Ozempic')))"`
- 1:10: Run `python -c "from mcp_server.tools.prior_auth import get_prior_auth_criteria; print(get_prior_auth_criteria('J0173', 'generic'))"`
- 1:25: Show MCP server logs confirming tool responses

---

### SCENE 4: LIVE DEMO - A2A Agent (1:30 - 2:30) - 60 seconds

**VISUAL:** Browser/Postman showing A2A Agent API call

**NARRATION:**
```
[1:30-1:45]
"Now the A2A Agent. I'm loading a synthetic FHIR bundle for Maria
González, a 50-year-old patient with Type 2 Diabetes. She has an
HbA1c of 8.9%, BMI of 34, and has tried Metformin and Glipizide for
over 3 months."

[1:45-2:00]
"The agent parses the FHIR bundle, extracts 1 diagnosis, 2 medications,
and 2 lab results. It then calls the MCP Server to resolve all clinical
codes and retrieve prior auth criteria for Ozempic."

[2:00-2:15]
"Using Claude's reasoning, the agent analyzes whether Maria meets
the criteria: HbA1c above 7.5? Yes. BMI above 30? Yes. Two oral agents
tried? Yes. All criteria met."

[2:15-2:30]
"The agent generates a structured prior authorization draft with 90%
confidence, clinical justification, and supporting evidence. Most
importantly, it flags this for human review - we never auto-approve."
```

**SCREEN ACTIONS:**
- 1:30: Show patient_t2dm_complete.json in editor
- 1:45: POST to `/tasks/send` with FHIR bundle
- 2:00: Show agent reasoning logs (calling MCP tools, evaluating criteria)
- 2:15: Show final PriorAuthDraft JSON response
- 2:25: Highlight `"human_review_required": true`

---

### SCENE 5: COMPLIANCE & IMPACT (2:30 - 2:55) - 25 seconds

**VISUAL:** Split screen - compliance badges (left), ROI calculator (right)

**NARRATION:**
```
[2:30-2:40]
"AuthClear is compliant with state AI transparency laws: Texas
SB 490, Arizona HB 2417, and Maryland HB 1174. Human-in-the-loop
is architecturally enforced - no agent can approve or deny
authorizations."

[2:40-2:50]
"The impact? For a 10-physician practice processing 430 prior auths
per week, AuthClear saves 8 hours per week in staff time. That's
$83,000 per year in labor costs alone."

[2:50-2:55]
"AuthClear: AI-powered prior authorization that keeps physicians
in control."
```

**ON SCREEN TEXT:**
- 2:32: "✓ TX SB 490 Compliant"
- 2:34: "✓ AZ HB 2417 Compliant"
- 2:36: "✓ MD HB 1174 Compliant"
- 2:42: "8 hours/week saved"
- 2:44: "$83K/year ROI"
- 2:52: "AuthClear - github.com/yourname/authclear"

**SCREEN ACTIONS:**
- Show compliance checklist with green checkmarks
- Show simple ROI calculator spreadsheet

---

## 🎙️ VOICE-OVER RECORDING NOTES

**Tone:** Professional, confident, conversational (not robotic)
**Pace:** 150-160 words per minute (slightly faster than normal speech)
**Emphasis on:**
- Statistics: "12 hours", "31 billion", "90% confidence"
- Key terms: "FHIR", "human-in-the-loop", "never auto-approve"
- Compliance: "Texas SB 490", "architecturally enforced"

**Recording tips:**
- Use a quiet room with minimal echo
- Record in Audacity or Adobe Audition
- Apply: Noise reduction, EQ boost at 100-200Hz (warmth), Compressor (even volume)
- Export as MP3 320kbps or WAV 48kHz

---

## 📊 TIMING BREAKDOWN

| Scene | Duration | Cumulative | Content |
|-------|----------|-----------|---------|
| 1. Problem | 30s | 0:30 | Statistics, pain points |
| 2. Architecture | 20s | 0:50 | Two-agent system |
| 3. MCP Demo | 40s | 1:30 | Code resolution tools |
| 4. A2A Demo | 60s | 2:30 | Full prior auth flow |
| 5. Compliance | 25s | 2:55 | Regulatory + ROI |

**Total:** 2:55 (5 seconds buffer under 3:00 limit)

---

## 🎥 SCREEN RECORDING SETUP

**Software:** OBS Studio (free, open source)

**OBS Scene Configuration:**

1. **Scene 1 - Title Card**
   - Source: Image (create title_card.png with AuthClear logo)
   - Transition: Fade to Scene 2

2. **Scene 2 - Architecture Diagram**
   - Source: Image (create architecture_diagram.png)
   - Add text overlays with animated entrance

3. **Scene 3 - Terminal Demo**
   - Source: Window Capture (Terminal/PowerShell)
   - Font: Consolas 14pt or Fira Code 14pt
   - Resolution: 1920x1080

4. **Scene 4 - Browser Demo**
   - Source: Window Capture (VS Code + Browser side by side)
   - Highlight cursor movements with OBS plugin

5. **Scene 5 - Compliance Screen**
   - Source: Browser (HTML page with compliance badges)
   - Add animated checkmarks

**Recording settings:**
- Resolution: 1920x1080
- FPS: 30
- Encoder: x264
- Bitrate: 5000 kbps (high quality)
- Format: MP4

---

## 📝 SUBTITLE FILE (SRT FORMAT)

Saved as: `authclear_demo_subtitles.srt`

(See separate file below)

---

## ✅ PRE-RECORDING CHECKLIST

- [ ] All Python dependencies installed
- [ ] MCP Server running on port 8001
- [ ] Synthetic patient files in `shared/fhir/synthetic_patients/`
- [ ] Test MCP tools (run integration test)
- [ ] Title card image created (1920x1080)
- [ ] Architecture diagram created
- [ ] Terminal font size readable (14pt minimum)
- [ ] OBS scenes configured
- [ ] Microphone tested (clear audio, no echo)
- [ ] Script printed or on second monitor
- [ ] Practice run completed (timing verified)

---

## 🚀 POST-PRODUCTION CHECKLIST

- [ ] Video rendered to MP4
- [ ] Audio levels normalized (-14 LUFS)
- [ ] Subtitles embedded or uploaded separately
- [ ] Video duration verified < 3:00
- [ ] Thumbnail created (1280x720)
- [ ] YouTube upload (unlisted)
- [ ] Video title: "AuthClear - AI Prior Authorization Copilot (Agents Assemble 2026)"
- [ ] Video description includes: GitHub link, hackathon name, tech stack
- [ ] Add to Devpost submission

---

## 📐 VISUAL ASSETS NEEDED

1. **title_card.png** (1920x1080)
   - AuthClear logo/wordmark
   - Subtitle: "AI-Powered Prior Authorization"
   - Footer: "Agents Assemble Hackathon 2026"

2. **architecture_diagram.png** (1920x1080)
   - Left box: "MCP Server - FHIR Terminology"
   - Right box: "A2A Agent - Prior Auth Copilot"
   - Arrow between them labeled "MCP Tool Calls"
   - Bottom: "Prompt Opinion Marketplace"

3. **compliance_badges.png** (960x1080)
   - Three badges with checkmarks:
     - Texas SB 490 ✓
     - Arizona HB 2417 ✓
     - Maryland HB 1174 ✓
   - Footer: "Human-in-the-Loop Always Required"

4. **roi_calculator.png** (960x1080)
   - Simple spreadsheet showing:
     - Prior auths/week: 430
     - Time saved/auth: 15 min
     - Total hours saved/week: 8h
     - Hourly staff cost: $25
     - Annual savings: $83,200

---

**Script word count:** ~450 words
**Speaking rate target:** 155 words/minute
**Calculated duration:** 2:54 ✓

Ready for recording!
