# ---- Stage 1: build the virtual environment ----
FROM python:3.13-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:0.13.1 /uv /bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# Install dependencies first (cached unless pyproject.toml or uv.lock change)
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project

# Then install our own code
COPY . .
RUN uv sync --locked --no-dev --no-editable

# ---- Stage 2: the runtime image ----
FROM python:3.13-slim

RUN groupadd --system --gid 999 app \
 && useradd --system --gid 999 --uid 999 --no-create-home app

COPY --from=builder --chown=app:app /app/.venv /app/.venv

ENV PATH="/app/.venv/bin:$PATH"
WORKDIR /app
USER app

EXPOSE 8000
CMD ["uvicorn", "hygieai_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
