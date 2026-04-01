"""
mcp_server/tools/rxnorm.py — RxNorm drug lookup and interaction checking

Calls NLM RxNav API for drug information and interactions.
"""

from __future__ import annotations

import structlog
import httpx

from mcp_server.models import RxNormLookup, DrugInteractionCheck, DrugInteraction
from mcp_server.cache import RXNORM_CACHE, INTERACTION_CACHE, cache_key
from mcp_server.http_client import get_http_client, retry_request

log = structlog.get_logger()


async def lookup_rxnorm(drug_name: str) -> RxNormLookup:
    """
    Look up drug by name and return RxNorm details.

    Args:
        drug_name: Drug name (brand or generic)

    Returns:
        RxNormLookup with drug details or error

    External API:
        https://rxnav.nlm.nih.gov/REST/drugs.json

    Cache TTL: 3600s
    """
    key = cache_key("lookup_rxnorm", drug_name.lower())

    # Check cache
    if key in RXNORM_CACHE:
        log.info("tool_called", tool="lookup_rxnorm", input=drug_name, cache_hit=True)
        return RXNORM_CACHE[key]

    log.info("tool_called", tool="lookup_rxnorm", input=drug_name, cache_hit=False)

    try:
        async with get_http_client() as client:
            # RxNav drug search API
            url = "https://rxnav.nlm.nih.gov/REST/drugs.json"
            params = {"name": drug_name}

            response = await retry_request(client, "GET", url, params=params)
            data = response.json()

            if "drugGroup" in data and "conceptGroup" in data["drugGroup"]:
                for group in data["drugGroup"]["conceptGroup"]:
                    if "conceptProperties" in group and len(group["conceptProperties"]) > 0:
                        concept = group["conceptProperties"][0]
                        rxnorm_id = concept.get("rxcui")
                        name = concept.get("name", drug_name)

                        # Get additional details
                        drug_class, indications, brand_names = await _get_drug_details(client, rxnorm_id)

                        result = RxNormLookup(
                            rxnorm_id=rxnorm_id,
                            generic_name=name,
                            brand_names=brand_names,
                            drug_class=drug_class,
                            requires_prior_auth=_requires_prior_auth(drug_class),
                            typical_indications=indications
                        )

                        log.info("tool_success", tool="lookup_rxnorm", rxnorm_id=rxnorm_id)
                        RXNORM_CACHE[key] = result
                        return result

            # Drug not found
            result = RxNormLookup(
                generic_name=drug_name,
                error=f"Drug not found: {drug_name}"
            )
            log.warning("tool_failed", tool="lookup_rxnorm", error="Drug not found", name=drug_name)
            return result

    except (httpx.HTTPStatusError, httpx.TimeoutException) as e:
        log.error("tool_failed", tool="lookup_rxnorm", error=str(e), name=drug_name)
        return RxNormLookup(
            generic_name=drug_name,
            error=f"External API error: {str(e)}"
        )


async def check_drug_interactions(rxnorm_ids: list[str]) -> DrugInteractionCheck:
    """
    Check for drug-drug interactions.

    Args:
        rxnorm_ids: List of RxNorm IDs to check

    Returns:
        DrugInteractionCheck with interactions or error

    External API:
        https://rxnav.nlm.nih.gov/REST/interaction/list.json

    Cache TTL: 300s (more dynamic than lookups)
    """
    if len(rxnorm_ids) < 2:
        return DrugInteractionCheck(
            interactions=[],
            total_interactions=0
        )

    key = cache_key("check_interactions", *sorted(rxnorm_ids))

    # Check cache
    if key in INTERACTION_CACHE:
        log.info("tool_called", tool="check_interactions", cache_hit=True)
        return INTERACTION_CACHE[key]

    log.info("tool_called", tool="check_interactions", num_drugs=len(rxnorm_ids), cache_hit=False)

    try:
        async with get_http_client() as client:
            # RxNav interaction API
            rxcuis = "+".join(rxnorm_ids)
            url = f"https://rxnav.nlm.nih.gov/REST/interaction/list.json"
            params = {"rxcuis": rxcuis}

            response = await retry_request(client, "GET", url, params=params)
            data = response.json()

            interactions = []
            if "fullInteractionTypeGroup" in data:
                for type_group in data["fullInteractionTypeGroup"]:
                    if "fullInteractionType" in type_group:
                        for interaction_type in type_group["fullInteractionType"]:
                            if "interactionPair" in interaction_type:
                                for pair in interaction_type["interactionPair"]:
                                    drug1 = pair["interactionConcept"][0]["minConceptItem"]["name"]
                                    drug2 = pair["interactionConcept"][1]["minConceptItem"]["name"]
                                    description = pair.get("description", "No description available")
                                    severity = pair.get("severity", "unknown")

                                    interactions.append(DrugInteraction(
                                        drug_1=drug1,
                                        drug_2=drug2,
                                        severity=severity.lower(),
                                        description=description,
                                        recommendation=_get_recommendation(severity)
                                    ))

            result = DrugInteractionCheck(
                interactions=interactions,
                total_interactions=len(interactions)
            )

            log.info("tool_success", tool="check_interactions", total=len(interactions))
            INTERACTION_CACHE[key] = result
            return result

    except (httpx.HTTPStatusError, httpx.TimeoutException) as e:
        log.error("tool_failed", tool="check_interactions", error=str(e))
        return DrugInteractionCheck(
            interactions=[],
            total_interactions=0,
            error=f"External API error: {str(e)}"
        )


async def _get_drug_details(client: httpx.AsyncClient, rxnorm_id: str) -> tuple[str | None, list[str], list[str]]:
    """Get additional drug details (drug class, indications, brand names)."""
    # Simplified for hackathon - hardcoded common drugs
    drug_info = {
        # GLP-1 Receptor Agonists
        "2200660": ("GLP-1 receptor agonist", ["Type 2 diabetes", "Obesity"], ["Ozempic", "Wegovy"]),
        "1114195": ("GLP-1 receptor agonist", ["Type 2 diabetes"], ["Victoza"]),
        "1807809": ("GLP-1 receptor agonist", ["Type 2 diabetes"], ["Trulicity"]),

        # Antidiabetics
        "860974": ("Biguanide", ["Type 2 diabetes"], ["Glucophage"]),
        "4815": ("Sulfonylurea", ["Type 2 diabetes"], ["Glipizide"]),
        "25789": ("Sulfonylurea", ["Type 2 diabetes"], ["Glimepiride"]),
        "1373458": ("SGLT2 inhibitor", ["Type 2 diabetes", "Heart failure"], ["Jardiance"]),
        "1545653": ("SGLT2 inhibitor", ["Type 2 diabetes"], ["Invokana"]),

        # TNF Alpha Inhibitors / Biologics
        "1656328": ("TNF alpha inhibitor", ["Rheumatoid arthritis", "Psoriasis"], ["Humira"]),
        "349332": ("TNF alpha inhibitor", ["Rheumatoid arthritis", "Ankylosing spondylitis"], ["Enbrel"]),
        "358263": ("TNF alpha inhibitor", ["Crohn's disease", "Ulcerative colitis"], ["Remicade"]),

        # DMARDs
        "6851": ("DMARD", ["Rheumatoid arthritis", "Psoriasis"], ["Methotrexate"]),
        "5521": ("DMARD", ["Rheumatoid arthritis", "Lupus"], ["Plaquenil", "Hydroxychloroquine"]),

        # Anticoagulants
        "1361574": ("Direct oral anticoagulant (DOAC)", ["Atrial fibrillation", "DVT"], ["Eliquis"]),
        "1114195": ("Direct oral anticoagulant (DOAC)", ["Atrial fibrillation", "DVT"], ["Xarelto"]),
        "11289": ("Vitamin K antagonist", ["Atrial fibrillation", "DVT"], ["Coumadin", "Warfarin"]),
        "1037042": ("Direct oral anticoagulant (DOAC)", ["Atrial fibrillation", "DVT"], ["Pradaxa"]),

        # Statins
        "36567": ("HMG-CoA reductase inhibitor (Statin)", ["Hyperlipidemia"], ["Lipitor", "Atorvastatin"]),
        "42463": ("HMG-CoA reductase inhibitor (Statin)", ["Hyperlipidemia"], ["Crestor", "Rosuvastatin"]),

        # Antihypertensives
        "29046": ("ACE inhibitor", ["Hypertension", "Heart failure"], ["Lisinopril"]),
        "52175": ("Angiotensin II receptor blocker (ARB)", ["Hypertension"], ["Losartan"]),
        "1091643": ("Beta blocker", ["Hypertension", "Heart failure"], ["Metoprolol"]),

        # Corticosteroids
        "8640": ("Corticosteroid", ["Inflammation", "Autoimmune diseases"], ["Prednisone"]),

        # Respiratory
        "895994": ("Inhaled corticosteroid + LABA", ["Asthma", "COPD"], ["Advair"]),
        "1649574": ("Bronchodilator", ["Asthma", "COPD"], ["Albuterol"]),
    }
    return drug_info.get(rxnorm_id, (None, [], []))


def _requires_prior_auth(drug_class: str | None) -> bool:
    """Determine if drug class typically requires prior auth."""
    if not drug_class:
        return False

    high_cost_classes = [
        "GLP-1 receptor agonist",
        "TNF alpha inhibitor",
        "PCSK9 inhibitor",
        "Monoclonal antibody"
    ]
    return any(cls in drug_class for cls in high_cost_classes)


def _get_recommendation(severity: str) -> str:
    """Get clinical recommendation based on interaction severity."""
    recommendations = {
        "high": "Avoid combination if possible. Consult specialist before prescribing.",
        "moderate": "Monitor patient closely. Consider dose adjustment.",
        "minor": "Monitor for adverse effects. Usually safe to use together.",
        "unknown": "Clinical significance unclear. Monitor patient."
    }
    return recommendations.get(severity.lower(), "Monitor patient closely.")
