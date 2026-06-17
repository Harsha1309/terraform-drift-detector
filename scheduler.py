import asyncio
import yaml
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from core.runner import ScanRunner

def load_config(config_path: str) -> dict:
    """Loads the YAML configuration file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

async def execute_job(config: dict):
    """The actual job executed by the scheduler."""
    runner = ScanRunner(config)
    results = runner.run_scan()
    
    # In Phase 4, we will pass `results` to the ReportGenerator here.
    # For now, we'll just acknowledge completion.
    print(f"[Job Execution] Successfully processed {len(results)} drift events.\n")

def start_scheduler(config_path: str = "config.yaml"):
    """Initializes and runs the continuous drift scanning daemon."""
    config = load_config(config_path)
    cron_expr = config.get("scan_settings", {}).get("cron", "0 * * * *")
    
    scheduler = AsyncIOScheduler()
    
    # Parse standard cron string to APScheduler CronTrigger
    trigger = CronTrigger.from_crontab(cron_expr)
    
    # Add the scan job
    scheduler.add_job(
        execute_job, 
        trigger=trigger, 
        args=[config],
        id="drift_scan_job",
        replace_existing=True,
        coalesce=True # Prevents running multiple times if the system pauses
    )
    
    scheduler.start()
    print(f"Drift Detection Scheduler started. Running on schedule: {cron_expr}")
    print("Press Ctrl+C to exit.")
    
    # Block the main thread to keep the async event loop alive
    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        print("Shutting down scheduler...")
        scheduler.shutdown()