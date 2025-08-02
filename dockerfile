# Use Python base image
FROM python:3.12.5-slim-bullseye
WORKDIR /app

# Install system dependencies for PostgreSQL and general requirements
RUN apt-get update && apt-get install -y \
    openssh-client \
    curl \
    git \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt requirements.txt
RUN python -m pip install --upgrade pip \
    && pip3 install --default-timeout=100 -r requirements.txt

# Copy application code
COPY . .

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser \
    && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 3100

# Set the startup command
CMD ["python3", "-u", "run.py"]