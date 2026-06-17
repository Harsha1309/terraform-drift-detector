import os
from typing import List
from jinja2 import Template
from core.models import DriftResult

class HTMLReporter:
    """Generates a static HTML dashboard from the drift results."""

    # A simple embedded template for demonstration
    # In a full build, this would be a separate dashboard.html.j2 file
    TEMPLATE_STR = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Drift Detection Dashboard</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 40px; background: #f9fafb; }
            .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 20px; }
            .high { border-left: 4px solid #ef4444; }
            .medium { border-left: 4px solid #f59e0b; }
            .low { border-left: 4px solid #3b82f6; }
            h1 { color: #111827; }
            .tag { display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
            .tag.high { background: #fee2e2; color: #991b1b; border: none; }
            .tag.medium { background: #fef3c7; color: #92400e; border: none; }
            .tag.low { background: #dbeafe; color: #1e40af; border: none; }
            code { background: #f3f4f6; padding: 2px 4px; border-radius: 4px; }
        </style>
    </head>
    <body>
        <h1>Drift Detection Report</h1>
        <p>Total Drift Events: <strong>{{ results|length }}</strong></p>
        
        {% for result in results %}
        <div class="card {{ result.severity }}">
            <h3>{{ result.resource_id }} 
                <span class="tag {{ result.severity }}">{{ result.drift_type.value }}</span>
            </h3>
            <p><strong>Type:</strong> <code>{{ result.resource_type }}</code> | <strong>Provider:</strong> {{ result.provider }}</p>
        </div>
        {% else %}
        <div class="card">
            <p>No drift detected. Everything is matching!</p>
        </div>
        {% endfor %}
    </body>
    </html>
    """

    @classmethod
    def generate(cls, results: List[DriftResult], output_path: str = "drift_dashboard.html"):
        template = Template(cls.TEMPLATE_STR)
        
        # Render the HTML with our results
        html_content = template.render(results=results)
        
        with open(output_path, 'w') as f:
            f.write(html_content)
            
        print(f"HTML dashboard generated: {os.path.abspath(output_path)}")