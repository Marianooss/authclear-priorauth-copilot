#!/usr/bin/env python
"""
Test all 5 synthetic FHIR patients
"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from a2a_agent.tools.fhir_reader import parse_fhir_bundle


def test_all_patients():
    """Test parsing all 5 synthetic patients"""
    patient_files = [
        ("patient_t2dm_complete.json", "Maria González", "Type 2 DM - Complete criteria"),
        ("patient_t2dm_gaps.json", "John Smith", "Type 2 DM - Missing criteria"),
        ("patient_rheumatoid_humira.json", "Sarah Johnson", "Rheumatoid Arthritis -> Humira"),
        ("patient_obesity_ozempic.json", "Robert Chen", "Obesity -> Ozempic (weight loss)"),
        ("patient_cardiac_eliquis.json", "William Martinez", "Atrial Fibrillation -> Eliquis"),
    ]

    print("=" * 70)
    print("Testing All Synthetic FHIR Patients")
    print("=" * 70)

    all_passed = True

    for filename, expected_name, scenario in patient_files:
        print(f"\n--- {filename} ---")
        print(f"Scenario: {scenario}")

        try:
            # Load file
            file_path = Path(f"shared/fhir/synthetic_patients/{filename}")
            with open(file_path) as f:
                fhir_bundle = json.load(f)

            # Parse
            patient_bundle = parse_fhir_bundle(fhir_bundle)

            # Verify
            print(f"OK Patient: {patient_bundle.patient.name}")
            print(f"   DOB: {patient_bundle.patient.birth_date}")
            print(f"   Gender: {patient_bundle.patient.gender}")
            print(f"   Diagnoses: {len(patient_bundle.diagnoses)}")
            for diag in patient_bundle.diagnoses:
                print(f"     - {diag.icd10_code}: {diag.description}")
            print(f"   Medications: {len(patient_bundle.medications)}")
            for med in patient_bundle.medications:
                print(f"     - {med.name} {med.dose}")
            print(f"   Lab results: {len(patient_bundle.lab_results)}")
            for lab in patient_bundle.lab_results[:3]:  # Show first 3
                print(f"     - {lab.test_name}: {lab.value} {lab.unit}")
            print(f"   Allergies: {len(patient_bundle.allergies)}")

            # Verify expected name matches
            if expected_name.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u") in patient_bundle.patient.name or expected_name in patient_bundle.patient.name:
                print(f"OK Name verification passed")
            else:
                print(f"ERROR Name mismatch: expected '{expected_name}', got '{patient_bundle.patient.name}'")
                all_passed = False

        except Exception as e:
            print(f"ERROR Failed to parse: {e}")
            import traceback
            traceback.print_exc()
            all_passed = False

    print("\n" + "=" * 70)
    if all_passed:
        print("OK ALL 5 PATIENTS PARSED SUCCESSFULLY")
        print("=" * 70)
        print("\nPatients available for testing:")
        for filename, name, scenario in patient_files:
            print(f"  - {name}: {scenario}")
        return 0
    else:
        print("ERROR SOME PATIENTS FAILED TO PARSE")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    exit_code = test_all_patients()
    sys.exit(exit_code)
