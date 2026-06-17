import asyncio
import time
from typing import List, Dict, Any

from core.models import DriftResult
from core.drift_engine import DriftEngine
from state.local import LocalStateReader
from providers.aws import AWSCloudFetcher

class ScanRunner:
    """Orchestrates the end-to-end drift detection scan."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.drift_engine = DriftEngine()
        
        # In a fully fleshed-out app, use a Factory pattern here based on config
        self.state_reader = LocalStateReader()
        self.cloud_fetcher = AWSCloudFetcher()

    async def run_scan(self) -> List[DriftResult]:
        """Runs the left (state) and right (cloud) pipelines concurrently."""
        print("Starting infrastructure drift scan...")
        start_time = time.perf_counter()

        # 1. Setup execution paths based on config
        state_path = self.config.get('state_source', {}).get('path', 'terraform.tfstate')
        cloud_config = self.config.get('cloud_target', {})

        # 2. Fire both fetchers concurrently to save time
        expected_coro = self.state_reader.read_state(state_path)
        actual_coro = self.cloud_fetcher.fetch_resources(cloud_config)
        
        try:
            expected_resources, actual_resources = await asyncio.gather(expected_coro, actual_coro)
        except Exception as e:
            print(f"Scan failed during extraction phase: {e}")
            return []

        # 3. Compute the drift
        drift_results = self.drift_engine.detect_drift(expected_resources, actual_resources)

        elapsed = time.perf_counter() - start_time
        
        # High-level summary
        total_drift = len(drift_results)
        print(f"Scan completed in {elapsed:.2f} seconds.")
        print(f"Analyzed {len(expected_resources)} state resources vs {len(actual_resources)} cloud resources.")
        print(f"Found {total_drift} drifting items.")

        return drift_results