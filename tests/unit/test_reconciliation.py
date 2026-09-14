from cryptopulse.quality.persistence import ReconciliationResult


def test_reconciliation_passes_at_threshold() -> None:
    assert ReconciliationResult("test", 10, 9, threshold=1).status == "pass"


def test_reconciliation_fails_outside_threshold() -> None:
    assert ReconciliationResult("test", 10, 8).status == "fail"
