import json
from typing import List, Dict, Any
from dataclasses import asdict
from core.models import DriftResult

class JSONReporter:
    """Exports drift results to a machine-readable JSON format."""
    
    @staticmethod
    def generate(results: List[DriftResult], output_path: str = "output/drift_report.json"):
        report_data = {
            "summary": {
                "total_drift_events": len(results),
                "high_severity": sum(1 for r in results if r.severity == "high"),
                "medium_severity": sum(1 for r in results if r.severity == "medium"),
                "low_severity": sum(1 for r in results if r.severity == "low"),
            },
            "drifts": [
                {
                    "resource_id": r.resource_id,
                    "resource_type": r.resource_type,
                    "provider": r.provider,
                    "drift_type": r.drift_type.value,
                    "severity": r.severity,
                    "details": r.details
                }
                for r in results
            ]
        }
        
        with open(output_path, 'w') as f:
            json.dump(report_data, f, indent=2)
            
        print(f"JSON report generated: {output_path}")