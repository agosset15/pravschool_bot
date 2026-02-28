FROM ghcr.io/astral-sh/uv:python3.12-alpine AS builder

WORKDIR /opt/pravschool_bot

COPY pyproject.toml uv.lock ./

RUN uv sync --locked --no-dev --no-cache --compile-bytecode \
    && find .venv -type d -name "__pycache__" -exec rm -rf {} + \
    && rm -rf .venv/lib/python3.12/site-packages/pip* \
    && rm -rf .venv/lib/python3.12/site-packages/setuptools* \
    && rm -rf .venv/lib/python3.12/site-packages/wheel*

FROM python:3.12-alpine AS production

WORKDIR /opt/pravschool_bot

COPY --from=builder /opt/pravschool_bot/.venv /opt/pravschool_bot/.venv

ENV PATH="/opt/pravschool_bot/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/opt/pravschool_bot

COPY ./src ./src
COPY ./assets ./assets
COPY ./docker-entrypoint.sh ./docker-entrypoint.sh
RUN mkdir "temp"

RUN chmod +x ./docker-entrypoint.sh

CMD ["./docker-entrypoint.sh"]