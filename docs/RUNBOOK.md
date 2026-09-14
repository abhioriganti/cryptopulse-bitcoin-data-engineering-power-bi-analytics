# Local runbook

## Windows Spark runtime

Run Delta Structured Streaming inside the Compose `spark` service. Native Windows Spark commonly
requires `winutils.exe`/`HADOOP_HOME` for Delta package resolution; CryptoPulse intentionally avoids
shipping an unverified third-party binary. Java 17 remains useful for the local Spark unit test.

```powershell
docker compose up -d redpanda minio spark
make stream
```

Run `make stream` in a dedicated terminal. It is a continuous service and stops with `Ctrl+C`.
