"""
a2a_agent/agent_card.py — A2A AgentCard generator

Generates the AgentCard JSON served at /.well-known/agent.json
Updated to match agents.md Section 9 specification.
"""

from __future__ import annotations

from a2a_agent.config import settings


def get_agent_card() -> dict:
    """
    Generate the A2A AgentCard per agents.md Section 9.

    Returns:
        AgentCard JSON as dict

    Spec: A2A protocol requires this at /.well-known/agent.json
    """
    return {
        "name": "AuthClear Prior Auth Copilot",
        "description": "Reads a FHIR R4 patient bundle and generates a complete, evidence-backed prior authorization package with gap analysis and confidence scoring. Human-in-the-loop: outputs are always physician-review drafts, never auto-approvals.",
        "version": "2.0.0",
        "url": settings.mcp_server_url.replace(":8001", ":8000"),  # Agent URL (not MCP URL)
        "capabilities": {
            "streaming": False,
            "pushNotifications": False,
            "stateTransitionHistory": True,
            "multiTurnContinuation": True
        },
        "defaultInputModes": ["application/json"],
        "defaultOutputModes": ["application/json"],
        "skills": [
            {
                "id": "prior_auth_package",
                "name": "Generate Prior Auth Package",
                "description": "Given a FHIR patient bundle and a requested drug or procedure, produces a confidence-scored prior auth submission package with explicit gap analysis and physician action items.",
                "inputSchema": {
                    "type": "object",
                    "required": ["fhir_bundle", "requested_item"],
                    "properties": {
                        "fhir_bundle": {
                            "type": "object",
                            "description": "FHIR R4 Bundle resource"
                        },
                        "requested_item": {
                            "type": "string",
                            "description": "Drug name, CPT/HCPCS code, or procedure description"
                        },
                        "payer": {
                            "type": "string",
                            "description": "Payer name (optional). Defaults to generic.",
                            "enum": ["generic", "medicare", "medicaid", "bcbs", "aetna", "united"]
                        },
                        "urgency": {
                            "type": "string",
                            "description": "Request urgency level",
                            "enum": ["standard", "urgent", "emergency"],
                            "default": "standard"
                        },
                        "submitter_npi": {
                            "type": "string",
                            "description": "Prescribing physician NPI (optional)"
                        }
                    }
                }
            }
        ],
        "mcp_server": {
            "url": settings.mcp_server_url,
            "description": "FHIR Terminology MCP Server for clinical code resolution",
            "tools": [
                "resolve_icd10",
                "lookup_rxnorm",
                "check_drug_interactions",
                "get_loinc_code",
                "get_prior_auth_criteria"
            ]
        },
        "model": {
            "provider": settings.claude_provider,
            "name": settings.claude_model,
            "version": "2.0"
        },
        "compliance": {
            "data_policy": "synthetic_only",
            "phi_handling": "none",
            "human_review_required": True,
            "regulatory_compliance": ["TX_SB_490", "AZ_HB_2417", "MD_HB_1174"]
        },
        "contact": {
            "author": "AuthClear Team",
            "repository": "https://github.com/yourusername/authclear",
            "support": "https://github.com/yourusername/authclear/issues"
        },
        "marketplace": {
            "category": "healthcare",
            "tags": ["prior_authorization", "fhir", "clinical_coding", "healthcare_ai"],
            "published": True,
            "pricing": "free_hackathon_submission"
        }
    }
