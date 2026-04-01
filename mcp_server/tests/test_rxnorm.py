"""
Tests for mcp_server/tools/rxnorm.py

Tests:
- lookup_rxnorm: happy path (brand name, generic name, not found, timeout)
- check_drug_interactions: happy path, single drug, empty list
"""
from __future__ import annotations
import pytest
import respx
import httpx

from mcp_server.tools.rxnorm import lookup_rxnorm, check_drug_interactions
from mcp_server.models import RxNormLookup, DrugInteractionCheck


class TestLookupRxNorm:
    
    async def test_lookup_rxnorm_brand_name_returns_rxnorm_id(self, mock_rxnav_ozempic):
        """Brand name 'Ozempic' resolves to RxNorm ID 2200660."""
        result = await lookup_rxnorm("Ozempic")
        
        assert isinstance(result, RxNormLookup)
        assert result.rxnorm_id == "2200660"
        assert result.generic_name == "semaglutide"
        assert result.error is None

    async def test_lookup_rxnorm_generic_name_returns_same_id(self, mock_rxnav_ozempic):
        """Generic name 'semaglutide' resolves to same RxNorm ID."""
        result = await lookup_rxnorm("semaglutide")
        
        assert result.rxnorm_id == "2200660"

    async def test_lookup_rxnorm_includes_drug_class(self, mock_rxnav_ozempic):
        """Result includes drug class for clinical relevance."""
        result = await lookup_rxnorm("Ozempic")
        
        assert result.drug_class is not None
        assert "GLP-1" in result.drug_class or "peptide" in result.drug_class.lower()

    async def test_lookup_rxnorm_flags_prior_auth_required(self, mock_rxnav_ozempic):
        """Ozempic is known to require prior auth."""
        result = await lookup_rxnorm("Ozempic")
        
        assert result.requires_prior_auth is True

    async def test_lookup_rxnorm_drug_not_found_returns_error_model(self):
        """Unknown drug name returns error model, not exception."""
        with respx.mock() as mock:
            mock.get(url__regex=r"rxnav\.nlm\.nih\.gov.*drugs").mock(
                return_value=httpx.Response(200, json={"drugGroup": {"conceptGroup": []}})
            )
            
            result = await lookup_rxnorm("not_a_real_drug_xyz")
        
        assert result.error is not None
        assert "not found" in result.error.lower()
        assert result.rxnorm_id is None

    async def test_lookup_rxnorm_api_timeout_returns_error_model(self):
        """Timeout from NLM API returns error model gracefully."""
        with respx.mock() as mock:
            mock.get(url__regex=r"rxnav\.nlm\.nih\.gov").mock(
                side_effect=httpx.TimeoutException("read timeout")
            )
            
            result = await lookup_rxnorm("Ozempic")
        
        assert result.error is not None
        assert result.rxnorm_id is None

    async def test_lookup_rxnorm_500_response_returns_error_model(self):
        """NLM API 500 error returns error model, not unhandled exception."""
        with respx.mock() as mock:
            mock.get(url__regex=r"rxnav\.nlm\.nih\.gov").mock(
                return_value=httpx.Response(500, text="Internal Server Error")
            )
            
            result = await lookup_rxnorm("Ozempic")
        
        assert result.error is not None


class TestCheckDrugInteractions:
    
    async def test_check_interactions_two_drugs_returns_interactions(self, mock_rxnav_interactions):
        """Two drugs with known interaction returns populated interaction list."""
        result = await check_drug_interactions(["2200660", "860974"])
        
        assert isinstance(result, DrugInteractionCheck)
        assert result.total_interactions >= 1
        assert len(result.interactions) >= 1
        assert result.error is None

    async def test_check_interactions_severity_present(self, mock_rxnav_interactions):
        """Each interaction has a severity level."""
        result = await check_drug_interactions(["2200660", "860974"])
        
        for interaction in result.interactions:
            assert interaction.severity in {"none", "minor", "moderate", "major", "contraindicated"}

    async def test_check_interactions_single_drug_returns_empty(self):
        """Single RxNorm ID returns empty interactions without API call."""
        result = await check_drug_interactions(["2200660"])
        
        assert result.total_interactions == 0
        assert result.interactions == []
        assert result.error is None

    async def test_check_interactions_empty_list_returns_empty(self):
        """Empty list returns empty interactions."""
        result = await check_drug_interactions([])
        
        assert result.total_interactions == 0

    async def test_check_interactions_no_interactions_found(self):
        """Two drugs with no known interactions returns empty list."""
        with respx.mock() as mock:
            mock.get(url__regex=r"rxnav\.nlm\.nih\.gov.*interaction").mock(
                return_value=httpx.Response(200, json={"fullInteractionTypeGroup": []})
            )
            
            result = await check_drug_interactions(["111111", "222222"])
        
        assert result.total_interactions == 0
        assert result.error is None

    async def test_check_interactions_api_timeout_returns_error_model(self):
        """API timeout returns error model, not unhandled exception."""
        with respx.mock() as mock:
            mock.get(url__regex=r"rxnav\.nlm\.nih\.gov.*interaction").mock(
                side_effect=httpx.TimeoutException("timeout")
            )
            
            result = await check_drug_interactions(["2200660", "860974"])
        
        assert result.error is not None
