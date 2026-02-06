"""Load environment / configuration values."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from the project root (two levels up from this file)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_PROJECT_ROOT / ".env")

# --- public helpers -----------------------------------------------------------

# Accept both WEB3_RPC_URL (as documented in skills) and RPC_URL for compat
RPC_URL: str = os.getenv("WEB3_RPC_URL", os.getenv("RPC_URL", "https://sepolia.base.org"))
USDC_CONTRACT: str = os.getenv(
    "USDC_CONTRACT", "0x036CbD53842c5426634e7929541eC2318f3dCF7e"
)
chain_id_str = os.getenv("CHAIN_ID", "84532")
try:
    CHAIN_ID: int = int(chain_id_str)
except ValueError as exc:
    raise ValueError(f"CHAIN_ID must be a valid integer, got: {chain_id_str!r}") from exc

DATA_DIR: Path = _PROJECT_ROOT / "data"
LEDGER_PATH: Path = Path(os.getenv("LEDGER_PATH", str(DATA_DIR / "ledger.jsonl")))
