# Generator Differential Audit — Casascius / Electrum 1.x / Armory

Last updated: 2026-07-20  
**Prerequisite:** all three exact vector locks **PASS**.

| Family | Lock artifact | Status |
|--------|---------------|--------|
| Casascius C1/C2 | `casascius_vector_selftest.py` | **LOCKED** |
| Electrum 1.x | `electrum_v1_vector_selftest.py` | **LOCKED** |
| Armory HD CKD (2012 gist) | `armory_chain_selftest.py` | **LOCKED** |

**Not a seed hunt.** Technical fit ≠ Puzzle link. Three locks do **not** open a scan.

---

## Side-by-side

| Criterion | Casascius BAU | Electrum 1.x | Armory CKD (gist) |
|-----------|---------------|--------------|-------------------|
| **Index start** | **1-based** (`i≥1`) | **0-based** | **0-based** tree |
| **Receiving / change** | None (flat index) | `for_change` 0/1 in seq string | `HDW_CHAIN_EXTERNAL=0` / `INTERNAL=1` |
| **256 consecutive keys natural?** | Yes — export loop over `i=1..N` | Yes — `n=0..255` on one chain | Yes — `M/0/0/0..255` (or any chain) |
| **Seed / root format** | UTF-8 passphrase string | 128-bit hex (ASCII) → 100k SHA256 stretch | 32B priv + 32B chain (extended key) |
| **Private scalar output** | `SHA256(…)` raw 32B (as key material) | `(master + seq) mod n` | `(IL × k) mod n` per CKD step |
| **Forward structure** | Independent per `i` (not chained from prior priv) | Independent per `(n, change)` from master | **Chained tree**: each child from parent `(k,c)` |
| **Pubkey in address path** | Uncompressed (BAU `KeyPair` default) | Uncompressed | Gist prints **compressed** pub |
| **Pre-2015 use** | Yes (2011+) | Yes (2011–2015 old wallets) | Yes (2012 CKD vector; Armory product earlier) |
| **“Consecutive keys from a deterministic wallet” fit** | Strong (flat consecutive export) | Strong (sequential receiving) | Strong (tree address indices) |
| **Puzzle primary link** | **None** | **None** | **None** |

---

## What separates them

1. **Casascius** — passphrase‖index (or C2 slash formula); **no** HD chaincode; index starts at **1**; each key is an independent hash, not a parent→child multiply.
2. **Electrum 1.x** — stretched master + additive seq from `SHA256d("%d:%d:"‖mpk)`; receiving/change in the string; uncompressed P2PKH.
3. **Armory CKD** — HMAC-SHA512 over **uncompressed** parent pub ‖ **BE** index; child = **multiply**; parallel public derivation; account/chain/address tree.

If a future Puzzle hypothesis needs a **parent→child multiplicative** chain with chaincode, Armory CKD is the only one of the three that matches that shape. If it needs **flat passphrase‖counter**, Casascius. If **master+seq**, Electrum.

All three can emit 256 forward keys. **None** is thereby implicated.

---

## Reference families (not locked as wallet generators)

| Family | Role |
|--------|------|
| Maxwell Type-1/2 | Design recipe; not a single shipped wallet |
| BIP32 | Official vectors; too wide; no Puzzle link |

---

## Net research state

| Item | State |
|------|--------|
| Electrum | Locked |
| Casascius | Locked |
| Armory | Locked (2012 CKD gist) |
| Transform \(T\) | Unknown |
| Puzzle-linked seed/root | **None** |
| #71 solve command | **None** |

**Rule:** PASS locks historical generators only. Gate-5 (creator/Puzzle primary document) still **FAIL** for all three → no seed/root scan against Puzzle addresses.
