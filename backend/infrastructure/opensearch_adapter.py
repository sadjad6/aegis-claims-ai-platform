import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth
from typing import List, Dict, Any
from ..application.ports import DocumentProcessor # Reusing port or defining new one
from ..domain.entities import Claim

class OpenSearchVectorService:
    def __init__(self, host: str, region: str = "us-east-1"):
        credentials = boto3.Session().get_credentials()
        auth = AWSV4SignerAuth(credentials, region)
        
        self.client = OpenSearch(
            hosts=[{'host': host, 'port': 443}],
            http_auth=auth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection
        )

    async def search_similar_claims(self, tenant_id: str, embedding: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        query = {
            "size": limit,
            "query": {
                "bool": {
                    "must": [
                        {"term": {"tenant_id": tenant_id}}
                    ],
                    "knn": {
                        "embedding": {
                            "vector": embedding,
                            "k": limit
                        }
                    }
                }
            }
        }
        response = self.client.search(index="claims-vectors", body=query)
        return [hit["_source"] for hit in response["hits"]["hits"]]

    async def index_claim(self, tenant_id: str, claim_id: str, text: str, embedding: List[float]):
        body = {
            "tenant_id": tenant_id,
            "claim_id": claim_id,
            "text": text,
            "embedding": embedding
        }
        self.client.index(index="claims-vectors", id=claim_id, body=body)
