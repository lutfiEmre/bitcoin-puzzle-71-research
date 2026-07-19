# Solved-Key Transform Audit

Last updated: 2026-07-20  
**Scope:** known solved Puzzle private keys only (`solved_keys.json`).  
**Forbidden:** searching for #71 or any unsolved key.

Creator claim (gist): consecutive deterministic keys, then **leading bits masked** to set difficulty.

Working hypothesis class (community / prior cascade):

```text
P(n) ∈ [2^(n-1), 2^n)
bit (n-1) of P(n) is 1
bits ≥ n of P(n) are 0
```

Equivalent construction form (one of several that satisfy the above):

```text
P(n) = 2^(n-1) | (K(n) & (2^(n-1) - 1))
```

`K(n)` = unknown source wallet key; `T` may be exactly this OR another map into the same range.

---

## Empirical check (Verified on 82 solved keys)

| Invariant | Result |
|-----------|--------|
| MSB at position `n-1` set | **82/82** |
| All bits at positions `≥ n` clear | **82/82** |
| `2^(n-1) ≤ P(n) < 2^n` | **82/82** |

**Verified:** Every solved key lies in the canonical half-open difficulty window.  
Creator’s “leading …0001” story is **consistent** with this class for all known solutions.

**Not verified:** The exact operator `T` (AND-mask vs other). Any `T` that lands in the same window fits the data.

---

## Index mapping (theory only — not eliminated)

If source wallet uses index `i` and Puzzle number is `n`:

| Mapping | Meaning | Status |
|---------|---------|--------|
| `i = n` | 1-based wallet index = puzzle number | Possible (Casascius-like) |
| `i = n - 1` | 0-based wallet index | Possible (Electrum-like) |
| `i = n + δ` | constant offset | Possible; δ unknown |
| separate receiving/change | Electrum `for_change` | Possible; untested vs Puzzle |

**No solved-key audit can decide `i` ↔ `n` without knowing `K`.** Document only.

---

## Transform classes contradicted by solved set

| Class | Verdict |
|-------|---------|
| Keys outside `[2^(n-1), 2^n)` | **Eliminated** for solved n |
| “No structure / full 256-bit random in window” as *description* | Still possible for `K`; `P` is window-constrained |
| Unmasked full Electrum/Armory address = Puzzle address | Already separated: Puzzle uses compressed `P→A` after `T` |

---

## Use in research program

1. Any candidate generator must produce `K(n)` such that **some** `T` maps into the verified window.  
2. Cascade `mask_be` is a **hypothesis for `T`**, not proven unique.  
3. Do not treat this audit as evidence for Electrum, Casascius, or any named tool.

## Cross-links

- `SOURCE_SEQUENCE_REASSESSMENT.md`  
- `NEGATIVE_RESULTS.md`  
- `GENERATOR_CENSUS_PRE2015.md`  
