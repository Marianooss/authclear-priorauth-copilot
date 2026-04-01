"""
a2a_agent/orchestrator.py — Prior Auth ReAct orchestrator

Core ReAct loop that coordinates Claude API with MCP Server tools.
Generates complete PriorAuthDraft outputs.
"""

from __future__ import annotations

import asyncio
import time
import json
import hashlib
from datetime import datetime
import structlog

from a2a_agent.config import settings
from a2a_agent.claude_client import get_claude_client
from a2a_agent.models import Task, TaskState
from a2a_agent.tools.mcp_client import MCPClient
from a2a_agent.tools.fhir_reader import parse_fhir_bundle, FHIRParseError
from a2a_agent.prompts.system import build_system_prompt
from a2a_agent.prompts.prior_auth import PRIOR_AUTH_LETTER_TEMPLATE
from shared.models.prior_auth import (
    PriorAuthDraft,
    PatientSummary,
    RequestedItemDetails,
    ClinicalJustification,
    SupportingDoc,
    MissingItem,
    ConfidenceLevel,
    ConfidenceBreakdown,
)

log = structlog.get_logger()


# Anthropic tool definitions for Claude API
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


async def run_prior_auth_orchestration(task: Task, mcp: MCPClient) -> Task:
    """
    Main ReAct loop for prior auth generation.

    Pattern:
        1. Parse FHIR bundle
        2. Build initial message with patient context
        3. Claude thinks + calls tools (ReAct loop)
        4. Execute tools against MCP Server
        5. Feed tool results back to Claude
        6. Repeat until Claude produces final JSON
        7. Parse and validate as PriorAuthDraft

    Args:
        task: Task with input data
        mcp: MCP client for tool calls

    Returns:
        Updated task with result or error

    Side effects:
        - Updates task.state
        - Sets task.result on success
        - Sets task.error on failure
    """
    start_time = time.monotonic()
    task_input = task.input

    log.info("orchestration_started", task_id=task.id, requested_item=task_input.requested_item)

    try:
        # Parse FHIR bundle
        try:
            patient_bundle = parse_fhir_bundle(task_input.fhir_bundle)
        except FHIRParseError as e:
            log.error("fhir_parse_failed", task_id=task.id, error=str(e))
            task.state = TaskState.FAILED
            task.error = f"FHIR parse error: {e.message}"
            return task

        # Build initial message
        user_message = _build_initial_message(task_input, patient_bundle)
        messages = [{"role": "user", "content": user_message}]

        # Initialize Claude client (Anthropic or Bedrock)
        client = get_claude_client()
        system_prompt = build_system_prompt()

        # Track tool calls for audit log
        tool_calls_log = []

        # ReAct loop
        max_iterations = settings.max_tool_iterations
        iteration = 0

        while iteration < max_iterations:
            iteration += 1
            log.debug("react_iteration", task_id=task.id, iteration=iteration)

            # ── THINK (Claude reasons) ──
            response = await client.create_message(
                model=settings.claude_model,
                max_tokens=settings.claude_max_tokens,
                temperature=settings.claude_temperature,
                system=system_prompt,
                tools=TOOL_DEFINITIONS,
                messages=messages,
            )

            log.debug(
                "llm_response",
                task_id=task.id,
                stop_reason=response.stop_reason,
                content_blocks=len(response.content),
            )

            # Append assistant response to history (convert ContentBlocks to dicts)
            content_dicts = _content_blocks_to_dicts(response.content)
            messages.append({"role": "assistant", "content": content_dicts})

            # ── TERMINAL: No more tool calls → parse final output ──
            if response.stop_reason == "end_turn":
                # Extract final JSON from response
                final_json = _extract_final_json(response.content)
                if final_json:
                    # Add tool calls log and fhir_bundle to data for hash calculation
                    final_json["tool_calls_made"] = tool_calls_log
                    final_json["fhir_bundle"] = task_input.fhir_bundle
                    final_json["payer"] = task_input.payer
                    final_json["urgency"] = task_input.urgency

                    draft = _build_prior_auth_draft(task.id, final_json, patient_bundle)
                    task.result = draft
                    task.state = TaskState.COMPLETED
                    elapsed = time.monotonic() - start_time
                    log.info(
                        "orchestration_completed",
                        task_id=task.id,
                        confidence=draft.confidence_score,
                        duration_s=f"{elapsed:.2f}",
                    )
                    return task
                else:
                    log.error("no_json_in_final_output", task_id=task.id)
                    task.state = TaskState.FAILED
                    task.error = "Agent did not produce valid JSON output"
                    return task

            # ── ACT: Execute tool calls ──
            if response.stop_reason == "tool_use":
                tool_results = []
                for content_block in response.content:
                    if content_block.type == "tool_use":
                        tool_name = content_block.name
                        tool_input = content_block.input
                        tool_use_id = content_block.id

                        log.info("executing_tool", task_id=task.id, tool=tool_name, input=tool_input)

                        # Track tool call for audit log
                        tool_calls_log.append(f"{tool_name}({json.dumps(tool_input)})")

                        # Execute tool
                        result = await _execute_tool(mcp, tool_name, tool_input)

                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": tool_use_id,
                            "content": json.dumps(result),
                        })

                # Feed tool results back to Claude
                messages.append({"role": "user", "content": tool_results})

        # Max iterations reached
        log.error("max_iterations_reached", task_id=task.id)
        task.state = TaskState.FAILED
        task.error = f"Max iterations ({max_iterations}) reached without completion"
        return task

    except Exception as e:
        log.error("orchestration_failed", task_id=task.id, error=str(e), exc_info=True)
        task.state = TaskState.FAILED
        task.error = f"Orchestration error: {str(e)}"
        return task


def _build_initial_message(task_input, patient_bundle) -> str:
    """Build the initial user message with patient context."""
    return f"""Generate a prior authorization draft for the following patient:

PATIENT INFORMATION:
- Name: {patient_bundle.patient.name}
- ID: {patient_bundle.patient.id}
- DOB: {patient_bundle.patient.birth_date}
- Gender: {patient_bundle.patient.gender}

DIAGNOSES:
{chr(10).join(f"- {d.icd10_code}: {d.description} (status: {d.status})" for d in patient_bundle.diagnoses)}

CURRENT MEDICATIONS:
{chr(10).join(f"- {m.name} {m.dose} {m.frequency}" for m in patient_bundle.medications)}

LAB RESULTS:
{chr(10).join(f"- {l.test_name}: {l.value} {l.unit} (date: {l.date})" for l in patient_bundle.lab_results)}

ALLERGIES:
{chr(10).join(f"- {a}" for a in patient_bundle.allergies) if patient_bundle.allergies else "- None documented"}

REQUESTED ITEM: {task_input.requested_item}
PAYER: {task_input.payer}
URGENCY: {task_input.urgency}

{f"ADDITIONAL CONTEXT: {task_input.additional_context}" if task_input.additional_context else ""}

Please:
1. Use the terminology tools to resolve all clinical codes
2. Get the prior auth criteria for this medication/procedure
3. Compare the patient record against the criteria
4. Generate a complete PriorAuthDraft JSON object with all required fields
5. Flag any missing documentation or gaps in the criteria
"""


def calculate_confidence_breakdown(data: dict, patient_bundle) -> tuple[list[ConfidenceBreakdown], float]:
    """
    Calculate confidence score deterministically using agents.md Section 4 rubric.

    Section weights:
        - Patient demographics: 10%
        - Diagnosis mapping: 20%
        - Criteria satisfaction: 40%
        - Documentation completeness: 30%

    Args:
        data: Draft data from Claude (with gap analysis)
        patient_bundle: Parsed FHIR bundle

    Returns:
        Tuple of (breakdown_list, total_score) where total_score is 0.0-1.0
    """
    breakdown = []
    total_score = 0.0

    # ── SECTION 1: Patient demographics (10 pts) ──
    demo_score = 10.0
    demo_rationale = "Complete demographics present"
    patient_summary = data.get("patient_summary", {})
    if not patient_summary.get("patient_name"):
        demo_score -= 3.0
        demo_rationale = "Missing patient name"
    if not patient_summary.get("patient_id"):
        demo_score -= 3.0
        demo_rationale += ", missing ID"
    if not patient_bundle.patient.birth_date:
        demo_score -= 2.0
        demo_rationale += ", missing DOB"
    if not patient_bundle.patient.gender:
        demo_score -= 2.0
        demo_rationale += ", missing gender"

    breakdown.append(ConfidenceBreakdown(
        section="patient_demographics",
        sub_score=demo_score,
        max_score=10.0,
        rationale=demo_rationale.strip(", ")
    ))
    total_score += demo_score

    # ── SECTION 2: Diagnosis mapping (20 pts) ──
    diag_score = 0.0
    diag_rationale = ""
    icd10_code = patient_summary.get("icd10_code", "")
    snomed_code = patient_summary.get("snomed_code", "")

    if snomed_code and icd10_code:
        diag_score = 20.0
        diag_rationale = f"ICD-10 {icd10_code} resolved to SNOMED {snomed_code}"
    elif icd10_code:
        diag_score = 12.0
        diag_rationale = f"ICD-10 {icd10_code} present but unresolved"
    else:
        diag_score = 0.0
        diag_rationale = "Diagnosis missing or incomplete"

    breakdown.append(ConfidenceBreakdown(
        section="diagnosis_mapping",
        sub_score=diag_score,
        max_score=20.0,
        rationale=diag_rationale
    ))
    total_score += diag_score

    # ── SECTION 3: Criteria satisfaction (40 pts) ──
    criteria_score = 0.0
    criteria_rationale = ""
    clinical_just = data.get("clinical_justification", {})
    criteria_met = clinical_just.get("criteria_satisfied", [])
    criteria_not_met = clinical_just.get("criteria_not_satisfied", [])
    total_criteria = len(criteria_met) + len(criteria_not_met)

    if total_criteria > 0:
        points_per_criterion = 40.0 / total_criteria
        criteria_score = len(criteria_met) * points_per_criterion
        criteria_rationale = f"{len(criteria_met)}/{total_criteria} criteria satisfied"
    else:
        criteria_score = 0.0
        criteria_rationale = "No criteria evaluated"

    breakdown.append(ConfidenceBreakdown(
        section="criteria_satisfaction",
        sub_score=criteria_score,
        max_score=40.0,
        rationale=criteria_rationale
    ))
    total_score += criteria_score

    # ── SECTION 4: Documentation completeness (30 pts) ──
    doc_score = 0.0
    doc_rationale = ""
    supporting_docs = data.get("supporting_documentation", [])
    missing_items = data.get("missing_items", [])
    total_docs_required = len(supporting_docs) + len(missing_items)

    if total_docs_required > 0:
        # Count auto-populated docs
        auto_populated = sum(1 for doc in supporting_docs if doc.get("status") == "present")
        points_per_doc = 30.0 / total_docs_required
        doc_score = auto_populated * points_per_doc
        doc_rationale = f"{auto_populated}/{total_docs_required} docs auto-populated, {len(missing_items)} missing"
    else:
        doc_score = 30.0
        doc_rationale = "No documentation requirements identified"

    breakdown.append(ConfidenceBreakdown(
        section="documentation_completeness",
        sub_score=doc_score,
        max_score=30.0,
        rationale=doc_rationale
    ))
    total_score += doc_score

    # Normalize to 0.0-1.0
    normalized_score = total_score / 100.0

    return breakdown, normalized_score


async def _execute_tool(mcp: MCPClient, tool_name: str, tool_input: dict) -> dict:
    """
    Execute a tool against the MCP Server.

    Implements retry with exponential backoff per agents.md Section 7:
    - Retry 3× with backoff: 1s, 2s, 4s
    - Return structured error if all retries fail
    """
    max_retries = 3
    backoff_delays = [1.0, 2.0, 4.0]  # Exponential backoff in seconds

    last_error = None

    for attempt in range(max_retries):
        try:
            # Execute tool based on name
            if tool_name == "resolve_icd10":
                result = await mcp.resolve_icd10(tool_input["code"])
                return result.model_dump()

            elif tool_name == "lookup_rxnorm":
                result = await mcp.lookup_rxnorm(tool_input["drug_name"])
                return result.model_dump()

            elif tool_name == "check_drug_interactions":
                result = await mcp.check_drug_interactions(tool_input["rxnorm_ids"])
                return result.model_dump()

            elif tool_name == "get_loinc_code":
                result = await mcp.get_loinc_code(tool_input["test_name"])
                return result.model_dump()

            elif tool_name == "get_prior_auth_criteria":
                cpt_code = tool_input["cpt_code"]
                payer = tool_input.get("payer", "generic")
                result = await mcp.get_prior_auth_criteria(cpt_code, payer)
                return result.model_dump()

            else:
                return {"error": f"Unknown tool: {tool_name}"}

        except Exception as e:
            last_error = e
            log.warning(
                "tool_execution_retry",
                tool=tool_name,
                attempt=attempt + 1,
                max_retries=max_retries,
                error=str(e)
            )

            # If not last attempt, wait with exponential backoff
            if attempt < max_retries - 1:
                delay = backoff_delays[attempt]
                log.debug("retry_backoff", delay_seconds=delay)
                await asyncio.sleep(delay)
            else:
                # All retries exhausted
                log.error(
                    "tool_execution_failed_all_retries",
                    tool=tool_name,
                    error=str(last_error)
                )
                return {
                    "error": f"Tool {tool_name} failed after {max_retries} retries: {str(last_error)}",
                    "retries_attempted": max_retries
                }

    # Should never reach here, but return error just in case
    return {"error": f"Unexpected error in tool execution: {tool_name}"}


def _content_blocks_to_dicts(content_blocks) -> list[dict]:
    """Convert ContentBlock objects to dictionaries for JSON serialization."""
    result = []
    for block in content_blocks:
        if block.type == "text":
            result.append({"type": "text", "text": block.text})
        elif block.type == "tool_use":
            result.append({
                "type": "tool_use",
                "id": block.id,
                "name": block.name,
                "input": block.input
            })
    return result


def _extract_final_json(content_blocks) -> dict | None:
    """Extract JSON from Claude's final response."""
    for block in content_blocks:
        if block.type == "text":
            text = block.text
            # Try to find JSON in the text
            try:
                # Look for JSON object
                start = text.find("{")
                end = text.rfind("}") + 1
                if start >= 0 and end > start:
                    json_str = text[start:end]
                    return json.loads(json_str)
            except json.JSONDecodeError:
                continue
    return None


def _build_prior_auth_draft(task_id: str, data: dict, patient_bundle) -> PriorAuthDraft:
    """
    Build PriorAuthDraft from Claude's JSON output.

    Uses deterministic confidence calculation per agents.md Section 4.
    """
    # Calculate confidence score deterministically (agents.md Section 4)
    breakdown, score = calculate_confidence_breakdown(data, patient_bundle)

    # Map confidence score to level
    if score >= 0.90:
        level = ConfidenceLevel.HIGH
    elif score >= 0.70:
        level = ConfidenceLevel.MEDIUM
    elif score >= 0.50:
        level = ConfidenceLevel.LOW
    else:
        level = ConfidenceLevel.INSUFFICIENT

    # Calculate FHIR bundle hash for audit trail
    bundle_json = json.dumps(data.get("fhir_bundle", {}), sort_keys=True)
    bundle_hash = hashlib.sha256(bundle_json.encode()).hexdigest()

    # Extract tool calls made from data (if Claude tracked them)
    tool_calls_made = data.get("tool_calls_made", [])

    return PriorAuthDraft(
        task_id=task_id,
        schema_version="2.0",
        patient_summary=PatientSummary(**data.get("patient_summary", {})),
        requested_item_details=RequestedItemDetails(**data.get("requested_item_details", {})),
        clinical_justification=ClinicalJustification(**data.get("clinical_justification", {})),
        supporting_documentation=[
            SupportingDoc(**doc) for doc in data.get("supporting_documentation", [])
        ],
        missing_items=[MissingItem(**item) for item in data.get("missing_items", [])],
        confidence_breakdown=breakdown,
        confidence_score=score,
        confidence_level=level,
        draft_letter=data.get("draft_letter", ""),
        drug_interactions=data.get("drug_interactions", []),
        human_review_required=True,
        payer=data.get("payer", "generic"),
        urgency=data.get("urgency", "standard"),
        generated_at=datetime.utcnow(),
        model_version="claude-sonnet-4-20250514",
        fhir_bundle_hash=bundle_hash,
        tool_calls_made=tool_calls_made,
        warnings=data.get("warnings", []),
    )
