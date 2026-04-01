"""
a2a_agent/tools/mcp_client.py — MCP Server client

Async client for calling the FHIR Terminology MCP Server.
Wraps all 5 tools with retry logic and typed responses.
"""

from __future__ import annotations

import httpx
import structlog

from mcp_server.models import (
    ICD10Resolution,
    RxNormLookup,
    DrugInteractionCheck,
    LOINCCode,
    PriorAuthCriteria,
)
from a2a_agent.config import settings

log = structlog.get_logger()


class MCPClient:
    """
    Async client for the FHIR Terminology MCP Server.

    Provides typed methods for all 5 MCP tools with automatic retry logic.
    """

    def __init__(self, base_url: str | None = None):
        """
        Initialize MCP client.

        Args:
            base_url: MCP server base URL (defaults to config)
        """
        self.base_url = base_url or settings.mcp_server_url
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self):
        """Async context manager entry."""
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(
                connect=settings.http_connect_timeout,
                read=settings.http_read_timeout,
                write=10.0,
                pool=10.0
            ),
            follow_redirects=True,
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()

    async def _post(self, tool_name: str, params: dict) -> dict:
        """
        Make a POST request to an MCP tool.

        Args:
            tool_name: Tool name (e.g., "resolve_icd10_tool")
            params: Tool parameters

        Returns:
            Tool response as dict

        Raises:
            httpx.HTTPStatusError: On HTTP error
            httpx.TimeoutException: On timeout
        """
        if not self._client:
            raise RuntimeError("MCPClient must be used as async context manager")

        url = f"{self.base_url}/tools/{tool_name}"

        log.debug("mcp_call", tool=tool_name, params=params)

        # Retry logic
        max_attempts = settings.http_max_retries
        for attempt in range(1, max_attempts + 1):
            try:
                response = await self._client.post(url, json=params)
                response.raise_for_status()
                result = response.json()

                log.info("mcp_success", tool=tool_name, attempt=attempt)
                return result

            except httpx.HTTPStatusError as e:
                if e.response.status_code in [408, 429, 500, 502, 503, 504]:
                    if attempt < max_attempts:
                        await self._sleep(2 ** attempt)
                        continue
                log.error("mcp_http_error", tool=tool_name, status=e.response.status_code, error=str(e))
                raise

            except httpx.TimeoutException as e:
                if attempt < max_attempts:
                    await self._sleep(2 ** attempt)
                    continue
                log.error("mcp_timeout", tool=tool_name, error=str(e))
                raise

    async def _sleep(self, seconds: float):
        """Sleep for retry backoff."""
        import asyncio
        await asyncio.sleep(seconds)

    async def resolve_icd10(self, code: str) -> ICD10Resolution:
        """
        Resolve ICD-10-CM code to SNOMED CT.

        Args:
            code: ICD-10-CM code (e.g., "E11.9")

        Returns:
            ICD10Resolution with mapping or error
        """
        try:
            result = await self._post("resolve_icd10_tool", {"code": code})
            return ICD10Resolution.model_validate(result)
        except Exception as e:
            log.error("resolve_icd10_failed", code=code, error=str(e))
            return ICD10Resolution(
                icd10_code=code,
                description="",
                error=f"MCP call failed: {str(e)}",
            )

    async def lookup_rxnorm(self, drug_name: str) -> RxNormLookup:
        """
        Look up drug by name.

        Args:
            drug_name: Drug name (brand or generic)

        Returns:
            RxNormLookup with drug details or error
        """
        try:
            result = await self._post("lookup_rxnorm_tool", {"drug_name": drug_name})
            return RxNormLookup.model_validate(result)
        except Exception as e:
            log.error("lookup_rxnorm_failed", drug_name=drug_name, error=str(e))
            return RxNormLookup(
                generic_name=drug_name,
                error=f"MCP call failed: {str(e)}",
            )

    async def check_drug_interactions(self, rxnorm_ids: list[str]) -> DrugInteractionCheck:
        """
        Check for drug-drug interactions.

        Args:
            rxnorm_ids: List of RxNorm IDs (minimum 2)

        Returns:
            DrugInteractionCheck with interactions or error
        """
        try:
            result = await self._post("check_drug_interactions_tool", {"rxnorm_ids": rxnorm_ids})
            return DrugInteractionCheck.model_validate(result)
        except Exception as e:
            log.error("check_interactions_failed", num_drugs=len(rxnorm_ids), error=str(e))
            return DrugInteractionCheck(
                interactions=[],
                total_interactions=0,
                error=f"MCP call failed: {str(e)}",
            )

    async def get_loinc_code(self, test_name: str) -> LOINCCode:
        """
        Get LOINC code for a lab test.

        Args:
            test_name: Common test name (e.g., "HbA1c")

        Returns:
            LOINCCode with details or error
        """
        try:
            result = await self._post("get_loinc_code_tool", {"test_name": test_name})
            return LOINCCode.model_validate(result)
        except Exception as e:
            log.error("get_loinc_failed", test_name=test_name, error=str(e))
            return LOINCCode(
                short_name=test_name,
                error=f"MCP call failed: {str(e)}",
            )

    async def get_prior_auth_criteria(self, cpt_code: str, payer: str = "generic") -> PriorAuthCriteria:
        """
        Get prior auth criteria for a CPT/HCPCS code.

        Args:
            cpt_code: CPT or HCPCS code (e.g., "J0173")
            payer: Payer name

        Returns:
            PriorAuthCriteria with requirements or error
        """
        try:
            result = await self._post("get_prior_auth_criteria_tool", {"cpt_code": cpt_code, "payer": payer})
            return PriorAuthCriteria.model_validate(result)
        except Exception as e:
            log.error("get_criteria_failed", cpt_code=cpt_code, payer=payer, error=str(e))
            return PriorAuthCriteria(
                cpt_code=cpt_code,
                description="",
                payer=payer,
                error=f"MCP call failed: {str(e)}",
            )
