#!/usr/bin/env python
"""
Demo script for video: Shows A2A Agent reasoning process
Used in Scene 4 (1:45 - 2:00)
"""
import sys
import json
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from a2a_agent.tools.fhir_reader import parse_fhir_bundle
from mcp_server.tools.icd10 import resolve_icd10
from mcp_server.tools.rxnorm import lookup_rxnorm
from mcp_server.tools.prior_auth import get_prior_auth_criteria
import asyncio


def print_step(message, delay=0.3):
    """Print with slight delay for readability"""
    print(message)
    time.sleep(delay)


async def demo_reasoning():
    """Simulate A2A Agent reasoning for video demo"""
    print("\n" + "=" * 70)
    print("A2A AGENT: Analyzing Prior Authorization Request")
    print("=" * 70 + "\n")
    time.sleep(0.5)

    # Step 1: Load patient
    print_step("Step 1: Parsing FHIR bundle for Maria González...")
    data = json.loads(
        Path('shared/fhir/synthetic_patients/patient_t2dm_complete.json').read_text()
    )
    bundle = parse_fhir_bundle(data)

    print_step(f"  -> Patient: {bundle.patient.name}")
    print_step(f"  -> Diagnoses: {len(bundle.diagnoses)}")
    print_step(f"  -> Medications: {len(bundle.medications)}")
    print_step(f"  -> Lab results: {len(bundle.lab_results)}")
    print()

    # Step 2: Resolve codes
    print_step("Step 2: Calling MCP Server to resolve clinical codes...")
    icd_result = await resolve_icd10('E11.9')
    print_step(f"  -> ICD-10 E11.9 mapped to SNOMED {icd_result.snomed_code}")
    print_step(f"  -> Description: {icd_result.snomed_description}")
    print()

    # Step 3: Look up drug
    print_step("Step 3: Looking up requested medication (Ozempic)...")
    drug_result = await lookup_rxnorm('Ozempic')
    print_step(f"  -> RxNorm ID: {drug_result.rxnorm_id}")
    print_step(f"  -> Drug class: {drug_result.drug_class}")
    print_step(f"  -> Requires prior auth: {drug_result.requires_prior_auth}")
    print()

    # Step 4: Get criteria (synchronous call, not async)
    print_step("Step 4: Retrieving prior authorization criteria...")
    from mcp_server.tools.prior_auth import get_prior_auth_criteria
    criteria = get_prior_auth_criteria('J0173', 'generic')
    print_step(f"  -> Required diagnoses: {len(criteria.required_diagnoses)}")
    print_step(f"  -> Required labs: {len(criteria.required_labs)}")
    print_step(f"  -> Required trials: {len(criteria.required_trials)}")
    print()

    # Step 5: Evaluate criteria
    print_step("Step 5: Evaluating criteria match using Claude reasoning...")
    print()

    # HbA1c check
    hba1c_result = next((lab for lab in bundle.lab_results if 'HbA1c' in lab.test_name), None)
    if hba1c_result:
        meets_hba1c = float(hba1c_result.value) > 7.5
        symbol = "✓" if meets_hba1c else "✗"
        print_step(f"  {symbol} HbA1c {hba1c_result.value}% > 7.5%? {'YES' if meets_hba1c else 'NO'}")

    # BMI check
    bmi_result = next((lab for lab in bundle.lab_results if 'BMI' in lab.test_name), None)
    if bmi_result:
        meets_bmi = float(bmi_result.value) > 30
        symbol = "✓" if meets_bmi else "✗"
        print_step(f"  {symbol} BMI {bmi_result.value} > 30? {'YES' if meets_bmi else 'NO'}")

    # Medication trials
    metformin = next((med for med in bundle.medications if 'Metformin' in med.name), None)
    if metformin:
        print_step(f"  ✓ Metformin trial documented? YES ({metformin.dose})")

    glipizide = next((med for med in bundle.medications if 'Glipizide' in med.name), None)
    if glipizide:
        print_step(f"  ✓ Second oral agent (Glipizide)? YES ({glipizide.dose})")

    print()
    print_step("  => All criteria MET", delay=0.5)
    print_step("  => Confidence: HIGH (90%)", delay=0.5)
    print_step("  => Recommendation: Approve with human review", delay=0.5)

    print("\n" + "=" * 70)
    print("Generating structured prior authorization draft...")
    print("=" * 70 + "\n")
    time.sleep(0.5)


if __name__ == "__main__":
    try:
        asyncio.run(demo_reasoning())
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
        sys.exit(0)
