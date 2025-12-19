# syntax=docker/dockerfile:1

FROM python:3.12-slim

# ---- runtime defaults ----
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DB_PATH=/data/stravit.db

WORKDIR /app

# ---- system deps (absolute minimum) ----
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# ---- uv binary ----
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# ---- deps (cache-friendly) ----
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

ENV PATH="/app/.venv/bin:$PATH"

# ---- app code ----
COPY stravit_companion ./stravit_companion

# ---- sqlite persistence ----
VOLUME ["/data"]

# ---- run the job ----
ENTRYPOINT ["python", "-m", "stravit_companion.runner"]
