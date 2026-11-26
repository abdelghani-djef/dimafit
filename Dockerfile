# syntax=docker/dockerfile:1

# 1. Build the React app.
FROM node:24-slim AS web
WORKDIR /web
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# 2. The Python API serving the built app. No database: nothing is stored.
FROM python:3.13-slim AS run
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
COPY --from=ghcr.io/astral-sh/uv:0.13.5 /uv /usr/local/bin/uv

WORKDIR /app/backend
COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY backend/app ./app
COPY --from=web /web/dist /app/frontend/dist

ENV PATH="/app/backend/.venv/bin:$PATH" STATIC_DIR=/app/frontend/dist
RUN useradd --create-home --uid 10001 app
USER app
EXPOSE 8000
# Behind Caddy on a private Docker network: trust its X-Forwarded-* headers (client IPs for rate limits).
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips", "*"]
