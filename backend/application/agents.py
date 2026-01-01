from abc import ABC, abstractmethod
from typing import Any, Dict
from ..domain.entities import Claim

class BaseAgent(ABC):
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id

    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        pass
