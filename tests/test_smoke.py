"""Smoke tests – ledger helpers + CLI commands."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from clawinvoice.cli import app
from clawinvoice import ledger

runner = CliRunner()


def _tmp_ledger(tmp_path: Path) -> Path:
    return tmp_path / "ledger.jsonl"


# -- ledger helpers ----------------------------------------------------------

def test_append_and_read(tmp_path: Path) -> None:
    path = _tmp_ledger(tmp_path)
    ledger.append_record({"id": "a", "val": 1}, path=path)
    ledger.append_record({"id": "b", "val": 2}, path=path)
    records = ledger.read_all(path=path)
    assert len(records) == 2
    assert records[0]["id"] == "a"


def test_find_by_id(tmp_path: Path) -> None:
    path = _tmp_ledger(tmp_path)
    ledger.append_record({"invoice_id": "abc", "v": 1}, path=path)
    ledger.append_record({"invoice_id": "abc", "v": 2}, path=path)
    rec = ledger.find_by_id("abc", path=path)
    assert rec is not None
    assert rec["v"] == 2  # latest wins


def test_find_by_id_missing(tmp_path: Path) -> None:
    path = _tmp_ledger(tmp_path)
    assert ledger.find_by_id("nope", path=path) is None


# -- CLI commands ------------------------------------------------------------

def test_cli_help() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "create" in result.output
    assert "verify" in result.output
    assert "status" in result.output
    assert "deliver" in result.output


def test_cli_create() -> None:
    result = runner.invoke(app, ["create", "--amount", "10.5", "--memo", "test"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["amount"] == 10.5
    assert data["status"] == "pending"
    assert "invoice_id" in data


def test_cli_status_not_found() -> None:
    result = runner.invoke(app, ["status", "--invoice-id", "nonexistent"])
    assert result.exit_code == 1
    data = json.loads(result.output)
    assert data["error"] == "invoice not found"
