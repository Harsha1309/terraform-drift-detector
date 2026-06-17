from abc import ABC, abstractmethod
from typing import List
from core.models import ResourceModel

class StateReader(ABC):
    """Abstract base class for extracting and normalizing resources from Terraform states."""
    
    @abstractmethod
    async def read_state(self, source_path: str) -> List[ResourceModel]:
        """
        Reads a terraform state representation from a source path 
        and extracts normalized ResourceModel instances.
        """
        pass