"""
mcp_server/tools/loinc.py — LOINC lab test code lookup

Maps common lab test names to LOINC codes using FHIR terminology server.
"""

from __future__ import annotations

import structlog
import httpx

from mcp_server.models import LOINCCode
from mcp_server.cache import LOINC_CACHE, cache_key
from mcp_server.http_client import get_http_client, retry_request

log = structlog.get_logger()


async def get_loinc_code(test_name: str) -> LOINCCode:
    """
    Get LOINC code for a lab test by common name.

    Args:
        test_name: Common lab test name (e.g., "HbA1c", "eGFR")

    Returns:
        LOINCCode with details or error

    External API:
        https://fhir.loinc.org/CodeSystem/$lookup

    Cache TTL: 3600s
    """
    key = cache_key("get_loinc_code", test_name.lower())

    # Check cache
    if key in LOINC_CACHE:
        log.info("tool_called", tool="get_loinc_code", input=test_name, cache_hit=True)
        return LOINC_CACHE[key]

    log.info("tool_called", tool="get_loinc_code", input=test_name, cache_hit=False)

    # Try hardcoded mapping first (common tests for hackathon)
    hardcoded = _get_hardcoded_loinc(test_name.lower())
    if hardcoded:
        LOINC_CACHE[key] = hardcoded
        log.info("tool_success", tool="get_loinc_code", loinc=hardcoded.loinc_code, source="hardcoded")
        return hardcoded

    try:
        async with get_http_client() as client:
            # FHIR LOINC search API
            url = "https://fhir.loinc.org/CodeSystem/$lookup"
            params = {
                "system": "http://loinc.org",
                "property": "COMPONENT"
            }

            # Try fuzzy search
            search_url = f"https://fhir.loinc.org/ValueSet/$expand"
            search_params = {
                "url": "http://loinc.org/vs",
                "filter": test_name,
                "count": 1
            }

            response = await retry_request(client, "GET", search_url, params=search_params)
            data = response.json()

            # Parse response
            if "expansion" in data and "contains" in data["expansion"]:
                matches = data["expansion"]["contains"]
                if len(matches) > 0:
                    match = matches[0]
                    result = LOINCCode(
                        loinc_code=match.get("code"),
                        long_name=match.get("display"),
                        short_name=test_name,
                        unit=_infer_unit(test_name),
                        component=match.get("display")
                    )

                    log.info("tool_success", tool="get_loinc_code", loinc=result.loinc_code)
                    LOINC_CACHE[key] = result
                    return result

            # Test not found
            result = LOINCCode(
                short_name=test_name,
                error=f"LOINC code not found for test: {test_name}"
            )
            log.warning("tool_failed", tool="get_loinc_code", error="Test not found", name=test_name)
            return result

    except (httpx.HTTPStatusError, httpx.TimeoutException) as e:
        log.error("tool_failed", tool="get_loinc_code", error=str(e), name=test_name)
        return LOINCCode(
            short_name=test_name,
            error=f"External API error: {str(e)}"
        )


def _get_hardcoded_loinc(test_name: str) -> LOINCCode | None:
    """
    Hardcoded LOINC mappings for common lab tests.

    In production, this would always call the API. For hackathon speed,
    we hardcode the most common tests.
    """
    mappings = {
        "hba1c": LOINCCode(
            loinc_code="4548-4",
            long_name="Hemoglobin A1c/Hemoglobin.total in Blood",
            short_name="HbA1c",
            unit="%",
            component="Hemoglobin A1c"
        ),
        "hemoglobin a1c": LOINCCode(
            loinc_code="4548-4",
            long_name="Hemoglobin A1c/Hemoglobin.total in Blood",
            short_name="HbA1c",
            unit="%",
            component="Hemoglobin A1c"
        ),
        "egfr": LOINCCode(
            loinc_code="33914-3",
            long_name="Glomerular filtration rate/1.73 sq M.predicted",
            short_name="eGFR",
            unit="mL/min/1.73m2",
            component="Glomerular filtration rate"
        ),
        "creatinine": LOINCCode(
            loinc_code="2160-0",
            long_name="Creatinine [Mass/volume] in Serum or Plasma",
            short_name="Creatinine",
            unit="mg/dL",
            component="Creatinine"
        ),
        "glucose": LOINCCode(
            loinc_code="2345-7",
            long_name="Glucose [Mass/volume] in Serum or Plasma",
            short_name="Glucose",
            unit="mg/dL",
            component="Glucose"
        ),
        "ldl": LOINCCode(
            loinc_code="18262-6",
            long_name="Cholesterol in LDL [Mass/volume] in Serum or Plasma",
            short_name="LDL cholesterol",
            unit="mg/dL",
            component="LDL cholesterol"
        ),
        "bmi": LOINCCode(
            loinc_code="39156-5",
            long_name="Body mass index (BMI) [Ratio]",
            short_name="BMI",
            unit="kg/m2",
            component="Body mass index"
        ),
        "blood pressure": LOINCCode(
            loinc_code="85354-9",
            long_name="Blood pressure panel",
            short_name="Blood pressure",
            unit="mmHg",
            component="Blood pressure"
        ),
    }

    return mappings.get(test_name.lower())


def _infer_unit(test_name: str) -> str | None:
    """Infer typical unit for common test names."""
    unit_map = {
        "hba1c": "%",
        "glucose": "mg/dL",
        "creatinine": "mg/dL",
        "egfr": "mL/min/1.73m2",
        "ldl": "mg/dL",
        "bmi": "kg/m2",
        "blood pressure": "mmHg"
    }
    return unit_map.get(test_name.lower())
