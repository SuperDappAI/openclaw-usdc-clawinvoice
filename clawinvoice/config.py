"""Load environment / configuration values."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from the project root (two levels up from this file)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_PROJECT_ROOT / ".env")

# --- public helpers -----------------------------------------------------------

RPC_URL: str = os.getenv("RPC_URL", "https://sepolia.base.org")
USDC_CONTRACT: str = os.getenv(
    "USDC_CONTRACT", "0x036CbD53842c5426634e7929541eC2318f3dCF7e"
)
CHAIN_ID: int = int(os.getenv("CHAIN_ID", "84532"))

DATA_DIR: Path = _PROJECT_ROOT / "data"
LEDGER_PATH: Path = DATA_DIR / "ledger.jsonl"
