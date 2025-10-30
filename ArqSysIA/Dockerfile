# ArqSysIA - Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Install the package
RUN pip install --no-cache-dir -e .

# Create directory for projects
RUN mkdir -p /app/projects

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV ARQSYSIA_DATA_DIR=/app/projects

# Volume for persistent data
VOLUME ["/app/projects"]

# Entry point
ENTRYPOINT ["arqsysia"]

# Default command (show help)
CMD ["--help"]
