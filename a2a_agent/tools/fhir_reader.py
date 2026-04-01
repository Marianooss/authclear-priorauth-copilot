"""
a2a_agent/tools/fhir_reader.py — FHIR R4 Bundle parser

Pure function to parse FHIR R4 Bundle JSON into PatientBundle model.
No I/O, no external calls - pure data transformation.
"""

from __future__ import annotations

from datetime import datetime
import structlog

from shared.models.patient import (
    PatientBundle,
    PatientDemographics,
    Diagnosis,
    Medication,
    LabResult,
)

log = structlog.get_logger()


class FHIRParseError(Exception):
    """Raised when FHIR bundle cannot be parsed."""

    def __init__(self, message: str, details: dict | None = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


def parse_fhir_bundle(raw_bundle: dict) -> PatientBundle:
    """
    Parse FHIR R4 Bundle JSON into PatientBundle model.

    Args:
        raw_bundle: FHIR R4 Bundle as dict

    Returns:
        PatientBundle with all extracted data

    Raises:
        FHIRParseError: If bundle structure is invalid or required data missing

    Handles:
        - Patient resource
        - Condition resources (diagnoses)
        - MedicationRequest resources
        - Observation resources (lab results)
        - AllergyIntolerance resources
    """
    log.info("parsing_fhir_bundle")

    # Validate bundle structure
    if not isinstance(raw_bundle, dict):
        raise FHIRParseError("Bundle must be a dictionary")

    if raw_bundle.get("resourceType") != "Bundle":
        raise FHIRParseError(
            f"Expected resourceType 'Bundle', got '{raw_bundle.get('resourceType')}'"
        )

    entries = raw_bundle.get("entry", [])
    if not entries:
        raise FHIRParseError("Bundle has no entries")

    # Extract resources by type
    patient_resource = None
    condition_resources = []
    medication_resources = []
    observation_resources = []
    allergy_resources = []

    for entry in entries:
        resource = entry.get("resource", {})
        resource_type = resource.get("resourceType")

        if resource_type == "Patient":
            patient_resource = resource
        elif resource_type == "Condition":
            condition_resources.append(resource)
        elif resource_type == "MedicationRequest":
            medication_resources.append(resource)
        elif resource_type == "Observation":
            observation_resources.append(resource)
        elif resource_type == "AllergyIntolerance":
            allergy_resources.append(resource)

    # Parse patient (required)
    if not patient_resource:
        raise FHIRParseError("No Patient resource found in bundle")

    try:
        patient = _parse_patient(patient_resource)
    except Exception as e:
        raise FHIRParseError(f"Failed to parse Patient: {str(e)}", {"resource": patient_resource})

    # Parse conditions
    diagnoses = []
    for condition in condition_resources:
        try:
            diagnosis = _parse_condition(condition)
            if diagnosis:
                diagnoses.append(diagnosis)
        except Exception as e:
            log.warning("condition_parse_failed", error=str(e), resource_id=condition.get("id"))

    # Parse medications
    medications = []
    for med_request in medication_resources:
        try:
            medication = _parse_medication_request(med_request)
            if medication:
                medications.append(medication)
        except Exception as e:
            log.warning("medication_parse_failed", error=str(e), resource_id=med_request.get("id"))

    # Parse observations (lab results)
    lab_results = []
    for observation in observation_resources:
        try:
            lab = _parse_observation(observation)
            if lab:
                lab_results.append(lab)
        except Exception as e:
            log.warning("observation_parse_failed", error=str(e), resource_id=observation.get("id"))

    # Parse allergies
    allergies = []
    for allergy in allergy_resources:
        try:
            allergy_name = _parse_allergy(allergy)
            if allergy_name:
                allergies.append(allergy_name)
        except Exception as e:
            log.warning("allergy_parse_failed", error=str(e), resource_id=allergy.get("id"))

    log.info(
        "fhir_bundle_parsed",
        patient_id=patient.id,
        diagnoses=len(diagnoses),
        medications=len(medications),
        labs=len(lab_results),
        allergies=len(allergies),
    )

    return PatientBundle(
        patient=patient,
        diagnoses=diagnoses,
        medications=medications,
        lab_results=lab_results,
        allergies=allergies,
        raw_fhir=raw_bundle,
    )


def _parse_patient(resource: dict) -> PatientDemographics:
    """Parse FHIR Patient resource."""
    patient_id = resource.get("id", "unknown")

    # Extract name
    names = resource.get("name", [])
    if names and len(names) > 0:
        name_obj = names[0]
        name = name_obj.get("text") or f"{name_obj.get('given', [''])[0]} {name_obj.get('family', '')}"
    else:
        name = "Unknown"

    # Extract birth date
    birth_date_str = resource.get("birthDate")
    if birth_date_str:
        birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d").date()
    else:
        raise FHIRParseError("Patient birthDate is required")

    gender = resource.get("gender", "unknown")

    return PatientDemographics(
        id=patient_id,
        name=name.strip(),
        birth_date=birth_date,
        gender=gender,
    )


def _parse_condition(resource: dict) -> Diagnosis | None:
    """Parse FHIR Condition resource."""
    # Extract ICD-10 code
    code_obj = resource.get("code", {})
    codings = code_obj.get("coding", [])

    icd10_code = None
    description = code_obj.get("text", "")

    for coding in codings:
        system = coding.get("system", "")
        if "icd-10" in system.lower():
            icd10_code = coding.get("code")
            if not description:
                description = coding.get("display", "")
            break

    if not icd10_code:
        return None

    # Extract onset date
    onset_str = resource.get("onsetDateTime") or resource.get("recordedDate")
    onset_date = None
    if onset_str:
        try:
            onset_date = datetime.fromisoformat(onset_str.replace("Z", "+00:00")).date()
        except:
            pass

    # Extract status
    clinical_status = resource.get("clinicalStatus", {})
    status_codings = clinical_status.get("coding", [])
    status = "active"
    if status_codings:
        status = status_codings[0].get("code", "active")

    return Diagnosis(
        icd10_code=icd10_code,
        description=description,
        onset_date=onset_date,
        status=status,
    )


def _parse_medication_request(resource: dict) -> Medication | None:
    """Parse FHIR MedicationRequest resource."""
    # Extract medication name
    medication_obj = resource.get("medicationCodeableConcept") or resource.get("medicationReference", {})

    name = ""
    rxnorm_id = None

    if isinstance(medication_obj, dict):
        name = medication_obj.get("text", "")
        codings = medication_obj.get("coding", [])
        for coding in codings:
            if "rxnorm" in coding.get("system", "").lower():
                rxnorm_id = coding.get("code")
            if not name:
                name = coding.get("display", "")

    if not name:
        return None

    # Extract dosage
    dosage_instructions = resource.get("dosageInstruction", [])
    dose = ""
    frequency = ""

    if dosage_instructions:
        dosage = dosage_instructions[0]
        dose_quantity = dosage.get("doseAndRate", [{}])[0].get("doseQuantity", {})
        dose = f"{dose_quantity.get('value', '')}{dose_quantity.get('unit', '')}"

        timing = dosage.get("timing", {})
        repeat = timing.get("repeat", {})
        frequency_val = repeat.get("frequency", 1)
        period = repeat.get("period", 1)
        period_unit = repeat.get("periodUnit", "d")
        frequency = f"{frequency_val} time(s) per {period} {period_unit}"

        if not dose:
            dose = dosage.get("text", "as directed")

    # Extract start date
    authored_on = resource.get("authoredOn")
    start_date = None
    if authored_on:
        try:
            start_date = datetime.fromisoformat(authored_on.replace("Z", "+00:00")).date()
        except:
            pass

    # Extract status
    status = resource.get("status", "active")

    return Medication(
        name=name,
        rxnorm_id=rxnorm_id,
        dose=dose or "as directed",
        frequency=frequency or "as directed",
        start_date=start_date,
        status=status,
    )


def _parse_observation(resource: dict) -> LabResult | None:
    """Parse FHIR Observation resource (lab results)."""
    # Extract test name and LOINC code
    code_obj = resource.get("code", {})
    test_name = code_obj.get("text", "")
    loinc_code = None

    codings = code_obj.get("coding", [])
    for coding in codings:
        if "loinc" in coding.get("system", "").lower():
            loinc_code = coding.get("code")
            if not test_name:
                test_name = coding.get("display", "")

    if not test_name:
        return None

    # Extract value
    value_quantity = resource.get("valueQuantity", {})
    value = value_quantity.get("value")

    if value is None:
        return None

    unit = value_quantity.get("unit", "")

    # Extract reference range
    reference_ranges = resource.get("referenceRange", [])
    reference_range = None
    if reference_ranges:
        ref = reference_ranges[0]
        low = ref.get("low", {}).get("value")
        high = ref.get("high", {}).get("value")
        if low is not None and high is not None:
            reference_range = f"{low}-{high}"

    # Extract date
    effective_date_str = resource.get("effectiveDateTime") or resource.get("issued")
    if not effective_date_str:
        return None

    try:
        date = datetime.fromisoformat(effective_date_str.replace("Z", "+00:00")).date()
    except:
        return None

    # Check if critical
    interpretation = resource.get("interpretation", [])
    is_critical = any(
        interp.get("coding", [{}])[0].get("code") in ["H", "HH", "L", "LL", "A", "AA"]
        for interp in interpretation
    )

    return LabResult(
        test_name=test_name,
        loinc_code=loinc_code,
        value=float(value),
        unit=unit,
        reference_range=reference_range,
        date=date,
        is_critical=is_critical,
    )


def _parse_allergy(resource: dict) -> str | None:
    """Parse FHIR AllergyIntolerance resource."""
    code_obj = resource.get("code", {})
    allergy_name = code_obj.get("text", "")

    if not allergy_name:
        codings = code_obj.get("coding", [])
        if codings:
            allergy_name = codings[0].get("display", "")

    return allergy_name if allergy_name else None
