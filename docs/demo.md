# ClawInvoice Demo – End-to-End Walkthrough

This guide walks through the complete invoice lifecycle on **Base Sepolia**:
create → pay → verify → deliver.

## Why this demo matters

This flow proves **agent‑native commerce** end‑to‑end:

- An invoice is created with clear terms.
- A USDC transfer is verified onchain.
- A deliverable is attached as proof.

The demo evidence (tx hash + proof link + JSON output) is the core artifact
for the hackathon submission.

---

## Prerequisites

| Requirement        | Details                                            |
|--------------------|----------------------------------------------------|
| Python             | ≥ 3.11                                             |
| Install            | `pip install -e .` from the repo root              |
| RPC endpoint       | Default `https://sepolia.base.org` works           |
| Testnet USDC       | See "Getting Testnet USDC" below                   |

### Getting Testnet USDC

1. Visit the **Base Sepolia faucet** at <https://faucet.circle.com/> and
   request USDC for your wallet on Base Sepolia.
2. Alternatively, bridge Sepolia ETH via the Base bridge and swap for
   USDC on a Sepolia DEX.
3. Confirm your balance in a block explorer:
   `https://sepolia.basescan.org/address/<YOUR_WALLET>`

---

## Step-by-Step Demo

### 1. Configure Environment

```bash
cp .env.example .env
# Edit .env if you need a custom RPC or ledger path
```

### 2. Create an Invoice

```bash
clawinvoice create \
  --amount 5.0 \
  --memo "demo task" \
  --payee 0xYOUR_PAYEE_WALLET \
  --expiry 3600
```

Save the `invoice_id` from the JSON output — you will need it in later steps.

### 3. Send USDC On-Chain

Using your wallet (MetaMask, cast, etc.), send **at least 5 USDC** on
Base Sepolia to the payee address above.

Copy the **transaction hash** once the transfer confirms.

### 4. Verify the Payment

```bash
clawinvoice verify \
  --invoice-id <INVOICE_ID> \
  --tx <TX_HASH>
```

If successful, the output will show `"status": "paid"`.

### 5. Record Delivery

```bash
clawinvoice deliver \
  --invoice-id <INVOICE_ID> \
  --proof-url "https://example.com/my-deliverable"
```

---

## Evidence Checklist

Use this checklist to prepare a submission bundle:

- [ ] **Invoice creation output** — JSON from `clawinvoice create`
- [ ] **Transaction hash** — the on-chain tx hash for the USDC transfer
- [ ] **Block explorer screenshot** — screenshot of the tx on
      `sepolia.basescan.org` showing the Transfer event
- [ ] **Verification output** — JSON from `clawinvoice verify`
- [ ] **Delivery output** — JSON from `clawinvoice deliver`
- [ ] **Ledger snapshot** — copy of `data/ledger.jsonl` showing all
      state transitions

### How to Produce the Evidence Bundle

```bash
# 1. Run the demo script (captures JSON at each step)
bash scripts/demo.sh 2>&1 | tee evidence/demo_output.txt

# 2. Take a screenshot of the tx on sepolia.basescan.org

# 3. Copy the ledger
cp data/ledger.jsonl evidence/ledger_snapshot.jsonl

# 4. Archive everything
tar czf evidence_bundle.tar.gz evidence/
```

---

## Automated Demo Script

A helper script is available at `scripts/demo.sh`.  It exercises the
full create → verify → deliver flow with placeholder values.

```bash
bash scripts/demo.sh
```

> **Note:** The verify step requires a real on-chain transaction hash.
> When running locally without one, the script will show the expected
> error output.

---

## Troubleshooting

| Symptom                        | Fix                                          |
|--------------------------------|----------------------------------------------|
| `Unable to reach RPC`          | Check `WEB3_RPC_URL` in `.env`               |
| `invoice not found`            | Confirm the `invoice_id` matches a created invoice |
| `no USDC Transfer event`       | Ensure the tx is a USDC transfer on Base Sepolia |
| `Underpayment`                 | Send at least the invoice `amount` in USDC   |
| `Expired`                      | Recreate the invoice with a longer `--expiry` |
