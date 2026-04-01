#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test Real Backend End-to-End

Tests the full flow: FHIR bundle -> A2A Agent -> Claude API -> MCP Server -> Result
"""
import asyncio
import json
import httpx
from pathlib import Path
import sys

# Force UTF-8 encoding for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Load a patient FHIR bundle
PATIENT_FILE = Path(__file__).parent / "shared" / "fhir" / "synthetic_patients" / "patient_breast_cancer.json"

async def test_backend():
    """Test the real backend with Linda Thompson (breast cancer)."""

    print("=" * 80)
    print("  AuthClear Backend End-to-End Test")
    print("=" * 80)
    print()

    # Load FHIR bundle
    print(f"[1/5] Loading FHIR bundle from {PATIENT_FILE.name}...")
    with open(PATIENT_FILE, "r") as f:
        fhir_bundle = json.load(f)
    print(f"      [OK] Loaded {len(fhir_bundle.get('entry', []))} FHIR resources")
    print()

    # Check MCP Server health
    print("[2/5] Checking MCP Server (http://localhost:8001/health)...")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get("http://localhost:8001/health")
            if response.status_code == 200:
                print(f"      [OK] MCP Server is healthy")
            else:
                print(f"      [ERROR] MCP Server returned {response.status_code}")
                return
    except Exception as e:
        print(f"      [ERROR] MCP Server not reachable: {e}")
        print()
        print("      Please start MCP Server first:")
        print("      python run_mcp_http_server.py")
        return
    print()

    # Check A2A Agent health
    print("[3/5] Checking A2A Agent (http://localhost:8000/health)...")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get("http://localhost:8000/health")
            if response.status_code == 200:
                print(f"      [OK] A2A Agent is healthy")
            else:
                print(f"      [ERROR] A2A Agent returned {response.status_code}")
                return
    except Exception as e:
        print(f"      [ERROR] A2A Agent not reachable: {e}")
        print()
        print("      Please start A2A Agent first:")
        print("      python run_a2a_agent.py")
        return
    print()

    # Send task to A2A Agent
    print("[4/5] Sending prior auth request to A2A Agent...")
    print("      Patient: Linda Thompson")
    print("      Medication: Herceptin (trastuzumab)")
    print("      Payer: BCBS")
    print()
    print("      This will take 10-30 seconds (Claude API reasoning)...")
    print()

    request_payload = {
        "message": {
            "role": "user",
            "content": json.dumps({
                "fhir_bundle": fhir_bundle,
                "requested_item": "Herceptin (trastuzumab) - J9355",
                "payer": "bcbs",
                "urgency": "standard"
            })
        }
    }

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                "http://localhost:8000/tasks/send",
                json=request_payload,
                headers={"Content-Type": "application/json"}
            )

            if response.status_code != 200:
                print(f"      [ERROR] A2A Agent returned {response.status_code}")
                print(f"      Response: {response.text}")
                return

            result = response.json()
            print(f"      [OK] Request completed")
    except Exception as e:
        print(f"      [ERROR] Request failed: {e}")
        return
    print()

    # Display results
    print("[5/5] Results:")
    print("=" * 80)

    task = result.get("task", {})
    task_result = task.get("result")

    if task_result:
        patient_summary = task_result.get("patient_summary", {})
        requested_item = task_result.get("requested_item_details", {})
        justification = task_result.get("clinical_justification", {})
        confidence = task_result.get("confidence_score", 0)
        confidence_level = task_result.get("confidence_level", "unknown")
        missing_items = task_result.get("missing_items", [])

        print(f"Patient: {patient_summary.get('patient_name', 'N/A')}")
        print(f"Primary Diagnosis: {patient_summary.get('primary_diagnosis', 'N/A')}")
        print(f"ICD-10: {patient_summary.get('icd10_code', 'N/A')}")
        print()
        print(f"Requested Item: {requested_item.get('item_name', 'N/A')}")
        print(f"Drug Class: {requested_item.get('drug_class', 'N/A')}")
        print()
        print(f"Confidence: {confidence_level.upper()} ({confidence * 100:.0f}%)")
        print()
        print(f"Criteria Satisfied: {len(justification.get('criteria_satisfied', []))}")
        for criteria in justification.get('criteria_satisfied', []):
            print(f"  [+] {criteria}")
        print()
        print(f"Criteria Not Satisfied: {len(justification.get('criteria_not_satisfied', []))}")
        for criteria in justification.get('criteria_not_satisfied', []):
            print(f"  [-] {criteria}")
        print()
        print(f"Missing Items: {len(missing_items)}")
        for item in missing_items:
            print(f"  [!] {item.get('item', 'N/A')}: {item.get('reason', 'N/A')}")
        print()
        print("Clinical Justification:")
        print(f"  {justification.get('narrative', 'N/A')}")
        print()
        print("=" * 80)
        print("[SUCCESS] Backend is working correctly!")
        print()
        print("You can now use the Web UI with real backend processing.")

    else:
        print(f"Task State: {task.get('state', 'unknown')}")
        if task.get('error'):
            print(f"Error: {task.get('error')}")
        print()
        print("=" * 80)
        print("[WARNING] Task did not complete successfully")


if __name__ == "__main__":
    asyncio.run(test_backend())
