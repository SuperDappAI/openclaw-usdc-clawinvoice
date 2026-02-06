# ClawInvoice

Minimal agentic commerce primitive for the OpenClaw USDC Hackathon on Moltbook.

## Architecture

```
┌────────────┐      ┌──────────────┐      ┌─────────────┐
│  Agent /    │─CLI─▶│  ClawInvoice │─R/W─▶│  JSONL      │
│  Human     │◀─JSON─│  (typer)     │      │  Ledger     │
└────────────┘      └──────┬───────┘      └─────────────┘
                           │
                     web3.py (future)
                           │
                    ┌──────▼───────┐
                    │  Base Sepolia│
                    │  USDC        │
                    └──────────────┘
```

## Quickstart

```bash
# 1. Clone & install
git clone <repo-url> && cd openclaw-usdc-clawinvoice
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# 2. Configure
cp .env.example .env   # edit values if needed

# 3. Use the CLI
clawinvoice create --amount 12.5 --memo "agent audit" --expiry 3600
clawinvoice status --invoice-id <id>
clawinvoice verify --invoice-id <id> --tx <hash>
clawinvoice deliver --invoice-id <id> --proof-url <url>
```

Every command prints JSON to stdout for easy agent consumption.

## CLI Commands

| Command   | Description                            |
|-----------|----------------------------------------|
| `create`  | Create a new USDC invoice              |
| `verify`  | Mark invoice as verified with tx hash  |
| `status`  | Query current invoice status           |
| `deliver` | Mark invoice as delivered with proof   |

## Development

```bash
# Run tests
pytest

# Show CLI help
clawinvoice --help
```

## Configuration

Copy `.env.example` to `.env`. Available variables:

| Variable        | Default                                      |
|-----------------|----------------------------------------------|
| `RPC_URL`       | `https://sepolia.base.org`                   |
| `USDC_CONTRACT` | `0x036CbD53842c5426634e7929541eC2318f3dCF7e` |
| `CHAIN_ID`      | `84532`                                      |

## Hackathon
- Track: Agentic Commerce
- Submission: m/usdc (Moltbook)

## Next
See repo issues for implementation tasks.
