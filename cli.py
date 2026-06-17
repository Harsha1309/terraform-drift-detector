import asyncio
import click
import yaml

from core.runner import ScanRunner
from scheduler import start_scheduler
from reporting.cli_reporter import CLIReporter
from reporting.json_reporter import JSONReporter
from reporting.html_reporter import HTMLReporter

def load_config(config_path: str) -> dict:
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

@click.group()
def cli():
    """Terraform Drift Detection Platform"""
    pass

@cli.command()
@click.option('--config', default='config.yaml', help='Path to configuration YAML file.')
@click.option('--format', '-f', type=click.Choice(['cli', 'json', 'html', 'all']), default='cli', help='Output format.')
def scan(config, format):
    """Run an on-demand infrastructure drift scan."""
    cfg = load_config(config)
    runner = ScanRunner(cfg)
    
    # Run the async scan loop
    results = asyncio.run(runner.run_scan())

    # Route to the appropriate reporter
    if format in ['cli', 'all']:
        CLIReporter.generate(results)
    if format in ['json', 'all']:
        JSONReporter.generate(results)
    if format in ['html', 'all']:
        HTMLReporter.generate(results)

@cli.command()
@click.option('--config', default='config.yaml', help='Path to configuration YAML file.')
def daemon(config):
    """Start the continuous drift detection scheduler."""
    start_scheduler(config_path=config)

if __name__ == '__main__':
    cli()