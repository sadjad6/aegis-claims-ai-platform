import boto3
import json
from typing import Dict, Any
from ..application.ports import DocumentProcessor, StorageService


class BedrockDocumentAgent(DocumentProcessor):
    """Document Understanding Agent using AWS Bedrock for OCR + NLP extraction."""

    def __init__(
        self,
        storage_service: StorageService,
        region: str = "us-east-1",
        model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0"
    ):
        self.bedrock = boto3.client("bedrock-runtime", region_name=region)
        self.textract = boto3.client("textract", region_name=region)
        self.storage_service = storage_service
        self.model_id = model_id

    async def extract_info(self, document_key: str, tenant_id: str) -> Dict[str, Any]:
        """
        Extract structured information from an unstructured document.
        Uses Textract for OCR and Bedrock for NLP extraction.
        """
        # 1. Get document content from S3
        try:
            document_content = await self.storage_service.download(document_key, tenant_id)
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to retrieve document: {str(e)}",
                "confidence": 0.0
            }

        # 2. Perform OCR using Textract
        ocr_text = await self._perform_ocr(document_content, document_key)

        # 3. Use LLM for structured extraction
        extracted_data = await self._extract_with_llm(ocr_text, tenant_id)

        return extracted_data

    async def _perform_ocr(self, document_content: bytes, document_key: str) -> str:
        """Perform OCR on document using AWS Textract."""
        try:
            # Detect document type
            if document_key.lower().endswith(('.png', '.jpg', '.jpeg')):
                response = self.textract.detect_document_text(
                    Document={"Bytes": document_content}
                )
            else:
                # For PDFs, use analyze_document or async operations in production
                response = self.textract.detect_document_text(
                    Document={"Bytes": document_content}
                )

            # Extract text from Textract response
            text_blocks = [
                block["Text"]
                for block in response.get("Blocks", [])
                if block["BlockType"] == "LINE"
            ]
            return "\n".join(text_blocks)
        except Exception as e:
            # Fallback for development/testing
            return f"[OCR Error: {str(e)}]"

    async def _extract_with_llm(self, ocr_text: str, tenant_id: str) -> Dict[str, Any]:
        """Use Bedrock LLM to extract structured data from OCR text."""
        prompt = f"""You are an expert insurance document analyzer.
Extract the following fields from this document text:

Document Text:
{ocr_text}

Required Fields:
- damage_type: Type of damage described
- estimated_cost: Numeric cost value
- currency: Currency code (USD, EUR, GBP)
- incident_date: Date in ISO format (YYYY-MM-DD)
- vendor_name: Name of vendor/repair shop if present
- document_type: Type of document (invoice, estimate, police_report, photo, other)

Return ONLY a valid JSON object with these fields. Use null for missing fields.
"""
        try:
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 500,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0
            })

            response = self.bedrock.invoke_model(
                body=body,
                modelId=self.model_id,
                accept="application/json",
                contentType="application/json"
            )

            response_body = json.loads(response.get("body").read())
            text = response_body["content"][0]["text"]

            # Parse JSON from response
            start = text.find("{")
            end = text.rfind("}") + 1
            extracted = json.loads(text[start:end])
            extracted["success"] = True
            extracted["confidence"] = 0.95  # High confidence for successful extraction
            extracted["tenant_id"] = tenant_id
            return extracted

        except Exception as e:
            return {
                "success": False,
                "error": f"LLM extraction failed: {str(e)}",
                "confidence": 0.0,
                "damage_type": None,
                "estimated_cost": None,
                "currency": None,
                "incident_date": None,
                "vendor_name": None,
                "document_type": None
            }
