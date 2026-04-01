"""
mcp_server/tools/prior_auth.py — Prior authorization criteria lookup

Loads payer-specific prior auth criteria from YAML files.
No external API calls - all data bundled with the server.
"""

from __future__ import annotations

import yaml
from pathlib import Path
import structlog

from mcp_server.models import PriorAuthCriteria

log = structlog.get_logger()

# Global criteria store - loaded once at startup
_CRITERIA_STORE: dict[str, dict] = {}
_LOADED = False


def _load_criteria() -> None:
    """Load all criteria YAML files into memory at startup."""
    global _CRITERIA_STORE, _LOADED

    if _LOADED:
        return

    criteria_dir = Path(__file__).parent.parent / "data" / "criteria"

    if not criteria_dir.exists():
        log.error("criteria_dir_not_found", path=str(criteria_dir))
        return

    for yaml_file in criteria_dir.glob("*.yaml"):
        payer = yaml_file.stem  # filename without extension
        try:
            with open(yaml_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                _CRITERIA_STORE[payer] = data
                log.info("criteria_loaded", payer=payer, cpt_codes=list(data.keys()))
        except Exception as e:
            log.error("criteria_load_failed", payer=payer, error=str(e))

    _LOADED = True
    log.info("all_criteria_loaded", payers=list(_CRITERIA_STORE.keys()))


async def get_prior_auth_criteria(cpt_code: str, payer: str = "generic") -> PriorAuthCriteria:
    """
    Get prior authorization criteria for a CPT/HCPCS code and payer.

    Args:
        cpt_code: CPT or HCPCS code (e.g., "J0173")
        payer: Payer name (generic, medicare, medicaid, bcbs, aetna, united)

    Returns:
        PriorAuthCriteria with requirements or error

    Data source: Bundled YAML files in mcp_server/data/criteria/
    Cache TTL: Infinite (loaded at startup, in-memory only)
    """
    # Load criteria on first call
    if not _LOADED:
        _load_criteria()

    log.info("tool_called", tool="get_prior_auth_criteria", cpt_code=cpt_code, payer=payer)

    payer_lower = payer.lower()

    # Check if payer exists
    if payer_lower not in _CRITERIA_STORE:
        log.warning("payer_not_found", payer=payer, falling_back="generic")
        payer_lower = "generic"

    # Check if CPT code exists for this payer
    if payer_lower not in _CRITERIA_STORE:
        return PriorAuthCriteria(
            cpt_code=cpt_code,
            description="",
            payer=payer,
            error=f"No criteria data available (payer: {payer})"
        )

    payer_data = _CRITERIA_STORE[payer_lower]

    if cpt_code not in payer_data:
        # Try fallback to generic if not found
        if payer_lower != "generic" and "generic" in _CRITERIA_STORE:
            generic_data = _CRITERIA_STORE["generic"]
            if cpt_code in generic_data:
                log.info("falling_back_to_generic", cpt_code=cpt_code, original_payer=payer)
                payer_data = generic_data
                payer_lower = "generic"
            else:
                return PriorAuthCriteria(
                    cpt_code=cpt_code,
                    description="",
                    payer=payer,
                    error=f"CPT code {cpt_code} not found in criteria database"
                )
        else:
            return PriorAuthCriteria(
                cpt_code=cpt_code,
                description="",
                payer=payer,
                error=f"CPT code {cpt_code} not found for payer {payer}"
            )

    # Extract criteria
    criteria_data = payer_data[cpt_code]

    result = PriorAuthCriteria(
        cpt_code=cpt_code,
        description=criteria_data.get("description", ""),
        payer=payer_lower,
        required_diagnoses=criteria_data.get("required_diagnoses", []),
        required_labs=criteria_data.get("required_labs", []),
        required_trials=criteria_data.get("required_trials", []),
        documentation_required=criteria_data.get("documentation_required", []),
        typical_approval_duration=criteria_data.get("typical_approval_duration")
    )

    log.info("tool_success", tool="get_prior_auth_criteria", cpt_code=cpt_code, payer=payer_lower)
    return result
