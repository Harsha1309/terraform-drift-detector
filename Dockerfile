# Build stage
FROM python:3.11-slim AS builder

WORKDIR /app

# Install dependencies in the builder stage
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy Python dependencies from builder stage
COPY --from=builder /root/.local /root/.local

# Set PATH to use user-installed packages
ENV PATH=/root/.local/bin:$PATH

# Copy the application code
COPY cli.py /app/
COPY config.yaml /app/
COPY core/ /app/core/
COPY providers/ /app/providers/
COPY reporting/ /app/reporting/
COPY state/ /app/state/
COPY terraform/ /app/terraform/

# Create output directory
RUN mkdir -p /app/output

# Create an entrypoint that points directly to our CLI
ENTRYPOINT ["python", "cli.py"]

# Default command (can be overridden to 'scan')
CMD ["daemon"]