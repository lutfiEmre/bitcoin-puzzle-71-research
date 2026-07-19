# Armory — Exact Vector Lock

Last updated: 2026-07-20  
**Status: LOCKED** — `python3 armory_chain_selftest.py` → `RESULT: PASS`

**Purpose:** lock Alan Reiner’s 2012-04-27 CKD test vector byte-for-byte.  
**Not** a Puzzle #71 hunt. No seed grind. No Armory→Puzzle claim.

---

## Primary source

| Item | Value |
|------|--------|
| Author | Alan Reiner (etotheipi) |
| Date | 2012-04-27 |
| Gist | https://gist.github.com/etotheipi/2513316 |
| File | `ckd_output.txt` — “Child Key Derivation Test Vector(s)” |
| API | `HDWalletCrypto().ChildKeyDeriv` / `ExtendedKey` |
| Extended key | triplet `(Priv, Pub, Chain)`; Pub empty Priv → Pub computed |

Gist requirement (verbatim intent): generate the same sequences in **private key space** and **public key space**; they must produce the same addresses.

---

## Exact CKD (verified)

```text
I  = HMAC-SHA512(chain, uncompressed_pubkey(65B) ‖ BE32(index))
k' = (IL × k) mod n     # multiply — not BIP32 additive CKD
c' = IR
```

Public-only path (Priv empty):

```text
same I from parent uncompressed pub ‖ BE32(index)
K' = IL × K             # EC point multiply
c' = IR
```

| Detail | Locked value |
|--------|----------------|
| Index serialization | **big-endian** `uint32` (gist BE display matches CKD) |
| Pubkey in HMAC data | **uncompressed** 65-byte (`04‖X‖Y`) |
| Output Pub print | **compressed** 33-byte |
| Scalar combine | **multiply** mod \(n\) (≠ BIP32 add) |
| `HDW_CHAIN_EXTERNAL` | `0` → path `…/0` |
| `HDW_CHAIN_INTERNAL` | `1` → path `…/1` |
| Account / address index | **0-based** tree `M/account/chain/i` |

Endianness display from the same gist (self-test asserts):

| Form | Value | Hex |
|------|-------|-----|
| LE(5) | | `05000000` |
| LE(4095) | | `ff0f0000` |
| BE(5) | | `00000005` |
| BE(4095) | | `00000fff` |

---

## Fixed root inputs (`ckdTestVectors`)

| Field | Hex |
|-------|-----|
| Priv | `aa` × 32 |
| Pub (input) | `04` + `6a04ab98…74691a6` (65B uncompressed) |
| Chain | `dd` × 32 |

Root compressed Pub (derived): `026a04ab98d9e4774ad806e302dddeb63bea16b5cb5f223ee77478e861bb583eb3`

---

## Locked tree nodes (Priv / Pub / Chain)

All nodes below are asserted in `armory_chain_selftest.py` (private walk + public walk equality).

| Path | Role in gist code |
|------|-------------------|
| `M` | root |
| `M/0`, `M/1` | accounts |
| `M/0/0`, `M/0/1` | EXTERNAL / INTERNAL on account 0 |
| `M/0/0/0`, `M/0/0/1`, `M/0/0/2` | external addresses |
| `M/0/1/0`, `M/0/1/1`, `M/0/1/2` | internal addresses |
| `M/1/1` | account 1 INTERNAL chain |
| `M/1/1/4095`, `M/1/1/4294967295` | large indices |

First five address-level children byte-locked:  
`M/0/0/0`, `M/0/0/1`, `M/0/0/2`, `M/0/1/0`, `M/0/1/1`.

---

## Scope note (important)

This lock covers the **2012 HD `ChildKeyDeriv` CKD** published in the gist.

It does **not** by itself lock every later Armory wallet format, nor the older “classic” sequential `Priv(i)→Priv(i+1)` chaincode story in product docs. Those remain separate historical modes. For generator census, this vector proves Armory had an **exact, reproducible consecutive-child tree** before 2015.

---

## Gate status

| Gate | Result |
|------|--------|
| Exact published throwaway vector | **PASS** |
| Private + public paths agree | **PASS** |
| ≥5 children byte-identical | **PASS** |
| Puzzle / creator primary link | **FAIL** (none) |
| Open Armory seed space vs Puzzle | **Forbidden** until Gate-5 |

---

## Cross-links

- Self-test: `armory_chain_selftest.py`
- Differential: `GENERATOR_DIFFERENTIAL_AUDIT.md`
- Census: `GENERATOR_CENSUS_PRE2015.md`
- Prior dossier: `ARMORY_DOSSIER.md`
