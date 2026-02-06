"""JSONL ledger helpers – append / read / query invoice records."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from clawinvoice.config import LEDGER_PATH


def _ensure_file(path: Path = LEDGER_PATH) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.touch()
    return path


def append_record(record: dict[str, Any], path: Path = LEDGER_PATH) -> None:
    """Append a single JSON record as one line."""
    _ensure_file(path)
    with path.open("a") as fh:
        fh.write(json.dumps(record) + "\n")


def read_all(path: Path = LEDGER_PATH) -> list[dict[str, Any]]:
    """Return every record in the ledger."""
    _ensure_file(path)
    records: list[dict[str, Any]] = []
    with path.open() as fh:
        for lineno, line in enumerate(fh, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Malformed JSON in ledger file {path} at line {lineno}"
                ) from exc
    return records


def find_by_id(invoice_id: str, path: Path = LEDGER_PATH) -> dict[str, Any] | None:
    """Return the *latest* record with the given invoice_id, or None."""
    match: dict[str, Any] | None = None
    for rec in read_all(path):
        if rec.get("invoice_id") == invoice_id:
            match = rec
    return match
