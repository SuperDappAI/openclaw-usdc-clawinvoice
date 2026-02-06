# ClawInvoice – OpenClaw Skill

## Overview

ClawInvoice is a lightweight CLI tool that lets any AI agent (or human)
create, verify, and close USDC invoices on **Base Sepolia**.

It is designed for the *agentic commerce* track of the OpenClaw hackathon,
where autonomous agents need a simple, auditable payment primitive.

## Capabilities

| Action     | What it does                                      |
|------------|---------------------------------------------------|
| **create** | Mint a new USDC invoice stored in a JSONL ledger  |
| **verify** | Confirm an on-chain USDC transfer matches the invoice |
| **status** | Query the current state of any invoice            |
| **deliver**| Attach a proof-of-delivery URL and close the loop |

## Environment Variables

Set these **before** invoking any command:

| Variable         | Required | Default                                        | Purpose                          |
|------------------|----------|------------------------------------------------|----------------------------------|
| `WEB3_RPC_URL`   | No       | `https://sepolia.base.org`                     | JSON-RPC endpoint for Base Sepolia |
| `RPC_URL`        | No       | `https://sepolia.base.org`                     | Fallback if `WEB3_RPC_URL` unset |
| `CHAIN_ID`       | No       | `84532`                                        | EVM chain identifier             |
| `USDC_CONTRACT`  | No       | `0x036CbD53842c5426634e7929541eC2318f3dCF7e`   | USDC token on Base Sepolia       |
| `LEDGER_PATH`    | No       | `data/ledger.jsonl`                            | Path to the invoice ledger file  |

> **Safety:** Never expose mainnet private keys.  This skill is designed
> exclusively for **Base Sepolia testnet** usage.

## Installation

```bash
pip install -e .
```

## Quick Reference

```bash
# Create an invoice (10 USDC, 1-hour expiry)
clawinvoice create --amount 10 --memo "audit task" --payee 0xYOUR_WALLET

# Check invoice status
clawinvoice status --invoice-id <INVOICE_ID>

# Verify payment on-chain
clawinvoice verify --invoice-id <INVOICE_ID> --tx <TX_HASH>

# Mark delivery
clawinvoice deliver --invoice-id <INVOICE_ID> --proof-url https://example.com/proof
```

Every command emits **structured JSON** to stdout.

## Integration Notes

- All output is JSON — pipe it to `jq` or parse it programmatically.
- The JSONL ledger is append-only; the latest record for a given
  `invoice_id` is always the authoritative state.
- No private keys are required — verification is read-only against the RPC.
