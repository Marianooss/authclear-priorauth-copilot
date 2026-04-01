# cot_react.md — CoT/ReAct Methodology
> AuthClear | Reasoning Patterns, Prompt Engineering, Agent Skeleton

---

## 1. WHAT IS ReAct IN THIS CONTEXT

ReAct (Reasoning + Acting) is the core loop that drives the Prior Auth Copilot.  
The agent **thinks before acting**, **observes the result**, and **thinks again** before the next action.  
This is implemented as structured tool-use with the Anthropic API.

```
[Think] → [Act] → [Observe] → [Think] → [Act] → ... → [Final Output]
```

---

## 2. REACT SKELETON (Copy this pattern for all orchestrator iterations)

```python
# a2a_agent/orchestrator.py

from __future__ import annotations
import asyncio
import time
import structlog
from anthropic import AsyncAnthropic
from a2a_agent.tools.mcp_client import MCPClient
from a2a_agent.prompts.system import build_system_prompt
from shared.models.prior_auth import PriorAuthDraft
from a2a_agent.models import Task

log = structlog.get_logger()
client = AsyncAnthropic()


TOOL_DEFINITIONS = [
    {
        "name": "resolve_icd10",
        "description": "Resolve an ICD-10-CM diagnosis code to SNOMED CT equivalent and human-readable description.",
        "input_schema": {
            "type": "object",
            "required": ["code"],
            "properties": {
                "code": {"type": "string", "description": "ICD-10-CM code, e.g. 'E11.9'"}
            }
        }
    },
    {
        "name": "lookup_rxnorm",
        "description": "Look up a drug by brand or generic name. Returns RxNorm ID, drug class, and prior auth flag.",
        "input_schema": {
            "type": "object",
            "required": ["drug_name"],
            "properties": {
                "drug_name": {"type": "string", "description": "Brand or generic drug name"}
            }
        }
    },
    {
        "name": "check_drug_interactions",
        "description": "Check interactions between multiple drugs. Requires at least 2 RxNorm IDs.",
        "input_schema": {
            "type": "object",
            "required": ["rxnorm_ids"],
            "properties": {
                "rxnorm_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of RxNorm IDs"
                }
            }
        }
    },
    {
        "name": "get_loinc_code",
        "description": "Look up the LOINC code for a laboratory test or clinical observation.",
        "input_schema": {
            "type": "object",
            "required": ["test_name"],
            "properties": {
                "test_name": {"type": "string", "description": "Common test name, e.g. 'HbA1c'"}
            }
        }
    },
    {
        "name": "get_prior_auth_criteria",
        "description": "Get prior authorization clinical criteria for a drug/procedure CPT or HCPCS code.",
        "input_schema": {
            "type": "object",
            "required": ["cpt_code"],
            "properties": {
                "cpt_code": {"type": "string", "description": "CPT or HCPCS code"},
                "payer": {"type": "string", "description": "Payer name (optional, defaults to generic)"}
            }
        }
    }
]


async def run_prior_auth_orchestration(task: Task, mcp: MCPClient) -> PriorAuthDraft:
    """
    Main ReAct loop. Sends patient context to Claude, handles tool calls,
    feeds results back, and returns a completed PriorAuthDraft.
    
    Pattern:
        1. Initial message with patient FHIR + requested item
        2. Claude thinks + calls tools
        3. We execute tools against MCP Server
        4. Feed tool results back to Claude
        5. Repeat until Claude produces final JSON output
        6. Parse and validate as PriorAuthDraft
    """
    start_time = time.monotonic()
    task_input = task.input
    
    log.info("orchestration_started", task_id=task.id, requested_item=task_input.requested_item)
    
    system_prompt = build_system_prompt()
    
    # Initial user message
    user_message = _build_initial_message(task_input)
    messages = [{"role": "user", "content": user_message}]
    
    max_iterations = 10
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1
        log.debug("react_iteration", task_id=task.id, iteration=iteration)
        
        # ── THINK (Claude reasons) ─────────────────────────────────────────
        response = await client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system=system_prompt,
            tools=TOOL_DEFINITIONS,
            messages=messages,
        )
        
        log.debug("llm_response", 
                  task_id=task.id,
                  stop_reason=response.stop_reason,
                  content_blocks=len(response.content))
        
        # Append assistant response to history
        messages.append({"role": "assistant", "content": response.content})
        
        # ── TERMINAL: No more tool calls → parse final output ──────────────
        if response.stop_reason == "end_turn":
            final_text = _extract_text(response.content)
            draft = _parse_draft(final_text, task.id)
            elapsed = time.monotonic() - start_time
            log.info("orchestration_completed",
                     task_id=task.id,
                     confidence=draft.confidence_score,
                     duration_s=round(elapsed, 2))
            return draft
        
        # ── ACT: Execute tool calls in parallel ────────────────────────────
        if response.stop_reason == "tool_use":
            tool_calls = [b for b in response.content if b.type == "tool_use"]
            
            # Run all tool calls concurrently
            tool_results = await asyncio.gather(
                *[_execute_tool(tc, mcp, task.id) for tc in tool_calls],
                return_exceptions=True
            )
            
            # ── OBSERVE: Feed results back to Claude ───────────────────────
            tool_result_blocks = []
            for tc, result in zip(tool_calls, tool_results):
                if isinstance(result, Exception):
                    content = f"Tool error: {str(result)}"
                    log.warning("tool_execution_error", 
                               task_id=task.id, tool=tc.name, error=str(result))
                else:
                    content = result
                    
                tool_result_blocks.append({
                    "type": "tool_result",
                    "tool_use_id": tc.id,
                    "content": content
                })
            
            messages.append({"role": "user", "content": tool_result_blocks})
            continue  # ← Loop back to THINK
        
        # Unexpected stop reason
        log.error("unexpected_stop_reason",
                  task_id=task.id, stop_reason=response.stop_reason)
        break
    
    # Max iterations exceeded — return partial draft with warning
    log.warning("max_iterations_exceeded", task_id=task.id, iterations=iteration)
    return _build_error_draft(task.id, "Max reasoning iterations exceeded")


async def _execute_tool(tool_call, mcp: MCPClient, task_id: str) -> str:
    """
    Dispatch a tool_use block to the appropriate MCP tool.
    Returns JSON string of result.
    """
    tool_name = tool_call.name
    inputs = tool_call.input
    
    log.info("tool_called", task_id=task_id, tool=tool_name, inputs=inputs)
    t0 = time.monotonic()
    
    try:
        if tool_name == "resolve_icd10":
            result = await mcp.resolve_icd10(inputs["code"])
        elif tool_name == "lookup_rxnorm":
            result = await mcp.lookup_rxnorm(inputs["drug_name"])
        elif tool_name == "check_drug_interactions":
            result = await mcp.check_drug_interactions(inputs["rxnorm_ids"])
        elif tool_name == "get_loinc_code":
            result = await mcp.get_loinc_code(inputs["test_name"])
        elif tool_name == "get_prior_auth_criteria":
            result = await mcp.get_prior_auth_criteria(
                inputs["cpt_code"],
                inputs.get("payer", "generic")
            )
        else:
            return f'{{"error": "Unknown tool: {tool_name}"}}'
        
        latency_ms = int((time.monotonic() - t0) * 1000)
        log.info("tool_success", task_id=task_id, tool=tool_name, latency_ms=latency_ms)
        return result.model_dump_json()
        
    except Exception as e:
        log.error("tool_failed", task_id=task_id, tool=tool_name, error=str(e))
        return f'{{"error": "Tool {tool_name} failed: {str(e)}"}}'


def _build_initial_message(task_input) -> str:
    """Build the structured initial prompt."""
    return f"""
Please generate a complete prior authorization request package for physician review.

REQUESTED ITEM: {task_input.requested_item}
PAYER: {task_input.payer}
URGENCY: {task_input.urgency}

PATIENT FHIR BUNDLE:
{task_input.fhir_bundle}

{f'ADDITIONAL CONTEXT: {task_input.additional_context}' if task_input.additional_context else ''}

Instructions:
1. Parse the FHIR bundle to extract patient demographics, diagnoses, medications, and labs
2. Use the available tools to resolve all clinical codes
3. Look up prior auth criteria for the requested item
4. Check for drug interactions between current medications and the requested drug
5. Perform gap analysis comparing patient record to payer criteria
6. Return a complete PriorAuthDraft JSON object

Return ONLY valid JSON matching the PriorAuthDraft schema. No preamble, no markdown.
"""


def _extract_text(content_blocks: list) -> str:
    """Extract text from Claude's response content blocks."""
    return "\n".join(
        block.text for block in content_blocks 
        if hasattr(block, "text")
    )


def _parse_draft(text: str, task_id: str) -> PriorAuthDraft:
    """Parse Claude's JSON output into PriorAuthDraft. Validates with Pydantic."""
    import json
    from datetime import datetime
    
    # Strip any accidental markdown fencing
    clean = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    
    try:
        data = json.loads(clean)
        data["task_id"] = task_id
        data["human_review_required"] = True  # Enforce invariant
        data["generated_at"] = datetime.utcnow().isoformat()
        return PriorAuthDraft.model_validate(data)
    except Exception as e:
        log.error("draft_parse_failed", task_id=task_id, error=str(e), raw_text=clean[:500])
        return _build_error_draft(task_id, f"Failed to parse agent output: {str(e)}")


def _build_error_draft(task_id: str, error_msg: str) -> PriorAuthDraft:
    """Return a minimal error draft when orchestration fails."""
    from shared.models.prior_auth import (
        PatientSummary, RequestedItemDetails, ClinicalJustification,
        ConfidenceLevel, MissingItem
    )
    from datetime import datetime
    
    return PriorAuthDraft(
        task_id=task_id,
        patient_summary=PatientSummary(
            patient_name="Unknown",
            patient_id="Unknown",
            primary_diagnosis="Unknown",
            icd10_code="Unknown"
        ),
        requested_item_details=RequestedItemDetails(item_name="Unknown"),
        clinical_justification=ClinicalJustification(
            diagnosis_meets_criteria=False,
            criteria_satisfied=[],
            criteria_not_satisfied=["Orchestration failed"],
            narrative=error_msg
        ),
        missing_items=[MissingItem(
            item="Complete clinical assessment",
            reason=error_msg,
            required_by="System",
            suggestion="Please retry the request"
        )],
        draft_letter="Prior authorization package generation failed. Please retry.",
        confidence_score=0.0,
        confidence_level=ConfidenceLevel.INSUFFICIENT,
        human_review_required=True,
        generated_at=datetime.utcnow(),
        warnings=[error_msg]
    )
```

---

## 3. CHAIN OF THOUGHT PROMPT ENGINEERING

### 3.1 System Prompt Builder

```python
# a2a_agent/prompts/system.py

def build_system_prompt() -> str:
    return """
You are AuthClear, a prior authorization copilot. You help physicians by preparing 
prior authorization documentation packages. You are an expert in ICD-10, CPT, HCPCS, 
RxNorm, and LOINC coding, and in payer-specific clinical criteria.

REASONING PROTOCOL — Follow this sequence for EVERY request:

STEP 1 — PARSE (no tools yet)
Think through: What is the patient's primary diagnosis? What are their current medications?
What labs are on file and how recent? What is being requested and why?

STEP 2 — RESOLVE CODES (use tools)
Call resolve_icd10 for each relevant diagnosis.
Call lookup_rxnorm for the requested drug and all current medications.
Call get_loinc_code for any lab tests mentioned.

STEP 3 — CHECK CRITERIA (use tools)
Call get_prior_auth_criteria with the correct CPT/HCPCS code.
Call check_drug_interactions with all relevant RxNorm IDs.

STEP 4 — GAP ANALYSIS (think, no tools)
Compare: what the payer requires vs. what the patient record contains.
Be precise about dates — a lab from 12 months ago may not meet "within 90 days" criteria.
List every gap explicitly. Do NOT omit gaps to make the request look stronger.

STEP 5 — GENERATE DRAFT (think + output)
Compute confidence score based on the rubric:
  - 0-20 pts: Patient demographics complete and verified
  - 0-20 pts: All diagnosis codes resolved
  - 0-40 pts: Payer criteria satisfied (each criterion = equal share)
  - 0-20 pts: All required documentation present

Write the draft_letter as a formal medical letter from physician to payer.
Include all satisfied criteria. Flag all gaps. Recommend next steps.

OUTPUT RULES:
- Return ONLY valid JSON. No markdown. No preamble.
- human_review_required MUST be true.
- missing_items MUST be populated for every gap found.
- confidence_score MUST be a float between 0.0 and 1.0.
- draft_letter MUST be complete enough for physician to review and sign.
"""
```

### 3.2 Prior Auth Draft Letter Template (for Claude's guidance)

```
The draft_letter should follow this structure:

[Date]
[Payer Name] Prior Authorization Department
[Payer Address if known]

RE: Prior Authorization Request for [Drug/Procedure]
Patient: [Name] | DOB: [Date] | Member ID: [If available]
Requesting Provider: [NPI if provided]

Dear Prior Authorization Reviewer,

I am requesting prior authorization for [drug/procedure] for my patient [name],
a [age]-year-old [gender] with [primary diagnosis].

CLINICAL SUMMARY:
[2-3 sentences on patient's relevant history and current condition]

MEDICAL NECESSITY:
[This patient meets/partially meets the following clinical criteria:]
[✅ Each met criterion with supporting data]
[⚠️  Each unmet criterion with explanation]

REQUESTED ITEM:
Drug/Procedure: [Name] | Code: [RxNorm/CPT/HCPCS]
Dose/Frequency: [If applicable]
Duration: [If applicable]
Prescribing Indication: [Clinical indication]

SUPPORTING DOCUMENTATION ENCLOSED:
[✅ List of available documentation]
[❌ List of missing documentation with note for physician]

[MISSING ITEMS NOTE — If any gaps:]
⚠️  This draft requires physician attention for the following items before submission:
[Numbered list of missing items with specific actions]

Respectfully,
[Physician signature block — TO BE COMPLETED BY PHYSICIAN]

[AUTHCLEAR NOTICE: This document was AI-generated as a draft for physician review.
 Human review required before submission. AuthClear v1.0.]
```

---

## 4. PROMPT TESTING CHECKLIST

Before shipping any prompt change, verify:

- [ ] Claude calls all 5 tools for a complete request (not skipping any)
- [ ] Claude does NOT hallucinate drug codes — it uses tool results
- [ ] Gap analysis is honest — missing items appear in `missing_items[]`
- [ ] `human_review_required` is always `true` in output JSON
- [ ] Confidence score reflects actual gap count (low gaps → high score)
- [ ] Draft letter is readable, professional, and includes all tool-derived data
- [ ] Error draft is returned gracefully if tool calls fail
- [ ] Output is valid JSON — no markdown fences, no preamble
