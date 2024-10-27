# Build stage
FROM python:3.12-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create and activate virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.12-slim

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create a non-root user
RUN useradd -m -u 1000 appuser

# Set working directory
WORKDIR /app

# Copy only necessary files
COPY --chown=appuser:appuser main.py .
COPY --chown=appuser:appuser config ./config/
COPY --chown=appuser:appuser entrypoint.sh .

# Create necessary directories
RUN mkdir -p /app/data /app/storage /app/config && \
    chown -R appuser:appuser /app && \
    mkdir -p /app/default_config && \
    cp /app/config/* /app/default_config/ && \
    chown -R appuser:appuser /app/default_config && \
    chmod +x entrypoint.sh

RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Expose port
EXPOSE 8501

ENTRYPOINT ["./entrypoint.sh"]
