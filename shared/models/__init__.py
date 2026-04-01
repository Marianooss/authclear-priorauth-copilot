"""
shared/models — Shared Pydantic models

Exports all models used by both MCP Server and A2A Agent.
"""

from shared.models.patient import (
    PatientDemographics,
    Diagnosis,
    Medication,
    LabResult,
    PatientBundle,
)

from shared.models.prior_auth import (
    ConfidenceLevel,
    SupportingDoc,
    MissingItem,
    PatientSummary,
    RequestedItemDetails,
    ClinicalJustification,
    PriorAuthDraft,
)

__all__ = [
    # Patient models
    "PatientDemographics",
    "Diagnosis",
    "Medication",
    "LabResult",
    "PatientBundle",
    # Prior auth models
    "ConfidenceLevel",
    "SupportingDoc",
    "MissingItem",
    "PatientSummary",
    "RequestedItemDetails",
    "ClinicalJustification",
    "PriorAuthDraft",
]
