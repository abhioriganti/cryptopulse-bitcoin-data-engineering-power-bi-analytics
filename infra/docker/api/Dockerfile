FROM python:3.11-slim-bookworm

WORKDIR /workspace

COPY pyproject.toml README.md ./
COPY src ./src

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir . "psycopg[binary]>=3.2,<4"

CMD ["python", "-m", "uvicorn", "cryptopulse.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
