# Dockerfile
FROM python:3.10-slim

WORKDIR /app

# System dependencies for audio processing
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry install --no-dev

# Application code
COPY src/ ./src/
COPY web/ ./web/

EXPOSE 5000

CMD ["poetry", "run", "python", "-m", "src.api.app"]