# CryptoPulse Analytics Assistant

The assistant is intentionally a constrained analytics tool, not an investment-advice chatbot.
It supports selected curated metric questions without requiring LLM credentials. Each response
returns the answer, exact SQL, allowlisted source tables, metric definition, and result rows.

## Safety controls

- Fixed metric templates; no unrestricted SQL generation.
- PostgreSQL session is read-only and has a five-second statement timeout.
- Tables are allowlisted in `src/cryptopulse/assistant/sql_safety.py`.
- Only one `SELECT`/CTE statement is allowed, with an explicit SQL `LIMIT` and API row-limit cap.
- DDL, DML, comments, multiple statements, and non-allowlisted tables are rejected.
- Unsupported questions, including investment-advice requests, return a structured 422 response.

## Local request

For a browser-friendly request, open:

`http://localhost:8000/assistant/query?question=Which%20forecasting%20model%20had%20the%20lowest%20MAE%3F`

For the structured POST API:

```powershell
Invoke-WebRequest -UseBasicParsing -Method Post -ContentType 'application/json' `
  -Body '{"question":"Which forecasting model had the lowest MAE?"}' `
  http://localhost:8000/assistant/query
```

Representative expected behavior is captured in `evaluation_dataset.json`. An OpenAI-compatible
provider can be added later only as a planner constrained to the same metric templates and SQL
validator; no LLM access is needed for the current implementation.
