# ClawInvoice Skill – README

## What is this?

This directory contains the **OpenClaw skill package** for ClawInvoice.
An OpenClaw skill is a self-contained bundle of documentation that tells
an AI agent *how* to use a tool, *what* environment it needs, and *when*
to use each command.

## File Index

| File           | Purpose                                          |
|----------------|--------------------------------------------------|
| `SKILL.md`     | Primary skill definition — capabilities, env vars, quick reference |
| `README.md`    | This file — orientation for humans and agents    |
| `examples.md`  | Copy/paste-ready command sequences and prompts   |

## How an Agent Should Use This Skill

1. **Read `SKILL.md`** to learn what commands are available and which
   environment variables must be set.
2. **Copy examples from `examples.md`** to compose a workflow that
   creates an invoice, waits for payment, verifies the transaction, and
   records delivery.
3. **Parse JSON output** from every command to decide the next step.

## Safety Guidelines

- **Testnet only** — all defaults point to Base Sepolia (chain 84532).
- **No mainnet keys** — the tool never needs a private key; verification
  is read-only.
- **No secrets in output** — the CLI never prints private keys or seed
  phrases.
- **Auditable ledger** — every state transition is appended to the JSONL
  file so it can be reviewed later.

## Prerequisites

- Python ≥ 3.11
- `pip install -e .` from the repo root
- A Base Sepolia RPC endpoint (the public default works for light usage)
