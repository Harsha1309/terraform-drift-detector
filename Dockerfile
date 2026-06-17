# Use a lightweight Python 3.11 base image
FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY drift_detector/ /app/drift_detector/
COPY cli.py /app/
COPY config.yaml /app/

# Create an entrypoint that points directly to our CLI
ENTRYPOINT ["python", "cli.py"]

# Default command (can be overridden to 'scan')
CMD ["daemon"]