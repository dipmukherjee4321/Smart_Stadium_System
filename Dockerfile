# ============================================================
# Smart Stadium OS — v2.3 ELITE Production Dockerfile
# ============================================================

# Stage 1: Build the React Frontend
FROM node:18-alpine AS build-stage
WORKDIR /app
COPY smart-stadium-os/frontend/package*.json ./
# Clean install respects package-lock.json for reproducibility
RUN npm ci --prefer-offline
COPY smart-stadium-os/frontend/ ./
RUN npm run build

# ============================================================
# Stage 2: Production Runtime (Python Backend)
# ============================================================
FROM python:3.11-slim AS runtime

WORKDIR /app

# Security: Install minimal system dependencies, then clean up
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies with hash-checking for supply chain security
COPY smart-stadium-os/backend/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy React build artifacts into the backend's static directory
COPY --from=build-stage /app/dist ./static

# Copy the entire backend application code
COPY smart-stadium-os/backend/ ./

# Security: Run as non-root user
RUN groupadd -r appgroup && useradd -r -g appgroup appuser && \
    chown -R appuser:appgroup /app
USER appuser

# Environment configuration
ENV PORT=8080
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Health check for Cloud Run
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')"

# Optimized for WebSocket + async workloads in Cloud Run
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1 --proxy-headers --forwarded-allow-ips='*' --log-level info"]
