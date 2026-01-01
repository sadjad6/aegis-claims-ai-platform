from fastapi import APIRouter, Depends, HTTPException, Header, Request
from typing import List
from .dtos import ClaimCreateDTO, ClaimResponseDTO, DecisionResponseDTO
from ..application.use_cases import ProcessClaimUseCase
from ..domain.value_objects import Money

router = APIRouter()

# Mock Dependency Injection setup (Simplified for implementation)
def get_process_claim_use_case():
    # In a real app, this would be wired with a DI container (e.g. Dependency Injector or FastAPIs native DI)
    # properly injecting the infrastructure implementations.
    return None # Placeholder for orchestration in main.py

async def get_tenant_id(x_tenant_id: str = Header(...)):
    if not x_tenant_id:
        raise HTTPException(status_code=400, detail="X-Tenant-ID header missing")
    return x_tenant_id

@router.post("/claims", response_model=str)
async def submit_claim(
    claim_data: ClaimCreateDTO,
    tenant_id: str = Depends(get_tenant_id),
    use_case: ProcessClaimUseCase = Depends(get_process_claim_use_case)
):
    # Convert DTO to Domain inputs
    data = claim_data.dict()
    data["amount"] = Money(claim_data.amount.amount, claim_data.amount.currency)
    
    try:
        claim_id = await use_case.execute(tenant_id, data)
        return claim_id
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/claims", response_model=List[ClaimResponseDTO])
async def list_claims(
    tenant_id: str = Depends(get_tenant_id),
    repo = Depends() # Inject repository
):
    # Implementation here
    pass
