# Electrum 1.x — Exact Vector Lock

Last updated: 2026-07-20  
**Purpose:** promote Electrum 1.x from “partial” to **exact implementable**.  
**Not** a Puzzle #71 hunt. No seed grind.

Self-test: `python3 electrum_v1_vector_selftest.py` → must print `RESULT: PASS`.

---

## Version pin

| Item | Value | Source |
|------|--------|--------|
| Family | Electrum **1.x / “old seed”** (pre-BIP32 wallet type) | spesmilo history; issue #616 |
| Reference impl | `Old_KeyStore` in current spesmilo/electrum tree (legacy semantics preserved) | `electrum/keystore.py` |
| Historical availability | 2011 – early 2015 (puzzle day still in 1.x era for old wallets) | dossier |
| Independent vectors | bip_utils tests: “Verified with the official Electrum wallet” | [test_electrum_v1.py](https://github.com/ebellocchia/bip_utils/blob/master/tests/electrum/test_electrum_v1.py), [test_electrum_v1_mnemonic.py](https://github.com/ebellocchia/bip_utils/blob/master/tests/electrum/mnemonic/test_electrum_v1_mnemonic.py) |

---

## Exact formulas (Verified against spesmilo + bip_utils)

### Old seed form

- Typical: **128-bit** entropy → **32 ASCII hex chars** (`hex_seed`).  
- Or 12 old-Electrum words decoding to that hex.  
- Stretch input is the **ASCII encoding of the hex string**, not raw entropy bytes.

### Stretch (100 000 rounds)

```text
encoded = hex_seed.encode("ascii")
x = encoded
for i in 1..100000:
    x = SHA256(x || encoded)
master = x   # 32-byte scalar
```

Source: `Old_KeyStore.stretch_key`.

### Master public key (mpk)

```text
mpk = uncompressed_pubkey(master)[1:]   # 64-byte XY, no 0x04 prefix, hex-stored
```

### Sequence / child

```text
seq = int( SHA256d( f"{n}:{for_change}:".encode("ascii") || bytes.fromhex(mpk) ) )
child_priv = (master + seq) mod n
```

- **`n`:** address index, **0-based**  
- **`for_change`:** `0` = receiving, `1` = change  

### Address

- P2PKH from **uncompressed** pubkey (`compressed=False`).

---

## Locked throwaway vectors

### A — entropy → stretch → address[0]

| entropy (hex) | stretched master (hex) | receiving n=0 |
|---------------|------------------------|---------------|
| `0000…00` (16 bytes) | `7c2548ab89ffea8a…195abe5` | `1FHsTashEBUNPQwC1CwVjnKUxzwgw73pU4` |
| `e6914a31dc45fe52a979acde7128cfb4` | `151d19768f1c2bc0…0da5ed` | `1KxCSrMZLH2haDyaZ6VjfgmCx7od6voX8u` |

### B — master → first 5 receiving addresses

Master: `0bbe2537d7527f2d7376d4bb9de8ac42ca202dbae310471b88f2cbb0492e6e73`  
WIF: `5HuTXx6TC56nonxHfw3DmM72CurZ22zh24azdCmz3gh3We2Ujvk`

| n | Address |
|---|---------|
| 0 | `1P5Ai2wW2x93onQW5ZSDfHhu5LTgBPNx7r` |
| 1 | `1dGnYwstcGq5fsEkSkV3jpgbfKQf2wgR1` |
| 2 | `1CcNXYJW7DEtqLECPQGoTr8mhZEC7X9i8X` |
| 3 | `12Gq5N1tDRUx7Tn7nEgHunazoAcDK1p6sw` |
| 4 | `1L828t7SY3qzpKf3u3LfNNVvUHKtcQxBk8` |

---

## Gate status (census)

| Gate | Electrum 1.x |
|------|----------------|
| Pre-2015-01-15 | **Pass** |
| Consecutive deterministic keys | **Pass** |
| ≥256 export capable | **Pass** (gap / generate) |
| Source + test vector | **Pass** (this lock) |
| Puzzle/creator document link | **Fail** — technical candidate only |

→ Seed scan against Puzzle: **still closed**.

---

## Cross-links

- `LEGACY_ELECTRUM_DOSSIER.md`  
- `GENERATOR_CENSUS_PRE2015.md`  
- `SOURCE_SEQUENCE_REASSESSMENT.md`  
- `electrum_v1_vector_selftest.py`  
