"""HTTP surface for curated CryptoPulse data; serving queries land in Phase 10."""

from datetime import UTC, datetime
from typing import Any, Literal

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from pydantic import BaseModel, Field

from cryptopulse.api.repository import MarketRepository
from cryptopulse.assistant.engine import answer_question
from cryptopulse.common.config import get_settings
from cryptopulse.observability.metrics import SERVING_STORE_UP, observe_request

app = FastAPI(
    title="CryptoPulse API", version="0.1.0", description="Read-only market intelligence API"
)


@app.middleware("http")
async def collect_http_metrics(request: Any, call_next: Any) -> Any:
    """Capture route-level latency and status without high-cardinality request labels."""
    from time import perf_counter

    started_at = perf_counter()
    response = await call_next(request)
    route = request.scope.get("route")
    route_path = getattr(route, "path", request.url.path)
    observe_request(request.method, route_path, response.status_code, started_at)
    return response


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime


class Pagination(BaseModel):
    items: list[dict[str, Any]] = []
    limit: int = Field(ge=1, le=1_000)
    offset: int = Field(ge=0)


class AssistantQuery(BaseModel):
    question: str = Field(min_length=3, max_length=500)
    row_limit: int = Field(default=100, ge=1, le=1_000)


class AssistantAnswer(BaseModel):
    answer: str
    sql: str
    tables_used: list[str]
    metric_definition: str
    rows: list[dict[str, Any]]


def get_repository() -> MarketRepository:
    """Create a repository using the typed configured PostgreSQL DSN."""
    return MarketRepository(str(get_settings().postgres_dsn))


def database_error(error: Exception) -> HTTPException:
    """Avoid exposing connection detail while retaining a structured dependency error."""
    return HTTPException(
        status_code=503, detail={"code": "serving_store_unavailable", "message": str(error)}
    )


@app.get("/health", response_model=HealthResponse, tags=["platform"])
def health() -> HealthResponse:
    return HealthResponse(status="ok", timestamp=datetime.now(UTC))


@app.get("/ready", response_model=HealthResponse, tags=["platform"])
def ready(repository: MarketRepository = Depends(get_repository)) -> HealthResponse:  # noqa: B008
    """Check the read-only serving-store dependency."""
    try:
        repository.ping()
    except Exception as error:
        SERVING_STORE_UP.set(0)
        raise database_error(error) from error
    SERVING_STORE_UP.set(1)
    return HealthResponse(status="ready", timestamp=datetime.now(UTC))


@app.get("/metrics", include_in_schema=False)
def prometheus_metrics() -> Response:
    """Expose Prometheus metrics; unauthenticated only in local Compose."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/market/latest", tags=["market"])
def market_latest(repository: MarketRepository = Depends(get_repository)) -> dict[str, Any]:  # noqa: B008
    try:
        result = repository.latest_market_bar()
    except Exception as error:
        raise database_error(error) from error
    if result is None:
        raise HTTPException(status_code=404, detail={"code": "market_data_not_found"})
    return result


@app.get("/market/history", response_model=Pagination, tags=["market"])
def market_history(
    interval: Literal["1 minute", "5 minutes", "15 minutes", "1 hour"] = "1 minute",
    limit: int = Query(default=100, ge=1, le=1_000),
    offset: int = Query(default=0, ge=0),
    repository: MarketRepository = Depends(get_repository),  # noqa: B008
) -> Pagination:
    try:
        return Pagination(
            items=repository.market_history(interval, limit, offset), limit=limit, offset=offset
        )
    except Exception as error:
        raise database_error(error) from error


@app.get("/market/metrics", tags=["market"])
def metrics(repository: MarketRepository = Depends(get_repository)) -> dict[str, Any]:  # noqa: B008
    return market_latest(repository)


@app.get("/forecast/latest", response_model=Pagination, tags=["forecasting"])
def forecast_latest(
    limit: int = Query(default=100, ge=1, le=1_000),
    repository: MarketRepository = Depends(get_repository),  # noqa: B008
) -> Pagination:
    try:
        return Pagination(items=repository.latest_forecasts(limit), limit=limit, offset=0)
    except Exception as error:
        raise database_error(error) from error


@app.get("/anomalies", response_model=Pagination, tags=["quality"])
def anomalies(
    limit: int = Query(default=100, ge=1, le=1_000),
    offset: int = Query(default=0, ge=0),
    repository: MarketRepository = Depends(get_repository),  # noqa: B008
) -> Pagination:
    try:
        return Pagination(items=repository.anomalies(limit, offset), limit=limit, offset=offset)
    except Exception as error:
        raise database_error(error) from error


@app.get("/data-quality", response_model=Pagination, tags=["quality"])
def data_quality(
    limit: int = Query(default=100, ge=1, le=1_000),
    repository: MarketRepository = Depends(get_repository),  # noqa: B008
) -> Pagination:
    try:
        return Pagination(items=repository.quality_results(limit), limit=limit, offset=0)
    except Exception as error:
        raise database_error(error) from error


@app.get("/pipeline-health", tags=["platform"])
def pipeline_health(repository: MarketRepository = Depends(get_repository)) -> dict[str, Any]:  # noqa: B008
    try:
        return repository.pipeline_health()
    except Exception as error:
        raise database_error(error) from error


@app.post("/assistant/query", response_model=AssistantAnswer, tags=["assistant"])
def assistant_query(payload: AssistantQuery) -> AssistantAnswer:
    """Answer supported metric questions with read-only SQL provenance; never investment advice."""
    try:
        result = answer_question(
            payload.question, str(get_settings().postgres_dsn), payload.row_limit
        )
    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail={"code": "unsupported_assistant_question", "message": str(error)},
        ) from error
    except Exception as error:
        raise database_error(error) from error
    return AssistantAnswer(
        answer=result.answer,
        sql=result.sql,
        tables_used=result.tables_used,
        metric_definition=result.metric_definition,
        rows=result.rows,
    )


@app.get("/assistant/query", response_model=AssistantAnswer, tags=["assistant"])
def assistant_query_browser(
    question: str = Query(min_length=3, max_length=500),
    row_limit: int = Query(default=100, ge=1, le=1_000),
) -> AssistantAnswer:
    """Browser-friendly wrapper for supported assistant questions; no state is changed."""
    return assistant_query(AssistantQuery(question=question, row_limit=row_limit))


def run() -> None:
    """Entrypoint used by the console script."""
    import uvicorn

    settings = get_settings()
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level=settings.log_level.lower())
