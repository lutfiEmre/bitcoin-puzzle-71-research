# Exact Generator Monte Carlo

Last updated: 2026-07-20  
**Purpose:** model selection with **locked** Casascius / Electrum v1 / Armory CKD.  
**Forbidden:** seed grind vs Puzzle; #71 search.

```bash
python3 exact_generator_model_selection.py          # demo + 30-seed stability
python3 exact_generator_model_selection.py --quick  # demo only
```

---

## Scope limits (read before citing verdict)

| Claimed | Not claimed |
|---------|-------------|
| Under **tested** `T` + **hand features** + **nearest-centroid** on **canonical trio**, mean holdout ≈ chance | All possible features / ML models |
| C2 / change / index appear in **probe stats only** | Classifier separates those variants |
| Armory **CKD formula** locked to 2012 gist | Puzzle uses path `M/0/0/i` (hypothesis only) |

**Verdict string (scoped):**

```text
NO_SEPARATION_DETECTED_UNDER_TESTED_TRANSFORMS_AND_FEATURES
```

Do **not** write “generators are indistinguishable in general.”

---

## Transforms (2 distinct, not 3)

```text
T_low:  P = 2^(n-1) | (K & (2^(n-1)-1))
T_high: P = 2^(n-1) | (K >> (256-(n-1)))
```

`T_mod = 2^(n-1) + (K mod 2^(n-1))` ≡ `T_low` — **removed** from the suite.

---

## Armory path hypothesis

Code derives address children as **`M/0/0/i`** (account 0 → EXTERNAL → index).

- CKD operator: **vector-locked** (`ARMORY_VECTOR_LOCK.md`)
- This tree path as Puzzle `K[i]` layout: **assumed for MC only**, not creator-verified

---

## Classifier setup

| Item | Value |
|------|--------|
| Labels | `casa_c1@i=n`, `elec_recv@i=n−1`, `armory@i=n−1` |
| Not labels | C2, Electrum change, alternate index (probes only) |
| Features | free-bit p1, XOR popfrac, circular ΔL, LSB agree, high-bit agree, ΔP |
| Model | nearest-centroid |
| Chance | ≈ 33.3% |
| Sequence | masked `P[n]` for n=1..40 |

---

## Stability (30 `RANDOM_SEED`s)

| Transform | mean ± std | range |
|-----------|------------|-------|
| `T_low` | **0.339 ± 0.093** | [0.111, 0.556] |
| `T_high` | **0.323 ± 0.080** | [0.111, 0.444] |

Means sit on chance. One `T_low` seed hit 0.556 — expected with holdout n=36 (binomial σ≈0.08); **gate uses means**, not single-seed max.

**SOLVED_SEQUENCE_LINE: CLOSED** under this tested setup.

---

## Research consequence

Masked consecutive sequences from the three locked families do not yield a practical generator ID with these probes.  

**Next:** external archive hunt — `PRE2015_ARCHIVE_HUNT.md`.  
**Not next:** random / cascade / prefix scans (no justified candidate set).

## Cross-links

- `exact_generator_model_selection.py`  
- `SOLVED_SEQUENCE_MODEL_SELECTION.md` (preliminary; stubs)  
- `REDISTRIBUTION_MAPPING_AUDIT.md`  
- `PRE2015_ARCHIVE_HUNT.md`  
