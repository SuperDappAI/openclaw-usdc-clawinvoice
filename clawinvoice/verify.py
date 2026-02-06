"""On-chain USDC payment verification for Base Sepolia.

Connects to an RPC endpoint, fetches a transaction receipt,
and inspects ERC-20 Transfer logs emitted by the configured
USDC token contract.
"""

from __future__ import annotations

import dataclasses
from typing import Any

from web3 import Web3

from clawinvoice.config import RPC_URL, USDC_CONTRACT

# Pre-computed keccak-256 of the canonical ERC-20 event signature
# "Transfer(address,address,uint256)" — stored without the 0x prefix
# so it can be compared directly with HexBytes.hex() output.
_TRANSFER_EVENT_HASH = (
    "ddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
)

# USDC token uses 6 decimal places.
_USDC_DECIMALS = 6


class PaymentVerificationError(Exception):
    """Raised when on-chain payment verification cannot succeed."""


@dataclasses.dataclass(frozen=True)
class USDCTransferInfo:
    """Parsed result from an on-chain USDC Transfer event."""

    sender: str
    recipient: str
    raw_units: int
    usdc_amount: float
    block_ts: int
    tx_hash: str


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _connect(rpc_url: str = RPC_URL) -> Web3:
    """Return a connected Web3 instance or raise on failure."""
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not w3.is_connected():
        raise PaymentVerificationError(
            f"Unable to reach RPC at {rpc_url}"
        )
    return w3


def _address_from_topic(topic_bytes: bytes) -> str:
    """Extract a checksummed address from a 32-byte log topic."""
    raw_hex = "0x" + topic_bytes.hex()[-40:]
    return Web3.to_checksum_address(raw_hex)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def fetch_usdc_transfer(
    tx_hash: str,
    *,
    rpc_url: str = RPC_URL,
    usdc_addr: str = USDC_CONTRACT,
) -> USDCTransferInfo:
    """Retrieve the USDC Transfer event from *tx_hash*.

    Raises ``PaymentVerificationError`` when the tx cannot be fetched or
    contains no matching Transfer log from the expected USDC contract.
    """
    w3 = _connect(rpc_url)

    try:
        receipt = w3.eth.get_transaction_receipt(tx_hash)
    except Exception as err:
        raise PaymentVerificationError(
            f"Could not retrieve receipt for {tx_hash}: {err}"
        ) from err

    target_contract = usdc_addr.lower()
    found_transfer = None

    for entry in receipt.get("logs", []):
        if entry["address"].lower() != target_contract:
            continue
        topics = entry.get("topics", [])
        if len(topics) < 3:
            continue
        if topics[0].hex() == _TRANSFER_EVENT_HASH:
            found_transfer = entry
            break

    if found_transfer is None:
        raise PaymentVerificationError(
            f"Transaction {tx_hash} has no USDC Transfer event "
            f"from contract {usdc_addr}"
        )

    topics = found_transfer["topics"]
    raw_value = int(found_transfer["data"].hex(), 16)

    blk = w3.eth.get_block(receipt["blockNumber"])

    return USDCTransferInfo(
        sender=_address_from_topic(topics[1]),
        recipient=_address_from_topic(topics[2]),
        raw_units=raw_value,
        usdc_amount=raw_value / 10**_USDC_DECIMALS,
        block_ts=blk["timestamp"],
        tx_hash=tx_hash,
    )


def validate_against_invoice(
    transfer: USDCTransferInfo,
    invoice: dict[str, Any],
) -> list[str]:
    """Compare a parsed transfer to the invoice requirements.

    Returns a list of human-readable problems.  An empty list means the
    transfer satisfies every check.
    """
    issues: list[str] = []

    # -- amount check --
    needed = invoice.get("amount", 0)
    if transfer.usdc_amount < needed:
        issues.append(
            f"Underpayment: received {transfer.usdc_amount} USDC "
            f"but invoice requires {needed} USDC"
        )

    # -- recipient / payee check --
    payee = invoice.get("payee")
    if payee and transfer.recipient.lower() != payee.lower():
        issues.append(
            f"Recipient mismatch: transfer sent to {transfer.recipient} "
            f"but invoice payee is {payee}"
        )

    # -- expiry check --
    deadline = invoice.get("expires_at")
    if deadline is not None and transfer.block_ts > deadline:
        issues.append(
            f"Expired: block timestamp {transfer.block_ts} is after "
            f"invoice deadline {deadline}"
        )

    return issues
