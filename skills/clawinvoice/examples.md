# ClawInvoice – Command Examples & Agent Prompts

Below are ready-to-use command sequences.  Each block shows the CLI
invocation followed by the expected JSON shape.

---

## 1. Create an Invoice

```bash
clawinvoice create \
  --amount 25.0 \
  --memo "security audit for contract 0xABC" \
  --payee 0xB2b2B2b2B2b2B2B2b2b2b2B2B2b2b2b2B2b2B2b2 \
  --expiry 7200
```

**Expected output:**

```json
{
  "invoice_id": "a1b2c3d4e5f6...",
  "amount": 25.0,
  "memo": "security audit for contract 0xABC",
  "payee": "0xB2b2B2b2B2b2B2B2b2b2b2B2B2b2b2b2B2b2B2b2",
  "status": "pending",
  "created_at": 1700000000,
  "expires_at": 1700007200,
  "tx": null,
  "proof_url": null
}
```

---

## 2. Check Invoice Status

```bash
clawinvoice status --invoice-id a1b2c3d4e5f6
```

**Expected output:**

```json
{
  "invoice_id": "a1b2c3d4e5f6...",
  "status": "pending",
  "amount": 25.0
}
```

> If the invoice does not exist, the CLI returns exit code 1 and an
> error JSON: `{"error": "invoice not found", "invoice_id": "..."}`.

---

## 3. Verify Payment On-Chain

After the payer sends USDC on Base Sepolia, grab the transaction hash
and run:

```bash
clawinvoice verify \
  --invoice-id a1b2c3d4e5f6 \
  --tx 0xff00ff00...
```

**Expected output (success):**

```json
{
  "invoice_id": "a1b2c3d4e5f6...",
  "status": "paid",
  "tx_hash": "0xff00ff00...",
  "paid_at": 1700001234,
  "amount": 25.0,
  "recipient": "0xB2b2B2b2B2b2B2B2b2b2b2B2B2b2b2b2B2b2B2b2"
}
```

**Possible errors:**

- `"no USDC Transfer event"` – tx does not contain a Transfer from the
  expected USDC contract.
- `"Underpayment"` – transferred amount is less than the invoice amount.
- `"Recipient mismatch"` – USDC was sent to a different address.
- `"Expired"` – the block timestamp exceeds the invoice deadline.
- `"Payment predates invoice"` – tx happened before the invoice was created.

---

## 4. Record Delivery

```bash
clawinvoice deliver \
  --invoice-id a1b2c3d4e5f6 \
  --proof-url "https://example.com/report.pdf"
```

**Expected output:**

```json
{
  "invoice_id": "a1b2c3d4e5f6...",
  "status": "delivered",
  "proof_url": "https://example.com/report.pdf"
}
```

---

## Agent Prompt Templates

### Prompt: Full Invoice Lifecycle

```
You have access to the `clawinvoice` CLI.  Follow these steps:

1. Create an invoice:
   clawinvoice create --amount <AMOUNT> --memo "<DESCRIPTION>" --payee <WALLET> --expiry 3600

2. Share the invoice_id and payee address with the payer.

3. Once payment is made, verify it:
   clawinvoice verify --invoice-id <ID> --tx <TX_HASH>

4. After delivering the work, record proof:
   clawinvoice deliver --invoice-id <ID> --proof-url <URL>

Parse the JSON output of each command to decide the next action.
All amounts are in USDC on Base Sepolia (chain 84532).
```

### Prompt: Payment Verification Only

```
Given an invoice ID and a transaction hash, verify the USDC payment:

   clawinvoice verify --invoice-id <ID> --tx <TX_HASH>

If the output JSON has "status": "paid", the payment is confirmed.
Otherwise, inspect the "problems" array for what went wrong.
```
