FROM python:3.13-slim-bookworm

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1 
ENV PYTHONPATH=/app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY ./pyproject.toml ./uv.lock ./alembic.ini /app/
COPY ./scripts /app/scripts
COPY ./alembic /app/alembic
COPY ./app /app/app

WORKDIR /app

ENV PATH="/app/.venv/bin:$PATH"

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

CMD ["fastapi", "run", "app/main.py"]