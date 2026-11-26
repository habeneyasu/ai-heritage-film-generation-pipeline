# Reproducible environment for the local stages: Python (via uv), FFmpeg with libass, fonts.
# The GPU stages run on Kaggle and are started from here with `make wan` / `make music`.
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

RUN apt-get update \
 && apt-get install -y --no-install-recommends ffmpeg fonts-dejavu-core make git \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

COPY . .
CMD ["make", "film"]
