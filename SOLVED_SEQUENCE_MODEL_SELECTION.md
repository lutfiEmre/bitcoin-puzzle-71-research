# Solved-Sequence Model Selection

Last updated: 2026-07-20  
**Scope:** public solved Puzzle keys only (`solved_keys.json`, 82 keys).  
**Forbidden:** seed/root grind, #71 search, passphrase expansion.

**Question:** Does “consecutive deterministic keys + leading-bit masking” leave a fingerprint that **separates** Casascius / Electrum 1.x / Armory after `T`?

Self-check: `python3 solved_sequence_model_selection.py` → `VERDICT: PRELIMINARY_NO_SEPARATION` / `RESULT: PASS`.

**Superseded for family ID:** synthetic generators in that script are **not** the locked Casascius/Electrum/Armory formulas. See `EXACT_GENERATOR_MONTE_CARLO.md` / `exact_generator_model_selection.py` for the real comparison.

---

## Model under test

```text
K[i]  = generator family output (unknown seed/root)
T     = unknown map into difficulty window
P[n]  = T(K[i(n)]) ∈ [2^(n-1), 2^n)
```

Working `T` class (consistent with all 82; not proven unique):

```text
P[n] = 2^(n-1) | (K[i(n)] & (2^(n-1) - 1))
```

Observable free bits: `L[n] = P[n] & (2^(n-1)-1)` (= low bits of `K` under this `T`).

---

## Why formulas alone do not open a scan

| Known | Unknown |
|-------|---------|
| Casascius / Electrum / Armory exact CKD formulas (locked) | seed / root / passphrase |
| Window constraint on `P[n]` | exact `T` operator |
| Creator wording (consecutive + mask) | index map `i ↔ n` |

Scanning any family’s seed space without Gate-5 evidence is full brute force again. Locks only prevent wrong implementations.

---

## Checks performed (solved keys only)

### 1. Window / leading-bit class

| Check | Result |
|-------|--------|
| `P[n] ∈ [2^(n-1), 2^n)` | **82/82** |
| Forced bit `n-1` set; bits `≥ n` clear | **82/82** |

Compatible with AND-mask, modulo-into-window, rejection clamp — **same observable**.

### 2. Index map `n ↔ i`

| Map | Fits family habit | Separable from `P` alone? |
|-----|-------------------|---------------------------|
| `i = n` | Casascius 1-based | **No** |
| `i = n - 1` | Electrum / Armory 0-based | **No** |
| `i = n + δ` | any | **No** |
| receiving vs change | Electrum / Armory chain bit | **No** |

Without `K`, index/branch hypotheses are **not identifiable** from `P`.

### 3. Free-bit randomness (AND-mask residue)

| Statistic | Observed | Null (uniform-in-window MC) |
|-----------|----------|------------------------------|
| Pooled free-bit ones rate | ≈ 0.492 | compatible (~20th pct) |
| Bit-position χ² > 3.84 | 1 / 62 | ≈ expected false-positive rate |
| Mean Hamming z-score of `P` | ≈ −0.13 | near 0 |

No systematic low-bit bias that would favor one generator.

### 4. Consecutive-pair structure (`n`, `n+1` both solved; 69 pairs)

| Probe | Targets | Observed | Expect if random after `T` |
|-------|---------|----------|----------------------------|
| XOR popcount fraction of shared-width `L` | independence | ≈ 0.503 | 0.5 |
| Circular \|ΔL\| / 2^(n−1) | Electrum additive residue | ≈ 0.250 | 0.25 |
| `gcd(P[n],P[n+1]) > 1` rate | Armory multiplicative residue | 26/69 | MC same (~52nd pct) |

Electrum’s `(master+seq)` and Armory’s `(IL×k)` relations **do not survive** per-`n` width masking at a detectable level.

### 5. Synthetic family collision

Generate throwaway Casascius-like / Electrum-like / Armory-like `K`, apply the same window `T`, measure consecutive XOR popfrac:

| Synth family | Mean XOR popfrac |
|--------------|------------------|
| Casascius-like | ≈ 0.500 |
| Electrum-like | ≈ 0.502 |
| Armory-like | ≈ 0.503 |
| Real solved | ≈ 0.503 |

**Spread < 0.02** — families collapse to the same null after `T`.

---

## Verdict (preliminary — softened)

| Outcome | Result |
|---------|--------|
| Free bits look random under window `T` | **Yes** (this script) |
| Real Casascius / Electrum / Armory separated? | **Not tested here** |
| Claim “three locked families indistinguishable” | **Too strong for this file** |
| Shortlist reduce to one family | **Not justified** |
| Open seed scan | **Still forbidden** |

**What this file actually proves:** solved `P[n]` low bits pass basic randomness vs a uniform-in-window null, and three **randomized synthetic** models are indistinguishable from each other (expected, since they are already noise).

**What it does not prove:** that the three **locked** generator implementations are inseparable after `T`. That requires `exact_generator_model_selection.py`.

`VERDICT: PRELIMINARY_NO_SEPARATION`

---

## When a scan would open

At least one of:

1. Puzzle-linked exact passphrase / root  
2. Wallet backup / MPK / xpub / root fingerprint tied to the Puzzle  
3. Creator code defining exact `T`  
4. Tiny, historically justified candidate list  
5. A **new** solved-key fingerprint that isolates one locked family (none found here)

None present now.

---

## Net route

1. ~~Generator locks~~ — Casascius, Electrum 1.x, Armory **PASS**  
2. Preliminary free-bit audit — `PRELIMINARY_NO_SEPARATION` (stubs)  
3. Exact MC + 30-seed stability — `NO_SEPARATION_DETECTED_UNDER_TESTED_TRANSFORMS_AND_FEATURES`  
4. Redistrib I/O map — no `i↔n` offset  
5. **Solved-sequence generator-ID line — CLOSED**  
6. **Active:** `PRE2015_ARCHIVE_HUNT.md`  

| Item | State |
|------|--------|
| Transform `T` | Unknown (`T_low`/`T_high` tested; `T_mod`≡`T_low`) |
| Generator ID from masked sequences | **No separation under tested setup** |
| Puzzle-linked seed/root | **None** |
| #71 solve command | **None** |

## Cross-links

- `EXACT_GENERATOR_MONTE_CARLO.md` / `exact_generator_model_selection.py`  
- `PRE2015_ARCHIVE_HUNT.md`  
- `REDISTRIBUTION_MAPPING_AUDIT.md`  
- `SOLVED_KEY_TRANSFORM_AUDIT.md`  
- `GENERATOR_DIFFERENTIAL_AUDIT.md`  
