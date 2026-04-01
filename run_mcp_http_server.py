#!/usr/bin/env python
"""
MCP Server HTTP Wrapper - For Demo/Development

FastMCP 3.x uses stdio transport, but for the demo we need HTTP endpoints
so the A2A Agent can call the MCP tools via REST API.

This wrapper exposes all 5 MCP tools as FastAPI endpoints at /tools/{tool_name}
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from mcp_server.tools import (
    resolve_icd10,
    lookup_rxnorm,
    check_drug_interactions,
    get_loinc_code,
    get_prior_auth_criteria
)
from mcp_server.config import settings

app = FastAPI(
    title="AuthClear MCP Server (HTTP Wrapper)",
    description="FHIR terminology resolution engine - HTTP endpoints for demo",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request models
class ResolveICD10Request(BaseModel):
    code: str


class LookupRxNormRequest(BaseModel):
    drug_name: str


class CheckInteractionsRequest(BaseModel):
    rxnorm_ids: list[str]


class GetLOINCRequest(BaseModel):
    test_name: str


class GetPriorAuthRequest(BaseModel):
    cpt_code: str
    payer: str = "generic"


# Endpoints
@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "authclear-mcp-server",
        "version": "1.0.0",
        "environment": settings.environment
    }


@app.post("/tools/resolve_icd10_tool")
async def resolve_icd10_endpoint(request: ResolveICD10Request):
    """Resolve ICD-10-CM code to SNOMED CT"""
    try:
        result = await resolve_icd10(request.code)
        return result.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tools/lookup_rxnorm_tool")
async def lookup_rxnorm_endpoint(request: LookupRxNormRequest):
    """Look up drug by name"""
    try:
        result = await lookup_rxnorm(request.drug_name)
        return result.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tools/check_drug_interactions_tool")
async def check_interactions_endpoint(request: CheckInteractionsRequest):
    """Check drug-drug interactions"""
    try:
        result = await check_drug_interactions(request.rxnorm_ids)
        return result.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tools/get_loinc_code_tool")
async def get_loinc_endpoint(request: GetLOINCRequest):
    """Get LOINC code for lab test"""
    try:
        result = await get_loinc_code(request.test_name)
        return result.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tools/get_prior_auth_criteria_tool")
async def get_prior_auth_endpoint(request: GetPriorAuthRequest):
    """Get prior auth criteria"""
    try:
        result = await get_prior_auth_criteria(request.cpt_code, request.payer)
        return result.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    print("=" * 80)
    print("  AuthClear MCP Server (HTTP Wrapper)")
    print("=" * 80)
    print()
    print(f"  Starting server on port {settings.port_mcp}")
    print(f"  Environment: {settings.environment}")
    print(f"  Log level: {settings.log_level}")
    print()
    print("  Endpoints:")
    print(f"    Health:        http://localhost:{settings.port_mcp}/health")
    print(f"    ICD-10:        http://localhost:{settings.port_mcp}/tools/resolve_icd10_tool")
    print(f"    RxNorm:        http://localhost:{settings.port_mcp}/tools/lookup_rxnorm_tool")
    print(f"    Interactions:  http://localhost:{settings.port_mcp}/tools/check_drug_interactions_tool")
    print(f"    LOINC:         http://localhost:{settings.port_mcp}/tools/get_loinc_code_tool")
    print(f"    Prior Auth:    http://localhost:{settings.port_mcp}/tools/get_prior_auth_criteria_tool")
    print()
    print("  Press Ctrl+C to stop")
    print("=" * 80)
    print()

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=settings.port_mcp,
        log_level=settings.log_level.lower()
    )
