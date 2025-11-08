# Use Python 3.13 slim image
FROM python:3.13-slim AS builder

# Set working directory
WORKDIR /app

# Install system dependencies and uv
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    bash \
    git \
    && pip install --no-cache-dir --upgrade pip uv \
    && rm -rf /var/lib/apt/lists/*

ARG DEPLOY_VERSION

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    VERSION=$DEPLOY_VERSION

# Copy project files
COPY pyproject.toml uv.lock README.md ./
COPY src/ ./src/

# Install dependencies using uv
RUN if [ -n "$VERSION" ]; then \
        SETUPTOOLS_SCM_PRETEND_VERSION=$VERSION; \
    fi && \
    uv sync --frozen && \
    uv build --sdist --wheel \
    && mkdir -p /build/dist && cp dist/* /build/dist/

# # ============================================================================
# # API Service Dockerfile
# # ============================================================================
# FROM python:3.13-slim AS app

# # Install the application and its dependencies (without embeddings)
# COPY --from=builder /build/dist /tmp/dist
# RUN pip install --no-cache-dir /tmp/dist/*.whl && rm -rf /tmp/dist
FROM builder AS app
LABEL mode="api" \
      description="CrewAI API service mode"
EXPOSE 8000

# Health check for API mode
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health', timeout=5.0).raise_for_status()" || exit 1

# Environment variables for API mode
ENV UVICORN_HOST=0.0.0.0 \
    API_HOST=0.0.0.0 \
    API_PORT=8000 \
    PYTHONUNBUFFERED=1 \
    UVICORN_PORT=8000 \
    UVICORN_LOG_LEVEL=info

# Run the application using uv
#CMD ["uv", "run", "crewai-runner-api"]
CMD ["uv", "run", "src/engine/main.py"]
#CMD ["uv", "run", "uvicorn", "engine:app", "--host", "0.0.0.0", "--port", "8000"]
