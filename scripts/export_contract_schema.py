"""Generate the versioned JSON Schema artifact from the canonical Pydantic model."""

import json
from pathlib import Path

from cryptopulse.contracts import MarketEvent


def main() -> None:
    destination = Path("schemas/market_event.v1.json")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(MarketEvent.model_json_schema(), indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
