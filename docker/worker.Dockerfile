# syntax=docker/dockerfile:1.7

FROM python:3.13-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    HF_HOME=/models
RUN useradd --create-home --uid 10001 worker \
    && mkdir -p /models \
    && chown worker:worker /models
COPY workers/processor/pyproject.toml workers/processor/README.md workers/processor/LICENSE ./
COPY workers/processor/src ./src
RUN --mount=type=cache,target=/root/.cache/pip pip install ".[local]"
USER worker
CMD ["python", "-m", "oc_worker.main"]
