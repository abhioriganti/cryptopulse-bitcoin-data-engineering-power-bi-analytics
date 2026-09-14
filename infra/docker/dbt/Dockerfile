FROM python:3.11-slim-bookworm

WORKDIR /workspace
RUN pip install --no-cache-dir "dbt-postgres==1.11.0"

ENTRYPOINT ["dbt"]
