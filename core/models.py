from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum
from typing import List, Dict, Any

@dataclass
class ResourceModel:
    """
    Unified representation of a cloud resource across both 
    Terraform state files and live cloud provider APIs.
    """
    resource_id: str          # e.g., 'i-0123456789abcdef0' or 'my-bucket'
    resource_type: str        # e.g., 'aws_instance', 'aws_s3_bucket'
    provider: str             # e.g., 'aws', 'azure', 'gcp'
    region: str               # e.g., 'us-east-1'
    attributes: Dict[str, Any] = field(default_factory=dict)
    tags: Dict[str, str] = field(default_factory=dict)
    last_seen: datetime = field(default_factory=datetime.utcnow)

    @property
    def canonical_id(self) -> str:
        """
        Generates a unique, deterministic key used by the drift engine 
        to match state resources against live cloud resources.
        """
        return f"{self.provider}::{self.resource_type}::{self.resource_id}"

class DriftType(Enum):
    DELETED = "DELETED"       # In Terraform state, missing in Cloud
    UNMANAGED = "UNMANAGED"   # In Cloud, missing in Terraform state
    MODIFIED = "MODIFIED"     # Attribute mismatch between State and Cloud
    TAG_DRIFT = "TAG_DRIFT"   # Only tags differ

@dataclass
class DriftResult:
    """Represents a detected drift on a specific resource."""
    resource_id: str
    resource_type: str
    provider: str
    drift_type: DriftType
    severity: str             # 'high', 'medium', 'low'
    details: Dict[str, Any] = field(default_factory=dict)    