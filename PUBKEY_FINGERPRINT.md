# Public-Key Fingerprint — Puzzle Addresses & Spends

Last updated: 2026-07-20

## Critical methodological note (must keep)

A **P2PKH address alone does not reveal** whether the creator used compressed or uncompressed serialization at spend time. The address is `HASH160(pubkey)`.  

However, once the **private key is known** (solved puzzles), both serializations can be tested: only one HASH160 matches the on-chain puzzle output. That tells you which serialization the **masked puzzle address** was generated from, independent of later spenders’ WIF choices.

**Source wallet vs masked output (2026-07-20 correction):**  
Creator pipeline is `K[i] → mask → P[i] → A[i]`. Compression evidence binds **`P[i] → A[i]` only**. It does **not** prove that the source deterministic wallet’s native addresses were compressed. See `SOURCE_SEQUENCE_REASSESSMENT.md`.

Later **spending** transactions reveal a pubkey in scriptSig/witness; that pubkey reflects whoever spent (solver, thief bot, or creator) and **may differ in tooling** from address creation.

---

## A. Address-generation fingerprint (solved keys × puzzle TX outputs)

### Method

1. Load `solved_keys.json` (82 keys).  
2. For puzzle `n`, take vout `n-1` address from TX `08389f34…cd15` (mempool.space API dump).  
3. Derive compressed (33B) and uncompressed (65B) addresses via coincurve + HASH160 + Base58Check.  
4. Compare to on-chain output address.

### Result (verified 2026-07-19)

| Metric | Count |
|--------|-------|
| Solved keys in range 1–256 tested | 82 |
| Match **compressed** HASH160 | **82 / 82** |
| Match **uncompressed** HASH160 | **0 / 82** |

Sample:

| Puzzle | On-chain address | Compressed match | Uncompressed match |
|--------|------------------|------------------|--------------------|
| 1 | `1BgGZ9tcN4rm9KBzDn7KprQz87SZ26SAMH` | yes | no (`1EHNa6Q4Jz2uvNExL497mE43ikXhwF6kZm`) |
| 2 | `1CUNEBjYrCn2y1SdiUMohaKUi4wpP326Lb` | yes | no |
| 5 | `1E6NuFjCi27W5zoXg8TRdcSRq84zJeBW3k` | yes | no |
| 66 | `13zb1hQbWVsc2S7ZTZnP2G4undNNpdh5so` | yes | no |
| 70 | `19YZECXj3SxEZMoUeJ1yiPsw8xANe7M7QR` | yes | no |

**Verified finding:** For all currently solved puzzle outputs checked, addresses were generated from **compressed** public keys.

### Implication for wallet families (bounded)

| Role | Family | Fit |
|------|--------|-----|
| Tool that emitted **final** Puzzle addresses without remasking | Stock Electrum 1.x / classic Armory (uncompressed defaults) | **Poor** for stock export of `A[i]` |
| Source sequence **`K[i]`** feeding unknown `T` + separate compressed rebuild | Electrum v1 / Armory / Casascius BAU / Type-1 | **Not eliminated** by 82/82; **no positive evidence** from compression alone |
| Final address build after mask | Any script choosing compressed HASH160 | **Required** by fingerprint |

**Does not prove** BIP32 or any named wallet.  
**Does weaken** “stock Electrum/Armory UI alone exported Puzzle addresses.”  
**Does not eliminate** those wallets as **`K[i]` generators**.

---

## B. Creator-controlled spends (separate class)

### B1. Puzzle funding spend (2015-01-15)

TX `08389f34…` vin[0] spending `1Czoy8…`:

| Field | Value |
|-------|--------|
| Pubkey length | 33 (compressed) |
| Prefix | `02` |
| Class | **Creator-associated** (funds the puzzle) |

### B2. 2017 redistribution (creator-attributed by community + prior announcement)

| Field | Value | Source |
|-------|--------|--------|
| TXID | `5d45587cfd1d5b0fb826805541da7d94c61fe432259e68ee26f4a04544384164` | Bitcointalk reports 2017-07-11; mempool API |
| Block | `475240` | mempool API |
| Block time | `1499749253` (~2017-07-11) | mempool API |
| vin / vout | 97 / 109 | mempool API |
| Explorer | https://mempool.space/tx/5d45587cfd1d5b0fb826805541da7d94c61fe432259e68ee26f4a04544384164 | |

Pubkey classification of **all 97 inputs** (parsed from scriptsig_asm):

| Type | Count |
|------|-------|
| Compressed (33B, `02`/`03`) | **96** |
| Uncompressed (65B, `04`) | **1** |
| Other / missing | 0 |

Samples: vin0 `03…` (33), vin1 `03…` (33), vin2 `02…` (33); vin96 `04…` (65).

**Verified:** Creator’s 2017 multi-input spend is **overwhelmingly compressed**, with **one** uncompressed input.  

**Speculative:** The single uncompressed input may be a different import path or legacy key handling — not interpreted further here.

---

## C. Community solver spends (separate class)

Solver/bot spends reveal pubkeys chosen by **spender tooling**, not necessarily creator address-generation settings.

Examples (secondary sources; not exhaustively re-parsed in this pass):

| Puzzle | Notes | Source class |
|--------|--------|--------------|
| #66 | Public mempool spend; interception discussed | StackExchange / news (community) |
| #69 | Multiple replace-by-fee / theft reports | privatekeys.pw timeline |

**Status:** Full systematic table of every solved puzzle’s **first successful spend** TXID + pubkey length is **not complete** in this document. Priority sample for a follow-up pass: puzzles 1–20 early 2015 spends (likely still compressed if standard WIF compressed used).

**Do not conflate** solver spend compression with creator address generation — section A already settles generation for solved keys.

---

## D. 2019 “every 5th” micro-spends (creator-attributed in trackers)

Trackers report 2019-05-31 1000-sat spends from #65,#70,#75…#160 exposing pubkeys for kangaroo.  

| Item | Status in this dossier |
|------|------------------------|
| Exact TXID list | **Not independently enumerated here** — mark **Test edilmedi / incomplete** |
| Pubkey lengths on those spends | Expected compressed if consistent with B1/B2; **verify in follow-up** |

---

## Summary table (high confidence)

| Evidence class | Compression signal | Confidence |
|----------------|-------------------|------------|
| Solved address HASH160 vs key | **All compressed** (82/82) | High (recomputed) |
| Funding address spend 2015 | Compressed | High (chain) |
| Redistribution 2017 inputs | 96 compressed / 1 uncompressed | High (chain parse) |
| Solver spends | Mixed tooling; not creator fingerprint | Medium / separate |

## Status

**Highest-value item:** compressed-only for known solved **masked** puzzle outputs (`P→A`).  
**Do not** use section A to close Electrum/Armory as source sequences — `SOURCE_SEQUENCE_REASSESSMENT.md`.
