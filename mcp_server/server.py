"""
mcp_server/server.py — FastMCP Server entrypoint

Registers all 5 clinical terminology tools and exposes them via SSE transport.
"""

from __future__ import annotations

import structlog
from fastmcp import FastMCP

from mcp_server.tools import (
    resolve_icd10,
    lookup_rxnorm,
    check_drug_interactions,
    get_loinc_code,
    get_prior_auth_criteria
)
from mcp_server.config import settings

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer() if settings.environment == "production"
        else structlog.dev.ConsoleRenderer()
    ]
)

log = structlog.get_logger()

# Create FastMCP app
mcp = FastMCP(
    name="authclear-terminology",
    instructions="FHIR clinical terminology resolution engine for healthcare AI agents",
    version="1.0.0"
)


# Register tools
@mcp.tool()
async def resolve_icd10_tool(code: str) -> dict:
    """
    Resolve ICD-10-CM code to SNOMED CT equivalent.

    Args:
        code: ICD-10-CM code (e.g., "E11.9" for type 2 diabetes)

    Returns:
        Dictionary with icd10_code, description, snomed_code, snomed_description, category

    Example:
        Input: "E11.9"
        Output: {
            "icd10_code": "E11.9",
            "description": "Type 2 diabetes mellitus without complications",
            "snomed_code": "44054006",
            "snomed_description": "Diabetes mellitus type 2",
            "category": "Endocrine, nutritional and metabolic diseases"
        }
    """
    result = await resolve_icd10(code)
    return result.model_dump()


@mcp.tool()
async def lookup_rxnorm_tool(drug_name: str) -> dict:
    """
    Look up drug by name and return RxNorm details.

    Args:
        drug_name: Drug name (brand or generic, e.g., "Ozempic" or "semaglutide")

    Returns:
        Dictionary with rxnorm_id, generic_name, brand_names, drug_class, requires_prior_auth, typical_indications

    Example:
        Input: "Ozempic"
        Output: {
            "rxnorm_id": "2200660",
            "generic_name": "semaglutide",
            "brand_names": ["Ozempic", "Wegovy"],
            "drug_class": "GLP-1 receptor agonist",
            "requires_prior_auth": true,
            "typical_indications": ["Type 2 diabetes", "Obesity"]
        }
    """
    result = await lookup_rxnorm(drug_name)
    return result.model_dump()


@mcp.tool()
async def check_drug_interactions_tool(rxnorm_ids: list[str]) -> dict:
    """
    Check for drug-drug interactions.

    Args:
        rxnorm_ids: List of RxNorm IDs to check (minimum 2)

    Returns:
        Dictionary with interactions array and total_interactions count

    Example:
        Input: ["2200660", "860974"]  # Ozempic + Metformin
        Output: {
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
    """
    result = await check_drug_interactions(rxnorm_ids)
    return result.model_dump()


@mcp.tool()
async def get_loinc_code_tool(test_name: str) -> dict:
    """
    Get LOINC code for a lab test by common name.

    Args:
        test_name: Common lab test name (e.g., "HbA1c", "eGFR", "lipid panel")

    Returns:
        Dictionary with loinc_code, long_name, short_name, unit, component

    Example:
        Input: "HbA1c"
        Output: {
            "loinc_code": "4548-4",
            "long_name": "Hemoglobin A1c/Hemoglobin.total in Blood",
            "short_name": "HbA1c",
            "unit": "%",
            "component": "Hemoglobin A1c"
        }
    """
    result = await get_loinc_code(test_name)
    return result.model_dump()


@mcp.tool()
async def get_prior_auth_criteria_tool(cpt_code: str, payer: str = "generic") -> dict:
    """
    Get prior authorization criteria for a CPT/HCPCS code and payer.

    Args:
        cpt_code: CPT or HCPCS code (e.g., "J0173" for semaglutide injection)
        payer: Payer name - "generic", "medicare", "medicaid", "bcbs", "aetna", "united"

    Returns:
        Dictionary with required_diagnoses, required_labs, required_trials, documentation_required

    Example:
        Input: cpt_code="J0173", payer="generic"
        Output: {
            "cpt_code": "J0173",
            "description": "Semaglutide injection",
            "payer": "generic",
            "required_diagnoses": ["E11.9 - Type 2 diabetes mellitus"],
            "required_labs": ["HbA1c >= 7.5%", "BMI documented"],
            "required_trials": ["Metformin trial >= 3 months", ...],
            "documentation_required": ["Clinical notes", "Lab results", ...],
            "typical_approval_duration": "6 months"
        }
    """
    result = await get_prior_auth_criteria(cpt_code, payer)
    return result.model_dump()


# Note: FastMCP 3.x does not support HTTP endpoints like FastAPI
# Health check is handled by MCP protocol itself


if __name__ == "__main__":
    log.info("starting_mcp_server", port=settings.port_mcp, environment=settings.environment)
    # FastMCP 3.x uses run() method
    mcp.run()
