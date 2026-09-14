# ADR 0002: Run the local Delta streaming job in a project-managed Linux container

## Status

Accepted — 2026-09-10

## Context

The developer workstation runs Windows and Python 3.13. Spark unit transforms work with Java 17
and PySpark 3.5.9, but local Delta writes require Windows Hadoop support binaries such as
`winutils.exe`. Shipping an unverified third-party executable would make the project less
reproducible and less trustworthy.

## Decision

Keep lightweight Spark transformation tests runnable on the host with Java 17. Run the
checkpointed Delta/Kafka Structured Streaming job in the repository's `spark` Docker Compose
service, based on Linux, Python 3.11, and Java 17. The service installs the pinned project
streaming dependencies and resolves the matching Delta and Kafka Spark packages at job startup.

## Consequences

- Local Delta behavior is consistent across developer machines with Docker Desktop.
- No `winutils.exe` binary or global Hadoop configuration is required.
- Developers use `make stream` for the continuously-running local job.
- The Docker image and package versions are part of the reproducible runtime contract and must be
  updated together when Spark is upgraded.
