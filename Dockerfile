FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml ./
COPY src ./src
COPY data ./data

RUN uv sync --no-dev

CMD ["uv", "run", "python", "-m", "velmo.chat"]
