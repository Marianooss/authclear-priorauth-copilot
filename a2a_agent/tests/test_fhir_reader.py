"""
Tests for a2a_agent/tools/fhir_reader.py

Tests:
- Happy path: complete FHIR bundle → PatientBundle
- Partial bundle: missing resources handled gracefully
- Invalid bundle: raises FHIRParseError with field detail
- Edge cases: multiple conditions, multiple medications, no labs
"""
from __future__ import annotations
import pytest

from a2a_agent.tools.fhir_reader import parse_fhir_bundle, FHIRParseError
from shared.models.patient import PatientBundle


class TestParseFHIRBundle:
    
    def test_parse_complete_bundle_returns_patient_bundle(self, synthetic_bundle_complete):
        """Complete FHIR bundle parses to PatientBundle successfully."""
        result = parse_fhir_bundle(synthetic_bundle_complete)
        
        assert isinstance(result, PatientBundle)
        assert result.patient is not None

    def test_parse_extracts_patient_demographics(self, synthetic_bundle_complete):
        """Patient name, DOB, and gender are correctly extracted."""
        result = parse_fhir_bundle(synthetic_bundle_complete)
        
        assert "González" in result.patient.name or "Maria" in result.patient.name
        assert result.patient.birth_date is not None
        assert result.patient.gender in {"male", "female", "other", "unknown"}

    def test_parse_extracts_diagnoses(self, synthetic_bundle_complete):
        """ICD-10 diagnoses are extracted from Condition resources."""
        result = parse_fhir_bundle(synthetic_bundle_complete)
        
        assert len(result.diagnoses) >= 1
        icd10_codes = [d.icd10_code for d in result.diagnoses]
        assert "E11.9" in icd10_codes

    def test_parse_extracts_medications(self, synthetic_bundle_complete):
        """Active medications are extracted from MedicationRequest resources."""
        result = parse_fhir_bundle(synthetic_bundle_complete)
        
        assert len(result.medications) >= 1
        # Metformin should be present
        med_names = [m.name.lower() for m in result.medications]
        assert any("metformin" in name for name in med_names)

    def test_parse_extracts_lab_results(self, synthetic_bundle_complete):
        """Lab results are extracted from Observation resources."""
        result = parse_fhir_bundle(synthetic_bundle_complete)
        
        assert len(result.lab_results) >= 1
        # HbA1c should be present
        lab_names = [l.test_name.lower() for l in result.lab_results]
        assert any("hba1c" in name or "hemoglobin a1c" in name or "4548-4" in name 
                   for name in lab_names + [l.loinc_code or "" for l in result.lab_results])

    def test_parse_hba1c_value_correct(self, synthetic_bundle_complete):
        """HbA1c value of 8.2% is correctly extracted."""
        result = parse_fhir_bundle(synthetic_bundle_complete)
        
        hba1c = next(
            (l for l in result.lab_results if l.loinc_code == "4548-4"),
            None
        )
        assert hba1c is not None
        assert abs(hba1c.value - 8.2) < 0.01

    def test_parse_bundle_with_missing_observations_succeeds(self, synthetic_bundle_complete):
        """Bundle without Observation resources parses with empty lab_results."""
        bundle = {
            **synthetic_bundle_complete,
            "entry": [
                e for e in synthetic_bundle_complete["entry"]
                if e["resource"]["resourceType"] != "Observation"
            ]
        }
        
        result = parse_fhir_bundle(bundle)
        
        assert isinstance(result, PatientBundle)
        assert result.lab_results == []

    def test_parse_bundle_with_missing_medications_succeeds(self, synthetic_bundle_complete):
        """Bundle without MedicationRequest resources parses with empty medications."""
        bundle = {
            **synthetic_bundle_complete,
            "entry": [
                e for e in synthetic_bundle_complete["entry"]
                if e["resource"]["resourceType"] != "MedicationRequest"
            ]
        }
        
        result = parse_fhir_bundle(bundle)
        
        assert isinstance(result, PatientBundle)
        assert result.medications == []

    def test_parse_invalid_bundle_raises_fhir_parse_error(self):
        """Non-FHIR JSON raises FHIRParseError with descriptive message."""
        invalid_bundle = {"this": "is not", "a": "FHIR bundle"}
        
        with pytest.raises(FHIRParseError) as exc_info:
            parse_fhir_bundle(invalid_bundle)
        
        assert "resourceType" in str(exc_info.value) or "Bundle" in str(exc_info.value)

    def test_parse_empty_dict_raises_fhir_parse_error(self):
        """Empty dict raises FHIRParseError."""
        with pytest.raises(FHIRParseError):
            parse_fhir_bundle({})

    def test_parse_bundle_with_no_patient_raises_fhir_parse_error(self, synthetic_bundle_complete):
        """Bundle missing Patient resource raises FHIRParseError."""
        bundle = {
            **synthetic_bundle_complete,
            "entry": [
                e for e in synthetic_bundle_complete["entry"]
                if e["resource"]["resourceType"] != "Patient"
            ]
        }
        
        with pytest.raises(FHIRParseError):
            parse_fhir_bundle(bundle)

    def test_parse_preserves_raw_fhir_bundle(self, synthetic_bundle_complete):
        """Original raw FHIR bundle is preserved in PatientBundle.raw_fhir."""
        result = parse_fhir_bundle(synthetic_bundle_complete)
        
        assert result.raw_fhir == synthetic_bundle_complete

    def test_parse_is_pure_function(self, synthetic_bundle_complete):
        """Parsing does not modify the input dict."""
        import copy
        original = copy.deepcopy(synthetic_bundle_complete)
        
        parse_fhir_bundle(synthetic_bundle_complete)
        
        assert synthetic_bundle_complete == original
