"""Quality results retained by later pipeline phases rather than discarded."""

from dataclasses import dataclass
from enum import StrEnum

from cryptopulse.contracts import MarketEvent


class QualityStatus(StrEnum):
    PASS = "pass"
    FAIL = "fail"


@dataclass(frozen=True)
class QualityResult:
    rule: str
    status: QualityStatus
    message: str


def validate_event(event: MarketEvent) -> list[QualityResult]:
    """Apply explicit downstream quality rules after Pydantic contract validation."""
    results: list[QualityResult] = []
    if event.event_timestamp > event.ingested_at:
        results.append(
            QualityResult(
                "event_not_future", QualityStatus.FAIL, "event timestamp is after ingestion"
            )
        )
    if event.event_type.value == "bar" and event.volume is None:
        results.append(
            QualityResult("bar_volume_present", QualityStatus.FAIL, "bar volume is missing")
        )
    if not results:
        results.append(
            QualityResult("canonical_event_valid", QualityStatus.PASS, "event passed checks")
        )
    return results
