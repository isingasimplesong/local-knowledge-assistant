# Use Python base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Create a non-root user
RUN useradd -m -u 1000 appuser

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt

# Copy the entire application
COPY . .

# Create necessary directories
RUN mkdir -p /app/data /app/storage /app/config && \
    chown -R appuser:appuser /app

# Move default config files to a template directory
RUN mkdir -p /app/default_config && \
    cp /app/config/* /app/default_config/ && \
    chown -R appuser:appuser /app/default_config

# Expose the port Streamlit runs on
EXPOSE 8501

# Add an entrypoint script
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
