"""Persist reconciliation evidence for reporting and workflow decisions."""

from dataclasses import dataclass
from typing import Any
from uuid import UUID, uuid4


@dataclass(frozen=True)
class ReconciliationResult:
    name: str
    left_count: int
    right_count: int
    threshold: int = 0

    @property
    def difference(self) -> int:
        return self.left_count - self.right_count

    @property
    def status(self) -> str:
        return "pass" if abs(self.difference) <= self.threshold else "fail"


def persist_reconciliations(connection: Any, results: list[ReconciliationResult]) -> UUID:
    """Store results under one run identifier before a workflow decides whether to fail."""
    run_id = uuid4()
    with connection.cursor() as cursor:
        for result in results:
            cursor.execute(
                "insert into raw.reconciliation_results ("
                "reconciliation_id, run_id, reconciliation_name, left_count, right_count, "
                "difference, status, threshold) values (%s, %s, %s, %s, %s, %s, %s, %s)",
                (
                    uuid4(),
                    run_id,
                    result.name,
                    result.left_count,
                    result.right_count,
                    result.difference,
                    result.status,
                    result.threshold,
                ),
            )
    connection.commit()
    return run_id
