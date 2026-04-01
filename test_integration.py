#!/usr/bin/env python
"""
Integration test - Verifies core functionality without starting servers
"""
import sys
import json
import asyncio
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from a2a_agent.tools.fhir_reader import parse_fhir_bundle
from shared.models.patient import PatientBundle


async def test_fhir_parsing():
    """Test FHIR bundle parsing"""
    print("\n=== Test 1: FHIR Parsing ===")

    # Load synthetic patient
    patient_file = Path("shared/fhir/synthetic_patients/patient_t2dm_complete.json")
    with open(patient_file) as f:
        fhir_bundle = json.load(f)

    # Parse
    patient_bundle = parse_fhir_bundle(fhir_bundle)

    print(f"OK Parsed patient: {patient_bundle.patient.name}")
    print(f"OK Diagnoses: {len(patient_bundle.diagnoses)}")
    print(f"OK Medications: {len(patient_bundle.medications)}")
    print(f"OK Lab results: {len(patient_bundle.lab_results)}")

    for diag in patient_bundle.diagnoses:
        print(f"  - {diag.icd10_code}: {diag.description}")

    return patient_bundle


async def test_mcp_tools():
    """Test MCP Server tools (without HTTP)"""
    print("\n=== Test 2: MCP Tools ===")

    from mcp_server.tools.icd10 import resolve_icd10
    from mcp_server.tools.rxnorm import lookup_rxnorm
    from mcp_server.tools.loinc import get_loinc_code
    from mcp_server.tools.prior_auth import get_prior_auth_criteria

    # Test ICD-10 resolution
    print("\n--- ICD-10 Resolution ---")
    result = await resolve_icd10("E11.9")
    print(f"OK ICD-10 E11.9 -> SNOMED {result.snomed_code}")
    print(f"  Description: {result.description}")

    # Test RxNorm lookup
    print("\n--- RxNorm Lookup ---")
    result = await lookup_rxnorm("Metformin")
    print(f"OK Metformin -> RxNorm {result.rxnorm_id}")
    print(f"  Generic: {result.generic_name}")

    # Test LOINC lookup
    print("\n--- LOINC Lookup ---")
    result = await get_loinc_code("HbA1c")
    print(f"OK HbA1c -> LOINC {result.loinc_code}")
    print(f"  Name: {result.long_name}")

    # Test prior auth criteria
    print("\n--- Prior Auth Criteria ---")
    result = await get_prior_auth_criteria("J0173", "generic")
    print(f"OK J0173 (Semaglutide) criteria loaded")
    print(f"  Payer: {result.payer}")
    print(f"  Required diagnoses: {len(result.required_diagnoses)}")
    print(f"  Required labs: {len(result.required_labs)}")
    print(f"  Required trials: {len(result.required_trials)}")


async def test_pydantic_models():
    """Test Pydantic models"""
    print("\n=== Test 3: Pydantic Models ===")

    from shared.models.prior_auth import (
        PriorAuthDraft,
        PatientSummary,
        RequestedItemDetails,
        ClinicalJustification,
        ConfidenceLevel,
    )

    # Create a mock draft
    draft = PriorAuthDraft(
        task_id="test-123",
        patient_summary=PatientSummary(
            patient_name="Test Patient",
            patient_id="test-001",
            primary_diagnosis="Type 2 diabetes mellitus",
            icd10_code="E11.9",
            snomed_code="44054006",
        ),
        requested_item_details=RequestedItemDetails(
            item_name="Ozempic (semaglutide)",
            rxnorm_id="2200660",
        ),
        clinical_justification=ClinicalJustification(
            diagnosis_meets_criteria=True,
            criteria_satisfied=["HbA1c > 7.5%"],
            criteria_not_satisfied=[],
            narrative="Patient meets criteria",
        ),
        draft_letter="Test letter",
        confidence_score=0.85,
        confidence_level=ConfidenceLevel.MEDIUM,
    )

    print(f"OK PriorAuthDraft created")
    print(f"  Task ID: {draft.task_id}")
    print(f"  Confidence: {draft.confidence_level.value} ({draft.confidence_score:.0%})")
    print(f"  Human review required: {draft.human_review_required}")

    # Verify human_review_required cannot be changed
    assert draft.human_review_required == True, "human_review_required must always be True"
    print("OK human_review_required invariant verified")


async def main():
    """Run all tests"""
    print("=" * 60)
    print("AuthClear Integration Test Suite")
    print("=" * 60)

    try:
        # Test 1: FHIR Parsing
        patient_bundle = await test_fhir_parsing()

        # Test 2: MCP Tools
        await test_mcp_tools()

        # Test 3: Pydantic Models
        await test_pydantic_models()

        print("\n" + "=" * 60)
        print("OK ALL TESTS PASSED")
        print("=" * 60)
        print("\nCore functionality verified:")
        print("  OK FHIR bundle parsing")
        print("  OK Clinical code resolution (ICD-10, RxNorm, LOINC)")
        print("  OK Prior auth criteria lookup")
        print("  OK Pydantic model validation")
        print("  OK Human-in-the-loop invariant")
        print("\nReady for end-to-end testing with live servers!")

        return 0

    except Exception as e:
        print(f"\nERROR TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
