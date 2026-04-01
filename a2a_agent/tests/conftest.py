"""
MCP Server test fixtures.
All external HTTP calls are mocked via respx — no real network in tests.
"""
from __future__ import annotations
import pytest
import respx
import httpx


# ── NLM ICD-10 API Fixtures ───────────────────────────────────────────────

NLM_ICD10_E11_9_RESPONSE = {
    "resourceType": "Parameters",
    "parameter": [
        {"name": "result", "valueBoolean": True},
        {"name": "match", "part": [
            {"name": "concept", "valueCoding": {
                "system": "http://snomed.info/sct",
                "code": "44054006",
                "display": "Diabetes mellitus type 2"
            }},
            {"name": "equivalence", "valueCode": "equivalent"}
        ]}
    ]
}

NLM_ICD10_NOT_FOUND_RESPONSE = {
    "resourceType": "Parameters",
    "parameter": [
        {"name": "result", "valueBoolean": False},
        {"name": "message", "valueString": "No mapping found for code XXXXX"}
    ]
}


# ── NLM RxNav Fixtures ────────────────────────────────────────────────────

RXNAV_OZEMPIC_RESPONSE = {
    "drugGroup": {
        "conceptGroup": [
            {
                "tty": "IN",
                "conceptProperties": [
                    {
                        "rxcui": "2200660",
                        "name": "semaglutide",
                        "synonym": "Ozempic",
                        "tty": "IN",
                        "language": "ENG",
                        "suppress": "N"
                    }
                ]
            }
        ]
    }
}

RXNAV_DRUG_CLASS_RESPONSE = {
    "minConceptGroup": {
        "minConcept": [
            {
                "rxcui": "2200660",
                "name": "semaglutide",
                "tty": "IN"
            }
        ]
    },
    "classGroup": [
        {
            "rxclassMinConceptList": {
                "rxclassMinConcept": [
                    {
                        "classId": "A10BJ",
                        "className": "Glucagon-like peptide-1 receptor agonist",
                        "classType": "ATC1-4"
                    }
                ]
            }
        }
    ]
}

RXNAV_INTERACTIONS_RESPONSE = {
    "fullInteractionTypeGroup": [
        {
            "sourceDisclaimer": "NLM RxNav",
            "fullInteractionType": [
                {
                    "rxcui": ["2200660", "860974"],
                    "interactionPair": [
                        {
                            "interactionConcept": [
                                {"minConceptItem": {"rxcui": "2200660", "name": "semaglutide"}},
                                {"minConceptItem": {"rxcui": "860974", "name": "metformin"}}
                            ],
                            "severity": "moderate",
                            "description": "Concurrent use may increase hypoglycemia risk"
                        }
                    ]
                }
            ]
        }
    ]
}


# ── LOINC Fixtures ────────────────────────────────────────────────────────

LOINC_HBA1C_RESPONSE = {
    "resourceType": "Parameters",
    "parameter": [
        {"name": "code", "valueCode": "4548-4"},
        {"name": "display", "valueString": "Hemoglobin A1c/Hemoglobin.total in Blood"},
        {"name": "property", "part": [
            {"name": "code", "valueCode": "COMPONENT"},
            {"name": "value", "valueString": "Hemoglobin A1c"}
        ]}
    ]
}


# ── pytest Fixtures ───────────────────────────────────────────────────────

@pytest.fixture
def mock_nlm_icd10_e11_9():
    """Mock successful ICD-10 E11.9 resolution."""
    with respx.mock(assert_all_called=False) as respx_mock:
        respx_mock.get(
            url__regex=r"cts\.nlm\.nih\.gov.*ConceptMap.*E11\.9"
        ).mock(return_value=httpx.Response(200, json=NLM_ICD10_E11_9_RESPONSE))
        yield respx_mock


@pytest.fixture
def mock_nlm_icd10_not_found():
    """Mock ICD-10 lookup returning no results."""
    with respx.mock(assert_all_called=False) as respx_mock:
        respx_mock.get(
            url__regex=r"cts\.nlm\.nih\.gov.*ConceptMap"
        ).mock(return_value=httpx.Response(200, json=NLM_ICD10_NOT_FOUND_RESPONSE))
        yield respx_mock


@pytest.fixture
def mock_nlm_icd10_timeout():
    """Mock ICD-10 API timeout."""
    with respx.mock(assert_all_called=False) as respx_mock:
        respx_mock.get(
            url__regex=r"cts\.nlm\.nih\.gov"
        ).mock(side_effect=httpx.TimeoutException("Connection timed out"))
        yield respx_mock


@pytest.fixture
def mock_rxnav_ozempic():
    """Mock RxNav lookup for Ozempic/semaglutide."""
    with respx.mock(assert_all_called=False) as respx_mock:
        respx_mock.get(
            url__regex=r"rxnav\.nlm\.nih\.gov.*drugs.*Ozempic"
        ).mock(return_value=httpx.Response(200, json=RXNAV_OZEMPIC_RESPONSE))
        respx_mock.get(
            url__regex=r"rxnav\.nlm\.nih\.gov.*rxclass.*2200660"
        ).mock(return_value=httpx.Response(200, json=RXNAV_DRUG_CLASS_RESPONSE))
        yield respx_mock


@pytest.fixture
def mock_rxnav_interactions():
    """Mock drug interaction check."""
    with respx.mock(assert_all_called=False) as respx_mock:
        respx_mock.get(
            url__regex=r"rxnav\.nlm\.nih\.gov.*interaction.*list"
        ).mock(return_value=httpx.Response(200, json=RXNAV_INTERACTIONS_RESPONSE))
        yield respx_mock


@pytest.fixture
def mock_loinc_hba1c():
    """Mock LOINC lookup for HbA1c."""
    with respx.mock(assert_all_called=False) as respx_mock:
        respx_mock.get(
            url__regex=r"fhir\.loinc\.org.*lookup.*HbA1c"
        ).mock(return_value=httpx.Response(200, json=LOINC_HBA1C_RESPONSE))
        yield respx_mock
