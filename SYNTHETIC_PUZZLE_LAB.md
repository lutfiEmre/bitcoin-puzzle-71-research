# Synthetic Puzzle Lab

**Not Puzzle #71.** Controlled demo: known root → locked generator → known `T` → compressed P2PKH → recovery.

```bash
python3 synthetic_puzzle_lab.py           # n=1..32
python3 synthetic_puzzle_lab.py --full    # n=1..256
```

Output: `synthetic_lab_out/`

---

## Pipeline (lab)

```text
throwaway root  →  K[i] (Casascius C1 / Electrum recv / Armory M/0/0/i)
                →  T_low: P[n] = 2^(n-1) | (K & (2^(n-1)-1))
                →  compressed P2PKH A[n]
                →  re-derive from same root → match all A[n]
wrong root      →  must NOT match
```

| Family | Index map | Root (throwaway, fixed) |
|--------|-----------|-------------------------|
| `casa_c1` | `i = n` | passphrase string |
| `elec_recv` | `i = n−1` | 16-byte hex → 100k stretch |
| `armory` | `i = n−1` on `M/0/0/i` | fixed priv+chain (**path = lab hypothesis**) |

`T` is **known by construction** (`T_low`). Real Puzzle `T` remains unknown.

**Lab note:** under `T_low`, puzzle `n=1` has **zero free bits** → `P=1` for every family (same compressed address). Distinction appears only for `n≥2`.

---

## What this proves

- Locked generator implementations + window mask + compressed address path work end-to-end.
- Recovery is trivial **when** root + family + `T` + index map are known.
- Wrong root fails → search without those inputs is not “the same lab”.

## What this does **not** prove

- Which family the real Puzzle used  
- Real seed / `T` / index map  
- Any #71 candidate  

Real #71 stays `CLOSED_PENDING_NEW_PRIMARY_EVIDENCE` (`REOPEN_GATE.md`).

## Cross-links

- `synthetic_puzzle_lab.py`  
- `EXACT_GENERATOR_MONTE_CARLO.md`  
- `RESEARCH_CLOSURE.md`  
