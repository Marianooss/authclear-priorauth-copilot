"""
mcp_server/tools/icd10.py — ICD-10 to SNOMED resolution tool

Calls NLM VSAC/UMLS API to translate ICD-10-CM codes to SNOMED CT.
"""

from __future__ import annotations

import structlog
import httpx

from mcp_server.models import ICD10Resolution
from mcp_server.cache import ICD10_CACHE, cache_key
from mcp_server.http_client import get_http_client, retry_request
from mcp_server.config import settings

log = structlog.get_logger()


async def resolve_icd10(code: str) -> ICD10Resolution:
    """
    Resolve ICD-10-CM code to SNOMED CT equivalent.

    Args:
        code: ICD-10-CM code (e.g., "E11.9")

    Returns:
        ICD10Resolution with SNOMED mapping or error

    External API:
        https://clinicaltables.nlm.nih.gov/api/icd10cm/v3/search

    Cache TTL: 3600s (codes are stable)
    """
    key = cache_key("resolve_icd10", code)

    # Check cache
    if key in ICD10_CACHE:
        log.info("tool_called", tool="resolve_icd10", input=code, cache_hit=True)
        return ICD10_CACHE[key]

    log.info("tool_called", tool="resolve_icd10", input=code, cache_hit=False)

    try:
        async with get_http_client() as client:
            # NLM ICD-10-CM API
            url = f"https://clinicaltables.nlm.nih.gov/api/icd10cm/v3/search"
            params = {
                "sf": "code,name",
                "terms": code,
                "maxList": 1
            }

            response = await retry_request(client, "GET", url, params=params)
            data = response.json()

            # Parse response
            if data[0] > 0 and len(data[3]) > 0:
                result_code = data[3][0][0]
                description = data[3][0][1]

                # Get SNOMED mapping (simplified - in production would call UMLS API)
                # For hackathon, we'll use a known mapping for common codes
                snomed_code, snomed_desc = _get_snomed_mapping(code)

                result = ICD10Resolution(
                    icd10_code=result_code,
                    description=description,
                    snomed_code=snomed_code,
                    snomed_description=snomed_desc,
                    category=_get_category(code)
                )

                log.info("tool_success", tool="resolve_icd10", result_code=result_code)
                ICD10_CACHE[key] = result
                return result
            else:
                result = ICD10Resolution(
                    icd10_code=code,
                    description="",
                    error=f"Code not found: {code}"
                )
                log.warning("tool_failed", tool="resolve_icd10", error="Code not found", code=code)
                return result

    except (httpx.HTTPStatusError, httpx.TimeoutException) as e:
        log.error("tool_failed", tool="resolve_icd10", error=str(e), code=code)
        return ICD10Resolution(
            icd10_code=code,
            description="",
            error=f"External API error: {str(e)}"
        )


def _get_snomed_mapping(icd10_code: str) -> tuple[str | None, str | None]:
    """
    Get SNOMED mapping for common ICD-10 codes.

    In production, this would call UMLS API. For hackathon, hardcoded mappings.
    """
    mappings = {
        # Endocrine/Metabolic
        "E11.9": ("44054006", "Diabetes mellitus type 2"),
        "E11.0": ("44054006", "Diabetes mellitus type 2"),
        "E11": ("44054006", "Diabetes mellitus type 2"),
        "E10.9": ("46635009", "Diabetes mellitus type 1"),
        "E66.9": ("414915002", "Obesity"),
        "E78.5": ("55822004", "Hyperlipidemia"),
        "E03.9": ("40930008", "Hypothyroidism"),
        "R73.03": ("714628002", "Prediabetes"),

        # Cardiovascular
        "I10": ("38341003", "Essential hypertension"),
        "I48.91": ("49436004", "Atrial fibrillation"),
        "I50.9": ("42343007", "Congestive heart failure"),
        "I25.10": ("53741008", "Coronary arteriosclerosis"),
        "I73.9": ("400047006", "Peripheral vascular disease"),

        # Respiratory
        "J45.909": ("195967001", "Asthma"),
        "J44.9": ("13645005", "Chronic obstructive pulmonary disease"),

        # Musculoskeletal
        "M05.9": ("69896004", "Rheumatoid arthritis"),
        "M06.9": ("69896004", "Rheumatoid arthritis, unspecified"),
        "M79.3": ("73595000", "Panniculitis"),

        # Gastrointestinal
        "K21.9": ("235595009", "Gastroesophageal reflux disease"),
        "K25.9": ("397825006", "Gastric ulcer"),

        # Renal
        "N18.3": ("433146000", "Chronic kidney disease stage 3"),
        "N18.6": ("46177005", "End stage renal disease"),

        # Oncology
        "C50.919": ("254837009", "Malignant neoplasm of breast"),
        "C34.90": ("93880001", "Primary malignant neoplasm of lung"),

        # Mental Health
        "F33.9": ("370143000", "Major depressive disorder"),
        "F41.9": ("197480006", "Anxiety disorder"),
    }
    return mappings.get(icd10_code, (None, None))


def _get_category(icd10_code: str) -> str:
    """Get ICD-10 category based on first letter."""
    if icd10_code.startswith("E"):
        return "Endocrine, nutritional and metabolic diseases"
    elif icd10_code.startswith("I"):
        return "Diseases of the circulatory system"
    elif icd10_code.startswith("M"):
        return "Diseases of the musculoskeletal system"
    else:
        return "Other"
