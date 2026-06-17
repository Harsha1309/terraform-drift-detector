# 🔍 Terraform Drift Detection Platform

A lightweight, continuous infrastructure drift detection tool. This platform compares your expected infrastructure state (Terraform `.tfstate`) against your actual live cloud environment (AWS, Azure, GCP) to identify unauthorized changes, manual modifications, and tag discrepancies.

---

## 🏗️ Architecture & Flow

The system operates using a highly concurrent, split-pipeline architecture:

1. **Left Pipeline (State Extraction):** Reads local or remote `terraform.tfstate` files and extracts managed resources into a normalized schema.
2. **Right Pipeline (Cloud Fetching):** Connects directly to cloud provider APIs (e.g., via `boto3`) to fetch live resource configurations into the identical normalized schema.
3. **Drift Engine:** Merges both pipelines using a canonical ID and performs a deep dictionary diff to categorize changes into four states:
   * 🔴 **DELETED:** Exists in Terraform state, missing in the cloud.
   * 🟡 **UNMANAGED:** Exists in the cloud, untracked by Terraform.
   * 🔴 **MODIFIED:** Attribute-level configuration mismatch.
   * 🔵 **TAG_DRIFT:** Only tags or labels differ.

---

## ✨ Features
* **Asynchronous Execution:** Uses `asyncio` to fetch cloud state and read local state concurrently for ultra-fast scans.
* **Smart Comparison:** Powered by `DeepDiff` to handle complex, nested configuration attributes natively.
* **Multi-Format Reporting:** * 🖥️ **CLI:** Rich, color-coded console output for developers.
  * 📊 **HTML Dashboard:** A standalone, dependency-free visual web report.
  * 🤖 **JSON:** Machine-readable output optimized for CI/CD pipeline gates.
* **Built-in Automation:** Includes an asynchronous cron scheduler for continuous background monitoring.

---

## 📂 Project Structure

```text
drift_detector/
├── core/
│   ├── models.py          # Unified data models (ResourceModel, DriftResult)
│   ├── drift_engine.py    # DeepDiff comparison logic
│   └── runner.py          # Asynchronous orchestrator
├── providers/
│   ├── base.py            # CloudFetcher abstract interface
│   └── aws.py             # Boto3 AWS implementation
├── state/
│   ├── base.py            # StateReader abstract interface
│   └── local.py           # Terraform .tfstate parser
├── reporting/
│   ├── json_reporter.py
│   ├── cli_reporter.py
│   └── html_reporter.py
├── cli.py                 # Click-based command line interface
├── scheduler.py           # APScheduler continuous daemon
├── config.yaml            # Scan configuration parameters
├── requirements.txt       # Python dependencies
└── Dockerfile             # Containerization instructions