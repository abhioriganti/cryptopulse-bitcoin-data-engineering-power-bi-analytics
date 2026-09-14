# Failure and recovery demonstrations

These are local reliability experiments, not availability claims. Record outputs and timestamps in
`artifacts/benchmarks/` when running them.

| Experiment | How to run | Expected recovery behavior | Verification |
|---|---|---|---|
| Restart ingestion | Stop the finite/live ingestion command, then restart it | WebSocket reconnect logic resubscribes; publishing resumes with stable event IDs | Consume from Redpanda and inspect ingestion logs |
| Restart Redpanda | `docker compose restart redpanda` | Producer retries/reconnects; Spark recovers from its checkpoint when broker returns | Verify topic production and Delta checkpoint progress |
| Duplicate event | Replay the same controlled sequence twice | Bronze preserves raw arrivals; Silver deterministic event key removes duplicate canonical events | Run reconciliation and inspect duplicate metrics |
| Malformed event | Run `python scripts/publish_invalid_fixture.py` while stream is active | Invalid record reaches quarantine rather than disappearing | Inspect quarantine Delta table; this was verified with one retained fixture |
| Late event | Publish an event older than the configured watermark | Event is handled according to watermark/quality policy and remains observable | Inspect Silver quality flags and streaming query progress |
| Provider rate limit | Use a provider test stub returning HTTP 429 | Exponential retry honors rate-limit handling and logs failure context | Provider adapter unit test and structured logs |
| Missing interval | Replay a sequence with a skipped timestamp | Quality/reconciliation identifies missing expected interval | Review quality mart and reconciliation result |

## Safe local cleanup

Do not delete checkpoints to “fix” a failure. First capture logs, query Delta transaction history,
and run reconciliation. If a deliberately isolated replay run must be reset, remove only that
explicitly named replay output after stopping its corresponding stream; preserve production-like
default lakehouse paths for investigation.

## What is verified so far

- Restartable checkpointed Spark/Delta paths were exercised during controlled replay development.
- A malformed OHLC fixture was retained in quarantine (one row), proving invalid data is not silently
  discarded.
- Duplicate replay and reconciliation behavior were verified with zero layer-count difference.

The remaining experiments are documented runbooks until deliberately executed and captured.
