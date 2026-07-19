# Legacy Electrum v1 — Source Dossier

Last updated: 2026-07-19  
**No seed search. No Puzzle matching claimed as “Electrum test” until vectors match.**

## Purpose

Document what Electrum **actually did** in 2011–early 2015, so any future Puzzle comparison can be called an Electrum test only after independent reimplementation matches published behavior.

## Version context (verified from public sources)

| Period | Behavior | Source |
|--------|----------|--------|
| Electrum 1.x | Old seed (typically 12 words ↔ 128-bit / 32 hex); stretch; Type-2 style master+sequence; **uncompressed** pubkeys for addresses | StackExchange; Electrum issue #616 (2014-03-16); modern `OldkeyStore` in spesmilo/electrum |
| Electrum 2.0 plans | BIP32 + compressed keys announced | ecdsa comment on issue #616: “bip32 will be used in 2.0” (2014-03-16) |
| Puzzle TX date | 2015-01-15 | chain |

**Implication:** On puzzle creation day, stock Electrum 1.x still meant **uncompressed** address derivation. Electrum 2.x BIP32 era is adjacent in calendar but must be version-pinned with release tags before claiming.

## Seed format (documented)

| Property | Value | Source |
|----------|--------|--------|
| Entropy | **128-bit** typical | StackExchange electrum 1.x writeup; Electrum docs/community |
| Hex encoding | **32 hex characters** (ASCII hex string of entropy) | same; `OldkeyStore` expects hex seed string |
| Mnemonic | 12 (or custom 24) old Electrum words encoding that hex | StackExchange pseudocode |
| Randomness | **CSPRNG / OS random** in normal UI use — **not** TX timestamps or natural-language phrases | Historical wallet design; no source says timestamp→seed |

**Verified statement:** Literal phrase and multi-hour timestamp scans **do not** represent Electrum’s normal seed-generation path. They remain only “someone typed this into a non-default workflow” speculation.

## Stretching (documented)

Modern tree still documents old stretch (spesmilo/electrum `keystore.py` `OldkeyStore.stretch_key`):

- Input: hex seed as ASCII bytes  
- Loop **100000** times: `x = SHA256(x + encoded_hex_seed)`  
- Interpret digest as master secret scalar  

libbitcoin `electrum_v1.cpp` documents equivalent stretcher with `hash_iterations = 100000` and notes compression **false** for v1 convention:

https://github.com/libbitcoin/libbitcoin-system/blob/master/src/wallet/mnemonics/electrum_v1.cpp

StackExchange pseudocode (same structure):  
https://bitcoin.stackexchange.com/questions/37176/how-does-electrum-make-a-keypair-out-of-a-seed

**Caution:** Some third-party “cracker” snippets contain bugs (e.g. early `return` inside stretch loop). **Do not** treat random GitHub crackers as reference — prefer spesmilo or libbitcoin.

## Sequence / receiving / change (documented)

From current `OldkeyStore` (still encoding old semantics):

```text
get_sequence(mpk, for_change, n) =
  int(SHA256D( f"{n}:{for_change}:".encode('ascii') + bytes.fromhex(mpk) ))
```

- `for_change` ∈ {0, 1} — receiving vs change  
- Child private: `(stretched_master + sequence) mod n`  
- Pubkey from MPK: `04||mpk` then add `z*G`, export **`compressed=False`**

Source (live tree; line numbers drift):  
https://github.com/spesmilo/electrum/blob/master/electrum/keystore.py  
(search `OldkeyStore`, `stretch_key`, `get_sequence`, `get_pubkey_from_mpk`)

## Public-key serialization (documented)

| Item | Electrum 1.x | Source |
|------|--------------|--------|
| Address from | **Uncompressed** pubkey (65 bytes, `04…`) | Issue #616; `get_public_key_bytes(compressed=False)`; libbitcoin `compression = false` |
| Compressed planned | Electrum 2.0 / BIP32 era | Issue #616 thread |

## Index start

- Sequences use integer `n` with `for_change`.  
- Whether puzzle mapping would use `n=0` or `n=1` for puzzle #1 is **creator-unknown**; Electrum itself uses 0-based gap limits in later code — **do not invent mapping**.

## Our cascade Electrum mode (honesty)

`generator_cascade.py` electrum path:

- Builds material as `sha256(phrase)[:16].hex().encode()` — **not** a random 128-bit Electrum seed  
- Partial formula variants  
- **Not** validated against Electrum’s own test vectors in-repo  

Therefore prior electrum runs are labeled in `NEGATIVE_RESULTS.md` as **Kısmen test edildi / dar modelde negatif**, **not** “Electrum elendi”.

## Required before any future “Electrum vs Puzzle” claim

Checklist:

1. [ ] Pin exact Electrum tag/commit ≤ 2015-01-15 (or document 2.x if testing BIP32 Electrum).  
2. [ ] Reproduce official or well-known **old-seed → first 5 receiving addresses** vector.  
3. [ ] Independent reimplementation matches those 5 addresses.  
4. [ ] Only then compare Puzzle address list / low-bits cascade.  
5. [ ] Separate **source `K[i]`** vs **`P→A` compressed** (`SOURCE_SEQUENCE_REASSESSMENT.md`): stock 1.x poor as final exporter; as `K[i]` — not eliminated, no positive evidence.

## Published vectors

This pass did **not** paste third-party seed/address pairs (risk of unlicensed or unsafe material).  

Follow-up: pull vectors only from:

- Electrum unit tests in historical tags  
- libbitcoin electrum_v1 tests  
- StackExchange worked examples with cited seeds that are **known throwaway**

## Status (2026-07-20 reassessment)

**Dossier: historical behavior documented.**  
**As sole exporter of final Puzzle addresses:** still **poor fit** (uncompressed defaults vs 82/82 compressed `A[i]`).  
**As source sequence `K[i]` before unknown `T`:** **not eliminated; no positive evidence.** See `SOURCE_SEQUENCE_REASSESSMENT.md`.  
**Seed hunt:** closed without a justified seed candidate.
