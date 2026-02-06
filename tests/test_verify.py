"""Tests for clawinvoice.verify – uses mocked web3 objects."""

from __future__ import annotations

import types
from unittest.mock import MagicMock, patch

import pytest

from clawinvoice.verify import (
    PaymentVerificationError,
    USDCTransferInfo,
    _address_from_topic,
    fetch_usdc_transfer,
    validate_against_invoice,
)


# ---------------------------------------------------------------------------
# Helpers to construct realistic mock objects
# ---------------------------------------------------------------------------

# keccak256("Transfer(address,address,uint256)") without the 0x prefix
_TRANSFER_TOPIC_RAW = (
    "ddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
)

_FAKE_SENDER = "0x" + "a1" * 20  # 0xA1a1...
_FAKE_RECIPIENT = "0x" + "b2" * 20  # 0xB2b2...
_FAKE_TX = "0x" + "ff" * 32

# 10 USDC = 10_000_000 raw units → 32-byte hex
_TEN_USDC_HEX = format(10_000_000, "064x")


class _HexBytes(bytes):
    """Tiny stand-in for hexbytes.HexBytes used in web3 log entries."""

    def hex(self) -> str:  # noqa: A003
        return super().hex()


def _make_topic(hex_str: str) -> _HexBytes:
    return _HexBytes(bytes.fromhex(hex_str.lstrip("0x")))


def _build_mock_receipt(
    *,
    usdc_addr: str = "0x036CbD53842c5426634e7929541eC2318f3dCF7e",
    sender_padded: str | None = None,
    recipient_padded: str | None = None,
    amount_hex: str = _TEN_USDC_HEX,
    include_transfer: bool = True,
):
    """Return a dict that looks like a web3 transaction receipt."""
    if sender_padded is None:
        sender_padded = "a1" * 20
    if recipient_padded is None:
        recipient_padded = "b2" * 20

    logs = []
    if include_transfer:
        logs.append({
            "address": usdc_addr,
            "topics": [
                _make_topic(_TRANSFER_TOPIC_RAW),
                _make_topic(sender_padded.zfill(64)),
                _make_topic(recipient_padded.zfill(64)),
            ],
            "data": _HexBytes(bytes.fromhex(amount_hex)),
        })

    return {
        "logs": logs,
        "blockNumber": 123456,
    }


# ---------------------------------------------------------------------------
# Unit tests – validate_against_invoice
# ---------------------------------------------------------------------------

class TestValidateAgainstInvoice:
    """Checks for validate_against_invoice without any web3 calls."""

    def _transfer(self, *, amount: float = 10.0, recipient: str = _FAKE_RECIPIENT, ts: int = 1000) -> USDCTransferInfo:
        return USDCTransferInfo(
            sender=_FAKE_SENDER,
            recipient=recipient,
            raw_units=int(amount * 1_000_000),
            usdc_amount=amount,
            block_ts=ts,
            tx_hash=_FAKE_TX,
        )

    def test_all_checks_pass(self) -> None:
        xfer = self._transfer(amount=15.0, ts=500)
        inv = {"amount": 10.0, "payee": _FAKE_RECIPIENT, "expires_at": 9999}
        assert validate_against_invoice(xfer, inv) == []

    def test_underpayment_detected(self) -> None:
        xfer = self._transfer(amount=5.0)
        inv = {"amount": 10.0}
        errs = validate_against_invoice(xfer, inv)
        assert len(errs) == 1
        assert "Underpayment" in errs[0]

    def test_wrong_recipient_detected(self) -> None:
        xfer = self._transfer(recipient="0x" + "cc" * 20)
        inv = {"amount": 1.0, "payee": "0x" + "dd" * 20}
        errs = validate_against_invoice(xfer, inv)
        assert any("mismatch" in e.lower() for e in errs)

    def test_expired_invoice_detected(self) -> None:
        xfer = self._transfer(ts=2000)
        inv = {"amount": 1.0, "expires_at": 1500}
        errs = validate_against_invoice(xfer, inv)
        assert any("Expired" in e for e in errs)

    def test_no_payee_skips_recipient_check(self) -> None:
        xfer = self._transfer()
        inv = {"amount": 1.0}
        assert validate_against_invoice(xfer, inv) == []

    def test_exact_amount_passes(self) -> None:
        xfer = self._transfer(amount=10.0)
        inv = {"amount": 10.0}
        assert validate_against_invoice(xfer, inv) == []


# ---------------------------------------------------------------------------
# Unit tests – fetch_usdc_transfer (mocked web3)
# ---------------------------------------------------------------------------

class TestFetchUSDCTransfer:
    """Verify log parsing with a mocked web3 provider."""

    def _patch_web3(self, receipt, block_ts: int = 1700000000):
        mock_w3 = MagicMock()
        mock_w3.is_connected.return_value = True
        mock_w3.eth.get_transaction_receipt.return_value = receipt
        mock_w3.eth.get_block.return_value = {"timestamp": block_ts}
        return mock_w3

    @patch("clawinvoice.verify._connect")
    def test_successful_extraction(self, mock_connect: MagicMock) -> None:
        receipt = _build_mock_receipt()
        mock_w3 = self._patch_web3(receipt, block_ts=1_700_000_000)
        mock_connect.return_value = mock_w3

        info = fetch_usdc_transfer(_FAKE_TX)

        assert info.usdc_amount == 10.0
        assert info.block_ts == 1_700_000_000
        assert info.tx_hash == _FAKE_TX
        # Recipient should be checksummed version of 0xb2b2...
        assert info.recipient.lower() == ("0x" + "b2" * 20).lower()

    @patch("clawinvoice.verify._connect")
    def test_no_transfer_event_raises(self, mock_connect: MagicMock) -> None:
        receipt = _build_mock_receipt(include_transfer=False)
        mock_w3 = self._patch_web3(receipt)
        mock_connect.return_value = mock_w3

        with pytest.raises(PaymentVerificationError, match="no USDC Transfer"):
            fetch_usdc_transfer(_FAKE_TX)

    @patch("clawinvoice.verify._connect")
    def test_wrong_contract_raises(self, mock_connect: MagicMock) -> None:
        receipt = _build_mock_receipt(usdc_addr="0x" + "00" * 20)
        mock_w3 = self._patch_web3(receipt)
        mock_connect.return_value = mock_w3

        # The default usdc_addr kwarg won't match 0x00...
        with pytest.raises(PaymentVerificationError, match="no USDC Transfer"):
            fetch_usdc_transfer(_FAKE_TX)

    @patch("clawinvoice.verify._connect")
    def test_receipt_fetch_failure(self, mock_connect: MagicMock) -> None:
        mock_w3 = MagicMock()
        mock_w3.is_connected.return_value = True
        mock_w3.eth.get_transaction_receipt.side_effect = RuntimeError("rpc down")
        mock_connect.return_value = mock_w3

        with pytest.raises(PaymentVerificationError, match="Could not retrieve"):
            fetch_usdc_transfer(_FAKE_TX)


# ---------------------------------------------------------------------------
# Unit tests – _address_from_topic helper
# ---------------------------------------------------------------------------

def test_address_from_topic_pads_correctly() -> None:
    """A 20-byte address left-padded in a 32-byte topic should be recovered."""
    addr_hex = "aabbccdd" * 5  # 20 bytes
    padded = bytes.fromhex("00" * 12 + addr_hex)
    result = _address_from_topic(padded)
    assert result.lower() == ("0x" + addr_hex).lower()
