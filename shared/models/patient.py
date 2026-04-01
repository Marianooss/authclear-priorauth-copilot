"""
shared/models/patient.py — Patient FHIR data models

Pydantic models for parsed FHIR R4 patient data.
Used by both MCP Server and A2A Agent.
"""

from __future__ import annotations

from datetime import date, datetime
from pydantic import BaseModel, Field


class PatientDemographics(BaseModel):
    """Patient demographic information from FHIR Patient resource."""

    id: str
    name: str
    birth_date: date
    gender: str
    npi: str | None = None


class Diagnosis(BaseModel):
    """Patient diagnosis from FHIR Condition resource."""

    icd10_code: str
    description: str
    onset_date: date | None = None
    status: str = "active"  # active | resolved | chronic

    class Config:
        json_schema_extra = {
            "example": {
                "icd10_code": "E11.9",
                "description": "Type 2 diabetes mellitus without complications",
                "onset_date": "2020-03-15",
                "status": "active"
            }
        }


class Medication(BaseModel):
    """Patient medication from FHIR MedicationRequest resource."""

    name: str
    rxnorm_id: str | None = None
    dose: str
    frequency: str
    start_date: date | None = None
    status: str = "active"

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Metformin",
                "rxnorm_id": "860974",
                "dose": "1000mg",
                "frequency": "twice daily",
                "start_date": "2020-03-20",
                "status": "active"
            }
        }


class LabResult(BaseModel):
    """Patient lab result from FHIR Observation resource."""

    test_name: str
    loinc_code: str | None = None
    value: float
    unit: str
    reference_range: str | None = None
    date: date
    is_critical: bool = False

    class Config:
        json_schema_extra = {
            "example": {
                "test_name": "HbA1c",
                "loinc_code": "4548-4",
                "value": 8.9,
                "unit": "%",
                "reference_range": "4.0-5.6",
                "date": "2024-12-15",
                "is_critical": False
            }
        }


class PatientBundle(BaseModel):
    """
    Parsed FHIR R4 Patient Bundle — synthetic data only.

    Contains all relevant patient clinical data needed for prior auth.
    """

    patient: PatientDemographics
    diagnoses: list[Diagnosis] = Field(default_factory=list)
    medications: list[Medication] = Field(default_factory=list)
    lab_results: list[LabResult] = Field(default_factory=list)
    allergies: list[str] = Field(default_factory=list)
    raw_fhir: dict = Field(default_factory=dict, exclude=True)

    class Config:
        json_schema_extra = {
            "example": {
                "patient": {
                    "id": "synthetic-001",
                    "name": "Maria González",
                    "birth_date": "1975-03-15",
                    "gender": "female"
                },
                "diagnoses": [
                    {
                        "icd10_code": "E11.9",
                        "description": "Type 2 diabetes mellitus",
                        "status": "active"
                    }
                ],
                "medications": [
                    {
                        "name": "Metformin",
                        "dose": "1000mg",
                        "frequency": "twice daily",
                        "status": "active"
                    }
                ],
                "lab_results": [
                    {
                        "test_name": "HbA1c",
                        "value": 8.9,
                        "unit": "%",
                        "date": "2024-12-15"
                    }
                ],
                "allergies": ["Penicillin"]
            }
        }
