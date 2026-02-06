"""ClawInvoice CLI – typer application with create / verify / status / deliver."""

from __future__ import annotations

import json
import time
import uuid

import typer

from clawinvoice import ledger

app = typer.Typer(help="ClawInvoice – USDC invoice CLI for agentic commerce.")


def _print_json(data: dict) -> None:
    typer.echo(json.dumps(data, indent=2))


# ---------------------------------------------------------------------------
# create
# ---------------------------------------------------------------------------
@app.command()
def create(
    amount: float = typer.Option(..., help="Invoice amount in USDC"),
    memo: str = typer.Option("", help="Human-readable memo"),
    expiry: int = typer.Option(3600, help="Seconds until expiry"),
) -> None:
    """Create a new invoice and write it to the ledger."""
    now = int(time.time())
    record = {
        "invoice_id": uuid.uuid4().hex,
        "amount": amount,
        "memo": memo,
        "status": "pending",
        "created_at": now,
        "expires_at": now + expiry,
        "tx": None,
        "proof_url": None,
    }
    ledger.append_record(record)
    _print_json(record)


# ---------------------------------------------------------------------------
# verify
# ---------------------------------------------------------------------------
@app.command()
def verify(
    invoice_id: str = typer.Option(..., help="Invoice ID to verify"),
    tx: str = typer.Option(..., help="On-chain transaction hash"),
) -> None:
    """Mark an invoice as verified with a tx hash (stub)."""
    rec = ledger.find_by_id(invoice_id)
    if rec is None:
        _print_json({"error": "invoice not found", "invoice_id": invoice_id})
        raise typer.Exit(code=1)
    rec["status"] = "verified"
    rec["tx"] = tx
    ledger.append_record(rec)
    _print_json(rec)


# ---------------------------------------------------------------------------
# status
# ---------------------------------------------------------------------------
@app.command()
def status(
    invoice_id: str = typer.Option(..., help="Invoice ID to query"),
) -> None:
    """Print current status of an invoice."""
    rec = ledger.find_by_id(invoice_id)
    if rec is None:
        _print_json({"error": "invoice not found", "invoice_id": invoice_id})
        raise typer.Exit(code=1)
    _print_json(rec)


# ---------------------------------------------------------------------------
# deliver
# ---------------------------------------------------------------------------
@app.command()
def deliver(
    invoice_id: str = typer.Option(..., help="Invoice ID"),
    proof_url: str = typer.Option(..., help="URL proving delivery"),
) -> None:
    """Mark an invoice as delivered with a proof URL (stub)."""
    rec = ledger.find_by_id(invoice_id)
    if rec is None:
        _print_json({"error": "invoice not found", "invoice_id": invoice_id})
        raise typer.Exit(code=1)
    rec["status"] = "delivered"
    rec["proof_url"] = proof_url
    ledger.append_record(rec)
    _print_json(rec)


if __name__ == "__main__":
    app()
