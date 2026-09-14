"""Report local lakehouse maintenance candidates without deleting data."""

import argparse
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if not args.dry_run:
        raise SystemExit(
            "Only --dry-run is implemented; retention deletion requires an approved policy."
        )
    root = Path("data")
    delta_logs = list(root.rglob("_delta_log")) if root.exists() else []
    print(f"dry_run_delta_tables={len(delta_logs)}")


if __name__ == "__main__":
    main()
