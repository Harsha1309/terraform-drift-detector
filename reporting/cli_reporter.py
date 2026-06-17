from typing import List
from core.models import DriftResult, DriftType

class CLIReporter:
    """Prints a human-readable, color-coded summary to the console."""

    COLORS = {
        "high": "\033[91m",    # Red
        "medium": "\033[93m",  # Yellow
        "low": "\033[94m",     # Blue
        "reset": "\033[0m"     # Reset
    }

    @classmethod
    def generate(cls, results: List[DriftResult]):
        print("\n" + "="*60)
        print("🔍 INFRASTRUCTURE DRIFT REPORT")
        print("="*60)

        if not results:
            print("\n✅ No drift detected. Infrastructure matches state perfectly.")
            return

        # Group by severity for better scannability
        grouped_results = {"high": [], "medium": [], "low": []}
        for res in results:
            grouped_results[res.severity].append(res)

        for severity in ["high", "medium", "low"]:
            items = grouped_results[severity]
            if not items:
                continue
                
            color = cls.COLORS.get(severity, cls.COLORS["reset"])
            reset = cls.COLORS["reset"]
            
            print(f"\n{color}[{severity.upper()} SEVERITY] - {len(items)} issues found{reset}")
            print("-" * 60)
            
            for item in items:
                drift_type = item.drift_type.value
                print(f"• {item.resource_type} | {item.resource_id}")
                print(f"  Type: {color}{drift_type}{reset}")
                
                # Print a brief summary of details
                if item.drift_type == DriftType.MODIFIED:
                    print(f"  Details: Attribute changes detected")
                elif item.drift_type == DriftType.TAG_DRIFT:
                    print(f"  Details: Tag changes detected")
                else:
                    print(f"  Details: {item.details.get('message', 'N/A')}")
        
        print("\n" + "="*60 + "\n")