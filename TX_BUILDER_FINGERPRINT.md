# TX Builder Fingerprint — Funding + Puzzle

Last updated: 2026-07-20  
Scope: **which software family may have built the transactions** — not which tool generated keys.  
**No claim** that a single signature identifies a wallet or nonce RNG.

Raw hex (local): `_research_bau/puzzle.hex`, `_research_bau/funding.hex`  
API JSON: `_research_bau/puzzle.json`, `_research_bau/funding.json`  
Explorers: [puzzle](https://mempool.space/tx/08389f34c98c606322740c0be6a7125d9860bb8d5cb182c02f98461e5fa6cd15) · [funding](https://mempool.space/tx/9b11b90a212c27c982013bafe1d4a0730e01357245f0d074051a988e4bba1662)

---

## Legend

| Tag | Meaning |
|-----|---------|
| **Verified** | Parsed from raw hex / mempool API |
| **Inferred** | Reasonable reading of verified fields |
| **Speculative** | Hypothesis only |

---

## A. Puzzle TX — `08389f34…cd15`

| Field | Value | Tag |
|-------|--------|-----|
| TXID | `08389f34c98c606322740c0be6a7125d9860bb8d5cb182c02f98461e5fa6cd15` | Verified |
| Block / time | `339085` / `1421345234` (2015-01-15 18:07:14 UTC) | Verified |
| version | **1** | Verified |
| locktime | **0** | Verified |
| vin count | 1 | Verified |
| vout count | **256** | Verified |
| size / weight | **8864** bytes / 35456 | Verified |
| fee | **400000** sat (0.004 BTC) | Verified |
| fee rate | ≈ **45.13 sat/byte** (fee/size) | Verified |
| input sequence | **0xffffffff** (final) | Verified |
| prevout | funding `9b11b90a…1662` **vout 4** | Verified |

### A1. scriptSig (vin[0]) — Verified

| Item | Value |
|------|--------|
| Push layout | `OP_PUSHBYTES_72` (sig) + `OP_PUSHBYTES_33` (pubkey) |
| scriptSig length | 107 bytes |
| Signature total (DER+sighash) | 72 bytes |
| DER length | 71 |
| sighash | **0x01** (`SIGHASH_ALL`) |
| r length / s length | 33 / 32 (high-R with leading `0x00`) |
| **low-S** | **True** |
| Pubkey | 33 bytes, prefix `02`, compressed |
| Pubkey hex | `024b0faa9624763002e963816b2f6774df0dedd770896a9511cb5c9d90f674ecda` |

### A2. Outputs — Verified

| Property | Value |
|----------|--------|
| All types | **P2PKH** (256/256) |
| Order | **Index order**: vout `i` = puzzle `#i+1` |
| Value rule | `value(i) = (i+1) * 100000` sat (= 0.001…0.256 BTC) |
| Sum | `3289600000` sat (= 32.896 BTC) |
| First / last | `1BgGZ9…` @ 100000 · `1FMcot…` @ 25600000 |

**Inferred:** Output list was built by a loop over puzzle indices 1…256 (or 0…255 with `i+1`), not shuffled change/payment heuristics.

---

## B. Funding TX — `9b11b90a…1662`

| Field | Value | Tag |
|-------|--------|-----|
| TXID | `9b11b90a212c27c982013bafe1d4a0730e01357245f0d074051a988e4bba1662` | Verified |
| Block / time | `339045` / `1421321664` (2015-01-15 11:34:24 UTC) | Verified |
| version | **1** | Verified |
| locktime | **0** | Verified |
| vin / vout | 1 / **5** | Verified |
| size | **325** bytes | Verified |
| fee | **1000** sat | Verified |
| fee rate | ≈ **3.08 sat/byte** | Verified |
| input sequence | **0xffffffff** | Verified |
| input from | `173ujrhEVGqaZvPHXLqwXiSmPVMo225cqT` | Verified |

### B1. scriptSig (vin[0]) — Verified

| Item | Value |
|------|--------|
| Push layout | `OP_PUSHBYTES_71` (sig) + `OP_PUSHBYTES_33` (pubkey) |
| scriptSig length | 106 bytes |
| Signature total | 71 bytes |
| DER length | 70 |
| sighash | **0x01** (`SIGHASH_ALL`) |
| r / s lengths | 32 / 32 |
| **low-S** | **True** |
| Pubkey | 33 bytes, prefix `03`, compressed |
| Pubkey hex | `031c24239a829a89d7…64665050` |

### B2. Output ordering — Verified

| vout | Type | Value (sat) | Address |
|------|------|-------------|---------|
| 0 | P2PKH | 150000000 | `1Aru8Mz…` |
| 1 | P2PKH | 200000000 | `19gpJ5r…` |
| 2 | **P2SH** | 10000000000 | `3NTKgo…` |
| 3 | P2PKH | 4547989000 | `173ujrh…` (**change to same as input**) |
| 4 | P2PKH | **3290000000** | `1Czoy8…` (**puzzle fund**, spent later) |

**Inferred:** Change is **not last**. Puzzle fund is last. Mixed P2PKH + one large P2SH. Consistent with **manual / raw-TX construction** or a wallet that does not force change-last; **not** proof of any named wallet.

---

## C. Shared builder traits (funding vs puzzle)

| Trait | Funding | Puzzle | Same? |
|-------|---------|--------|-------|
| version | 1 | 1 | Yes |
| locktime | 0 | 0 | Yes |
| sequence | `0xffffffff` | `0xffffffff` | Yes |
| sighash | ALL (1) | ALL (1) | Yes |
| low-S | Yes | Yes | Yes |
| compressed spend pubkey | Yes | Yes | Yes |
| fee rate | ~3 sat/B | ~45 sat/B | **No** |
| output count / structure | 5 mixed | 256 arithmetic P2PKH | **No** |
| DER size class | 71-byte sig | 72-byte sig | Different R encoding |

**Verified:** Shared traits are the **2015-era common P2PKH template** (v1, locktime 0, final seq, SIGHASH_ALL, compressed, low-S).  
**Not verified:** Same binary / same RPC client / same fee policy.

**Inferred:** Fee-rate gap (~3 vs ~45) and the puzzle’s **exact 0.004 BTC** absolute fee (32.9 − 32.896) look more like **manual absolute remainder / fixed fee** than a dynamic sat/byte estimator. Core **0.10.0** (new fee estimation + libsecp256k1) released **2015-02-16**, ~1 month **after** the puzzle — so “Core 0.10 fee estimator did this” is **historically weak**. Funding’s **1000 sat** absolute fee vs puzzle’s **400000 sat** supports separate manual constructions or different fee knobs — still **inference only**.

**Speculative:** Same operator; Core **0.9.x** / raw-RPC / bitcoinj / custom script for publishing after offline key prep. Puzzle layout **strongly suggests** scripted or raw multi-output construction (manual entry of 256 outs is theoretically possible but operationally implausible).

---

## D. What this weakens / does not weaken

| Software role | Reading |
|---------------|---------|
| Casascius BAU as **TX builder** | **Weakened to near-impossible** — BAU has no send/broadcast/raw-tx path (see `CASASCIUS_BAU_ARCHAEOLOGY.md`). Export → `importprivkey` text only. |
| Stock UI “send to one address” alone for **puzzle TX** | **Weak** — 256 ordered arithmetic outputs **strongly suggest** a scripted/raw multi-output builder; pure manual construction is theoretically possible but operationally implausible. |
| Bitcoin Core **0.9.x / 0.10 pre-release / raw-RPC-compatible** as **signer** | **Compatible** (low-S since Core 0.9, Mar 2014). Released **0.10.0** is **post-puzzle** (2015-02-16) — weak as the normal release signer. Not identified. |
| Electrum / bitcoinj / custom C#/Python | **Compatible** with observed traits; not identified. |
| Pre-0.9 Core-only high-S habit | **Weakened** for these two spends (both low-S), but low-S was already common by Jan 2015 across several stacks. |
| Core 0.10 fee estimator as puzzle fee source | **Historically weak** (estimator shipped in 0.10.0 after puzzle date); 0.004 BTC looks like absolute leftover (**inferred**). |

**Single-signature nonce / wallet ID:** **Not claimed. Not possible from this dossier.**

---

## E. Cross-links

- `CASASCIUS_BAU_ARCHAEOLOGY.md` — BAU cannot build these TXs  
- `WALLET_BUILDER_COMPARISON.md` — family table  
- `HISTORICAL_BUILDER_REPRODUCTION.md` — synthetic era lab  
- `FUNDING_SIBLING_CLUSTER.md` — exact `9b11…:2` redeem **2-of-3**; WE Bitstamp attribution (bounded)  
- `FUNDING_PROVENANCE.md` — chronology  
- `TX_STRUCTURE_FINGERPRINT.md` — 256-output arithmetic uniqueness scan  
- `EVIDENCE_CANDIDATES.md` — passphrase candidates (separate track)  
