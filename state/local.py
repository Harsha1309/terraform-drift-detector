import json
import anyio
from typing import List, Dict, Any
from state.base import StateReader
from core.models import ResourceModel

class LocalStateReader(StateReader):
    """Reads and parses local terraform.tfstate JSON files."""

    async def read_state(self, source_path: str) -> List[ResourceModel]:
        # CHANGE: This must be a standard 'def', NOT 'async def'
        def _read_file():
            with open(source_path, 'r') as f:
                return json.load(f)
                
        try:
            # run_sync safely executes the synchronous _read_file on a worker thread
            state_data = await anyio.to_thread.run_sync(_read_file)
        except FileNotFoundError:
            raise ValueError(f"State file not found at path: {source_path}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON format in state file: {source_path}")

        return self._parse_state(state_data)

    def _parse_state(self, state_data: Dict[str, Any]) -> List[ResourceModel]:
        resources: List[ResourceModel] = []
        
        # Supporting modern Terraform state formats (v4)
        lineage_provider = state_data.get("provider", "unknown")
        
        for mode_block in state_data.get("resources", []):
            resource_type = mode_block.get("type")
            provider_name = mode_block.get("provider", lineage_provider).split(".")[-1]
            
            # Skip data sources; we only check drift on managed resources
            if mode_block.get("mode") != "managed":
                continue

            for instance in mode_block.get("instances", []):
                attributes = instance.get("attributes", {})
                
                # Extract identifiers
                resource_id = attributes.get("id") or instance.get("index_key")
                if not resource_id:
                    continue  # Skip unidentifiable resources
                
                # Separate out tags if present to handle them independently per requirements
                tags = attributes.get("tags", {}) or attributes.get("labels", {})
                cleaned_attributes = {k: v for k, v in attributes.items() if k not in ("tags", "labels")}
                
                # Infer region from ARN, provider metadata, or attributes if available
                region = attributes.get("region") or "global"
                
                resources.append(ResourceModel(
                    resource_id=str(resource_id),
                    resource_type=resource_type,
                    provider=provider_name,
                    region=region,
                    attributes=cleaned_attributes,
                    tags=dict(tags) if isinstance(tags, dict) else {},
                ))
                
        return resources