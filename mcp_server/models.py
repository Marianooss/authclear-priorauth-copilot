"""
mcp_server/models.py — MCP Tool Response Models

Pydantic models for all MCP tool responses.
Each tool returns a typed model with an optional error field.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class ICD10Resolution(BaseModel):
    """Response model for resolve_icd10 tool."""

    icd10_code: str
    description: str
    snomed_code: str | None = None
    snomed_description: str | None = None
    category: str | None = None
    error: str | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "icd10_code": "E11.9",
                "description": "Type 2 diabetes mellitus without complications",
                "snomed_code": "44054006",
                "snomed_description": "Diabetes mellitus type 2",
                "category": "Endocrine, nutritional and metabolic diseases"
            }
        }


class RxNormLookup(BaseModel):
    """Response model for lookup_rxnorm tool."""

    rxnorm_id: str | None = None
    generic_name: str
    brand_names: list[str] = Field(default_factory=list)
    drug_class: str | None = None
    requires_prior_auth: bool = False
    typical_indications: list[str] = Field(default_factory=list)
    error: str | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "rxnorm_id": "2200660",
                "generic_name": "semaglutide",
                "brand_names": ["Ozempic", "Wegovy"],
                "drug_class": "Glucagon-like peptide-1 receptor agonist",
                "requires_prior_auth": True,
                "typical_indications": ["Type 2 diabetes mellitus", "Obesity"]
            }
        }


class DrugInteraction(BaseModel):
    """A single drug-drug interaction."""

    drug_1: str
    drug_2: str
    severity: str  # none | minor | moderate | major | contraindicated
    description: str
    recommendation: str


class DrugInteractionCheck(BaseModel):
    """Response model for check_drug_interactions tool."""

    interactions: list[DrugInteraction] = Field(default_factory=list)
    total_interactions: int = 0
    error: str | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "interactions": [
                    {
                        "drug_1": "semaglutide",
                        "drug_2": "metformin",
                        "severity": "moderate",
                        "description": "Concurrent use may increase risk of hypoglycemia",
                        "recommendation": "Monitor blood glucose closely"
                    }
                ],
                "total_interactions": 1
            }
        }


class LOINCCode(BaseModel):
    """Response model for get_loinc_code tool."""

    loinc_code: str | None = None
    long_name: str | None = None
    short_name: str | None = None
    unit: str | None = None
    component: str | None = None
    error: str | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "loinc_code": "4548-4",
                "long_name": "Hemoglobin A1c/Hemoglobin.total in Blood",
                "short_name": "HbA1c",
                "unit": "%",
                "component": "Hemoglobin A1c"
            }
        }


class PriorAuthCriteria(BaseModel):
    """Response model for get_prior_auth_criteria tool."""

    cpt_code: str
    description: str
    payer: str
    required_diagnoses: list[str] = Field(default_factory=list)
    required_labs: list[str] = Field(default_factory=list)
    required_trials: list[str] = Field(default_factory=list)
    documentation_required: list[str] = Field(default_factory=list)
    typical_approval_duration: str | None = None
    error: str | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "cpt_code": "J0173",
                "description": "Semaglutide injection",
                "payer": "generic",
                "required_diagnoses": ["E11.9 - Type 2 diabetes mellitus"],
                "required_labs": ["HbA1c >= 7.5%", "BMI documented"],
                "required_trials": ["Metformin trial >= 3 months", "Second oral agent trial >= 3 months"],
                "documentation_required": ["Clinical notes", "Lab results", "Medication history"],
                "typical_approval_duration": "6 months"
            }
        }
