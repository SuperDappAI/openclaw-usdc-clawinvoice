#!/usr/bin/env bash
# ============================================================================
# ClawInvoice Demo Script
#
# Exercises the full invoice lifecycle: create → verify → deliver.
#
# Usage:
#   bash scripts/demo.sh [TX_HASH]
#
# If TX_HASH is provided, the script will attempt real on-chain verification.
# Without it, the verify step will demonstrate the expected error output.
# ============================================================================

set -euo pipefail

SEPARATOR="============================================================"

echo "$SEPARATOR"
echo "ClawInvoice Demo – Base Sepolia USDC Invoice Lifecycle"
echo "$SEPARATOR"
echo ""

# ------------------------------------------------------------------
# Step 1: Create an invoice
# ------------------------------------------------------------------
echo ">>> Step 1: Creating invoice (5 USDC, 1-hour expiry)..."
echo ""

CREATE_OUTPUT=$(clawinvoice create \
  --amount 5.0 \
  --memo "demo walkthrough" \
  --expiry 3600)

echo "$CREATE_OUTPUT"
echo ""

# Extract invoice_id from the JSON output
INVOICE_ID=$(echo "$CREATE_OUTPUT" | python3 -c "import sys,json; print(json.load(sys.stdin)['invoice_id'])")
echo "Captured invoice_id: $INVOICE_ID"
echo ""

# ------------------------------------------------------------------
# Step 2: Check status
# ------------------------------------------------------------------
echo "$SEPARATOR"
echo ">>> Step 2: Querying invoice status..."
echo ""

clawinvoice status --invoice-id "$INVOICE_ID"
echo ""

# ------------------------------------------------------------------
# Step 3: Verify payment
# ------------------------------------------------------------------
echo "$SEPARATOR"
echo ">>> Step 3: Verifying payment..."
echo ""

TX_HASH="${1:-}"

if [ -z "$TX_HASH" ]; then
  echo "(No TX_HASH argument supplied — using a placeholder to show error handling)"
  echo ""
  # Demonstrate the error path with a fake hash
  FAKE_TX="0x0000000000000000000000000000000000000000000000000000000000000000"
  clawinvoice verify --invoice-id "$INVOICE_ID" --tx "$FAKE_TX" || true
  echo ""
  echo "To run with a real transaction, re-run:"
  echo "  bash scripts/demo.sh <TX_HASH>"
else
  echo "Verifying with tx: $TX_HASH"
  echo ""
  clawinvoice verify --invoice-id "$INVOICE_ID" --tx "$TX_HASH"
fi
echo ""

# ------------------------------------------------------------------
# Step 4: Record delivery
# ------------------------------------------------------------------
echo "$SEPARATOR"
echo ">>> Step 4: Recording delivery..."
echo ""

clawinvoice deliver \
  --invoice-id "$INVOICE_ID" \
  --proof-url "https://example.com/demo-proof"
echo ""

# ------------------------------------------------------------------
# Summary
# ------------------------------------------------------------------
echo "$SEPARATOR"
echo ">>> Final invoice state:"
echo ""
clawinvoice status --invoice-id "$INVOICE_ID"
echo ""

echo "$SEPARATOR"
echo "Demo complete.  See docs/demo.md for the evidence checklist."
echo "$SEPARATOR"
