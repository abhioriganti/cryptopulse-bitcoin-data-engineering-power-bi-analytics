FROM python:3.11-slim-bookworm

WORKDIR /workspace

RUN apt-get update \
    && apt-get install --no-install-recommends -y openjdk-17-jre-headless \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY src ./src

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir ".[streaming,ml]" "psycopg[binary]>=3.2,<4"

CMD ["sleep", "infinity"]
