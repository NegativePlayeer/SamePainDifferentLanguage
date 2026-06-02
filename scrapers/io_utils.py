"""JSON/CSV helpers for song dataset I/O."""

import json
from pathlib import Path

import pandas as pd


def save_to_json(data, filepath: str | Path) -> None:
    """Save a list or dict to a JSON file, creating parent dirs if needed."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_from_json(filepath: str | Path):
    """Load JSON from disk."""
    with Path(filepath).open(encoding="utf-8") as f:
        return json.load(f)


def save_records_to_csv(records: list[dict], filepath: str | Path) -> None:
    """Save a list of song records to CSV."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(records).to_csv(path, index=False, encoding="utf-8")


def load_records_from_csv(filepath: str | Path) -> list[dict]:
    """Load song records from CSV as list of dicts."""
    return pd.read_csv(filepath).to_dict(orient="records")
