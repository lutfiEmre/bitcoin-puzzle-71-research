# Research Closure — Bitcoin Puzzle #71

**Final state:** `CLOSED_PENDING_NEW_PRIMARY_EVIDENCE`  
**Tag:** `research-closure-v1.0`  
**Date:** 2026-07-20  

## Correct statement of the result

Puzzle #71 is **not** proven absolutely unsolvable.  

With **currently available public evidence**, there is **no verifiable, computationally justified solution path**. Forcing new guesses does not advance the result.

```text
justified #71 search command: NONE
justified candidate set: EMPTY
```

Manifest: `REPRODUCIBILITY_MANIFEST.json`  
Reopen rules: `REOPEN_GATE.md`

---

## Eliminated / exhausted

| Line | Outcome |
|------|---------|
| Solved-key statistical fingerprinting | No generator separation |
| Exact Casascius / Electrum v1 / Armory locks + comparison | Formulas locked; **no Puzzle link** |
| Tested window transforms (`T_low` / `T_high`; `T_mod`≡`T_low`) | Families inseparable under tested features |
| Exact-generator Monte Carlo classification | ~chance accuracy (30-seed stability) |
| Transaction-builder fingerprinting | Compatible era; **not identified** |
| 2017 redistribution mapping | Clean puzzle-number script; **no `i↔n` offset** |
| Funding provenance / sibling cluster | Bounded; **not creator ID** |
| Creator phrase / alias archives | One 2017 operational post; **no seed/T** |
| Prefix / vanity-address claims | Closed / non-evidence |
| Bitaddress + generic generator archives | Grade **C**, `puzzle_link=none` |
| Puzzle linkage triage (Pass 1–3) | `CLOSED_PENDING_NEW_PRIMARY_EVIDENCE` |

---

## Still unknown

- Exact generator family used for Puzzle `K[i]`
- Seed / root / passphrase
- Exact transform `T`
- Wallet derivation index map (`i` ↔ puzzle `n`)
- Creator-linked backup, MPK, or builder source code

---

## Operational conclusion

**No justified #71 search command exists.**

Do **not** reopen GPU / passphrase / seed / prefix grind without a gate in `REOPEN_GATE.md`.

---

## Meaningful work *after* closure (optional)

1. **Synthetic lab:** build a controlled deterministic-wallet → `T` → address → recovery demo to prove tooling (not #71).  
2. **Watch only:** archive monitor for Grade **A/B** hits on creator alias, phrases, TXIDs, addresses — alert only on A/B.  
3. **Wait** for primary documents.

---

## Cross-links

- `REOPEN_GATE.md`  
- `REPRODUCIBILITY_MANIFEST.json`  
- `PUZZLE_LINKAGE_TRIAGE.md`  
- `EXACT_GENERATOR_MONTE_CARLO.md`  
- `CREATOR_ARCHIVE.md`  
