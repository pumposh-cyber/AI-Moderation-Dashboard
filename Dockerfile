# Multi-stage build for production
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -u 1000 appuser

# Copy Python dependencies from builder to a location accessible by appuser
COPY --from=builder /root/.local /home/appuser/.local

# Set ownership and make sure scripts in .local are usable
RUN chown -R appuser:appuser /home/appuser/.local
ENV PATH=/home/appuser/.local/bin:$PATH

# Copy application code
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# Copy entrypoint script
COPY entrypoint.sh /app/entrypoint.sh

# Set ownership
RUN chown -R appuser:appuser /app && \
    chmod +x /app/entrypoint.sh

# Switch to non-root user
USER appuser

# Expose port (default 8000, but PORT env var can override)
EXPOSE 8000

# Health check (uses default port, Railway will override PORT at runtime)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import os, urllib.request; port=os.getenv('PORT', '8000'); urllib.request.urlopen(f'http://localhost:{port}/health')" || exit 1

# Use entrypoint script that handles PORT environment variable
ENTRYPOINT ["/app/entrypoint.sh"]

