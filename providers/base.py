from abc import ABC, abstractmethod
from typing import List, Dict, Any
from core.models import ResourceModel

class CloudFetcher(ABC):
    """Abstract base class for polling actual metadata from Cloud Providers."""

    @abstractmethod
    async def fetch_resources(self, config: Dict[str, Any]) -> List[ResourceModel]:
        """
        Queries live cloud provider APIs and returns matching infrastructure 
        normalized as a list of ResourceModels.
        """
        pass