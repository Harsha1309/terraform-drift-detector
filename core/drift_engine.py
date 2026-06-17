from typing import List, Dict
from deepdiff import DeepDiff
from core.models import ResourceModel, DriftResult, DriftType

class DriftEngine:
    """
    Compares expected resources against actual resources to identify configuration drift.
    """

    def detect_drift(self, expected_resources: List[ResourceModel], actual_resources: List[ResourceModel]) -> List[DriftResult]:
        drift_results: List[DriftResult] = []

        # Convert to dictionaries keyed by the canonical ID for O(1) lookups
        expected_map = {res.canonical_id: res for res in expected_resources}
        actual_map = {res.canonical_id: res for res in actual_resources}

        # 1. Detect DELETED and MODIFIED/TAG_DRIFT resources
        for canonical_id, expected_res in expected_map.items():
            actual_res = actual_map.get(canonical_id)

            # DELETED: Exists in state, missing in cloud
            if not actual_res:
                drift_results.append(
                    self._create_result(expected_res, DriftType.DELETED, "high", {"message": "Resource missing in cloud environment"})
                )
                continue

            # Compare Attributes (MODIFIED)
            attr_diff = DeepDiff(expected_res.attributes, actual_res.attributes, ignore_order=True)
            
            # Compare Tags (TAG_DRIFT)
            tag_diff = DeepDiff(expected_res.tags, actual_res.tags, ignore_order=True)

            if attr_diff:
                drift_results.append(
                    self._create_result(expected_res, DriftType.MODIFIED, "high", {"attribute_changes": attr_diff.to_dict()})
                )
            
            # We evaluate tag drift independently so teams can filter for just tag compliance
            if tag_diff:
                # Severity is lower for tags unless specified otherwise
                drift_results.append(
                    self._create_result(expected_res, DriftType.TAG_DRIFT, "low", {"tag_changes": tag_diff.to_dict()})
                )

        # 2. Detect UNMANAGED resources (Exists in cloud, missing in state)
        for canonical_id, actual_res in actual_map.items():
            if canonical_id not in expected_map:
                drift_results.append(
                    self._create_result(actual_res, DriftType.UNMANAGED, "medium", {"message": "Resource found in cloud but not tracked in state"})
                )

        return drift_results

    def _create_result(self, resource: ResourceModel, drift_type: DriftType, severity: str, details: Dict) -> DriftResult:
        """Helper to standardize drift result creation."""
        return DriftResult(
            resource_id=resource.resource_id,
            resource_type=resource.resource_type,
            provider=resource.provider,
            drift_type=drift_type,
            severity=severity,
            details=details
        )