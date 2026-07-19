# Funding Provenance — Puzzle TX

Last updated: 2026-07-19  
Scope: on-chain chronology only. **No inference that timestamps are seeds.**

## Puzzle transaction (verified)

| Field | Value | Source |
|-------|--------|--------|
| TXID | `08389f34c98c606322740c0be6a7125d9860bb8d5cb182c02f98461e5fa6cd15` | mempool.space API |
| Block | `339085` | same |
| Block time (Unix) | `1421345234` | same |
| UTC | 2015-01-15 18:07:14 UTC | derived from block_time |
| Version / locktime | 1 / 0 | same |
| vin count | 1 | same |
| vout count | 256 | same |
| Fee | 400000 sat (0.004 BTC) | same |
| Explorer | https://mempool.space/tx/08389f34c98c606322740c0be6a7125d9860bb8d5cb182c02f98461e5fa6cd15 | |

## Funding outpoint (vin[0])

| Field | Value | Source |
|-------|--------|--------|
| Funding TXID | `9b11b90a212c27c982013bafe1d4a0730e01357245f0d074051a988e4bba1662` | puzzle TX vin[0].txid |
| Funding vout | `4` | puzzle TX vin[0].vout |
| Funding value | `3290000000` sat = **32.9 BTC** | prevout.value |
| Funding address | `1Czoy8xtddvcGrEhUUCZDQ9QqdRfKh697F` | prevout.scriptpubkey_address |
| Explorer (funding TX) | https://mempool.space/tx/9b11b90a212c27c982013bafe1d4a0730e01357245f0d074051a988e4bba1662 | |
| Explorer (funding address) | https://mempool.space/address/1Czoy8xtddvcGrEhUUCZDQ9QqdRfKh697F | |

## Funding transaction details

| Field | Value | Source |
|-------|--------|--------|
| Block | `339045` | funding TX status |
| Block time (Unix) | `1421321664` | same |
| UTC | **2015-01-15 11:34:24 UTC** | mempool.space HTML summary |
| Fee | 1000 sat | same |
| vin | 1 × from `173ujrhEVGqaZvPHXLqwXiSmPVMo225cqT` (181.8799 BTC) | same |
| vouts (summary) | see table below | same |

### Funding TX outputs

| vout | Address | Value (BTC) |
|------|---------|-------------|
| 0 | `1Aru8MzMVyWHxdCXN1p7e66jLKHCFUu3ZM` | 1.5 |
| 1 | `19gpJ5ry1EDppuvP9Hi43x4EX89stj8U77` | 2.0 |
| 2 | `3NTKgoHrYuktTXczxYfhLifTzfuNKcEc9B` (P2SH) | 100.0 |
| 3 | `173ujrhEVGqaZvPHXLqwXiSmPVMo225cqT` (change) | 45.47989 |
| 4 | `1Czoy8xtddvcGrEhUUCZDQ9QqdRfKh697F` (**puzzle fund**) | **32.9** |

## Chronology delta (verified)

| Metric | Value |
|--------|--------|
| Puzzle − Funding (seconds) | `1421345234 − 1421321664 = **23570**` (~**6.55 hours**) |
| Puzzle − Funding (blocks) | `339085 − 339045 = **40**` |

**Verified finding:** Funding UTXO was created the **same calendar day**, ~6.5 hours before the puzzle TX — not days/months earlier.

**Interpretation bound:** This only bounds when the *funding coin* existed. It does **not** prove when private keys were generated (could be earlier offline).

## Puzzle TX spend of funding UTXO — scriptsig fingerprint

When the puzzle TX spends `1Czoy8…`:

| Field | Value | Source |
|-------|--------|--------|
| scriptsig | DER signature + **OP_PUSHBYTES_33** pubkey | puzzle TX vin[0].scriptsig_asm |
| Pubkey length | **33 bytes** (compressed) | parsed from asm |
| Pubkey prefix | `02` | `024b0faa9624763002e963816b2f6774df0dedd770896a9511cb5c9d90f674ecda` |

**Verified:** The key controlling the funding address was spent with a **compressed** public key in January 2015.

## Prior hop (one step back)

Funding TX itself spends from:

| Field | Value |
|-------|--------|
| Address | `173ujrhEVGqaZvPHXLqwXiSmPVMo225cqT` |
| Spend pubkey in funding TX | **33-byte compressed**, prefix `03` (`031c24239a829a89d7…5050`) |
| Explorer | https://mempool.space/address/173ujrhEVGqaZvPHXLqwXiSmPVMo225cqT |

Address history (mempool API, sample): many later txs; early 2015 puzzle-related activity coexists with later reuse. **No claim** of exchange/mining cluster attribution in this document (not independently clustered here).

## Funding address later activity (not creator attribution)

`1Czoy8…` later appears in additional txs (mempool list includes blocks far after 339085). Those are **not** labeled as creator actions without separate proof.

## Speculative (labeled)

- Whether `173ujrh…` / `1Czoy8…` belong to an exchange batch, mixer, or personal wallet: **unverified** in this pass.
- Whether keys were generated in the ~6.5h window vs earlier: **unknown**.

## Implication for prior cascade timestamp tests

TX±6h and funding±~few hours overlap the same calendar day. That **does not** upgrade timestamp-seed hypotheses; it only shows funds were staged same-day. Prior `ts4be` tests remain **dar modelde negatif** (see `NEGATIVE_RESULTS.md`).

## Status

**Funding provenance: verified for one hop.**  
Next optional research: deeper history of `173ujrh…` first-seen time and any forum mentions of these two addresses — archive task, not cascade expansion.
