# Stage 1: Builder
FROM python:3.12-slim as builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install project dependencies
RUN poetry config virtualenvs.create false && \
    poetry install --only main --no-interaction --no-ansi

# Stage 2: Runtime
FROM python:3.12-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin/uvicorn /usr/local/bin/uvicorn
COPY --from=builder /usr/local/bin/streamlit /usr/local/bin/streamlit

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m appuser && \
    chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

ENTRYPOINT ["sh", "-c"]
CMD ["if [ \"$SERVICE\" = \"api\" ]; then \
        uvicorn app.main:app --host 0.0.0.0 --port 8000; \
     elif [ \"$SERVICE\" = \"streamlit\" ]; then \
        streamlit run streamlit_app/app.py --server.port=8501 --server.address=0.0.0.0; \
     else \
        echo 'Serviço desconhecido: $SERVICE' && exit 1; \
     fi"]