from abc import ABC, abstractmethod
from typing import Dict, Any
from ..domain.entities import Claim

class BaseAgent(ABC):
    """Base class for all autonomous AI agents. All agents must be tenant-aware."""
    
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id

    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent's main logic and return structured output."""
        pass
    
    def emit_audit_event(self, event_type: str, data: Dict[str, Any]):
        """Emit a structured audit event for governance and traceability."""
        import logging
        import json
        logger = logging.getLogger("agent.audit")
        logger.info(json.dumps({
            "agent": self.__class__.__name__,
            "tenant_id": self.tenant_id,
            "event_type": event_type,
            "data": data
        }))


class ClaimIntakeAgent(BaseAgent):
    """Validates and normalizes incoming claim data."""
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        self.emit_audit_event("INTAKE_START", {"raw_claim": context.get("claim_data")})
        
        claim_data = context.get("claim_data", {})
        
        # Validation logic
        required_fields = ["policy_number", "incident_date", "description", "amount"]
        missing = [f for f in required_fields if f not in claim_data]
        
        if missing:
            self.emit_audit_event("INTAKE_FAILED", {"missing_fields": missing})
            return {"success": False, "errors": f"Missing fields: {missing}"}
        
        self.emit_audit_event("INTAKE_SUCCESS", {"claim_number": claim_data.get("claim_number")})
        return {"success": True, "normalized_claim": claim_data}


class DocumentUnderstandingAgent(BaseAgent):
    """Processes unstructured documents (PDF, images) using OCR + NLP."""
    
    def __init__(self, tenant_id: str, document_processor):
        super().__init__(tenant_id)
        self.document_processor = document_processor
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        document_keys = context.get("document_keys", [])
        self.emit_audit_event("DOC_PROCESSING_START", {"document_count": len(document_keys)})
        
        extracted_data = []
        for key in document_keys:
            result = await self.document_processor.extract_info(key, self.tenant_id)
            extracted_data.append(result)
        
        self.emit_audit_event("DOC_PROCESSING_COMPLETE", {"extracted_count": len(extracted_data)})
        return {"success": True, "extracted_documents": extracted_data}


class FraudDetectionAgent(BaseAgent):
    """Invokes SageMaker ML model for fraud detection."""
    
    def __init__(self, tenant_id: str, fraud_service):
        super().__init__(tenant_id)
        self.fraud_service = fraud_service
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        claim = context.get("claim")
        self.emit_audit_event("FRAUD_CHECK_START", {"claim_id": claim.claim_id})
        
        fraud_score = await self.fraud_service.detect_fraud(claim)
        
        is_suspicious = fraud_score > 0.5
        self.emit_audit_event("FRAUD_CHECK_COMPLETE", {
            "claim_id": claim.claim_id,
            "fraud_score": fraud_score,
            "is_suspicious": is_suspicious
        })
        
        return {"fraud_score": fraud_score, "is_suspicious": is_suspicious}


class CoverageReasoningAgent(BaseAgent):
    """Uses LLM (Bedrock) + RAG to reason about policy coverage."""
    
    def __init__(self, tenant_id: str, llm_service, vector_service):
        super().__init__(tenant_id)
        self.llm_service = llm_service
        self.vector_service = vector_service
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        claim = context.get("claim")
        policy = context.get("policy")
        
        self.emit_audit_event("COVERAGE_REASONING_START", {"claim_id": claim.claim_id})
        
        # RAG: Retrieve similar historical claims
        # In production, generate embedding from claim description
        similar_claims = await self.vector_service.search_similar_claims(
            self.tenant_id, 
            embedding=[0.1] * 768,  # Placeholder embedding
            limit=3
        )
        
        rag_context = {"similar_claims": similar_claims, "fraud_score": context.get("fraud_score", 0)}
        
        llm_result = await self.llm_service.reason_coverage(claim, policy, rag_context)
        
        self.emit_audit_event("COVERAGE_REASONING_COMPLETE", {
            "claim_id": claim.claim_id,
            "confidence": llm_result.get("confidence"),
            "outcome": llm_result.get("recommended_outcome")
        })
        
        return llm_result


class DecisionAgent(BaseAgent):
    """Makes final decision with confidence-based logic and HITL escalation."""
    
    CONFIDENCE_THRESHOLD = 0.8
    FRAUD_THRESHOLD = 0.3
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        claim = context.get("claim")
        llm_result = context.get("llm_result")
        fraud_score = context.get("fraud_score", 0)
        
        self.emit_audit_event("DECISION_START", {"claim_id": claim.claim_id})
        
        confidence = llm_result.get("confidence", 0)
        recommended = llm_result.get("recommended_outcome", "PENDING_HUMAN")
        
        # Deterministic decision logic
        if confidence >= self.CONFIDENCE_THRESHOLD and fraud_score < self.FRAUD_THRESHOLD:
            final_outcome = recommended
            requires_human = False
        else:
            final_outcome = "PENDING_HUMAN"
            requires_human = True
        
        decision = {
            "final_outcome": final_outcome,
            "confidence": confidence,
            "fraud_score": fraud_score,
            "requires_human_review": requires_human,
            "reasoning": llm_result.get("reasoning", "")
        }
        
        self.emit_audit_event("DECISION_COMPLETE", {
            "claim_id": claim.claim_id,
            "outcome": final_outcome,
            "requires_human": requires_human
        })
        
        return decision
