# Source Sequence vs Puzzle Address — Methodology Reassessment

Last updated: 2026-07-20

## Working schema (hypothesis, not verified transform)

Creator described consecutive deterministic keys then adjusting difficulty so keys
begin with `000…0001`. A useful **working sketch**:

```text
Source deterministic key K[i]     ← wallet / generator (unknown family)
        ↓  unknown transform T
Puzzle private key P[i]
        ↓  (re)derive pubkey + HASH160
Puzzle address A[i]
```

**`T` is unknown.** Not confirmed:

- which bits of the scalar are forced / cleared  
- AND-mask vs modulo vs other construction  
- whether Puzzle #1 maps to source index 0 or 1  
- how invalid scalars (`≥ n`, zero) are handled before/after `T`

Cascade’s `mask_be` / `mask_le` are **test hypotheses**, not the creator’s proven `T`.

Whatever `T` is, it generally **breaks** the original address of `K[i]`. On-chain
Puzzle addresses only constrain **`P[i] → A[i]`** serialization (82/82 compressed).

## Error to retract

Earlier: compressed Puzzle addresses ⇒ stock Electrum / Armory **eliminated**.

Correct: compression only binds **`P → A`**. It does **not** eliminate those
wallets as possible **`K[i]`** sources. It also does **not** add positive evidence
for them.

### Corrected status (no probability inflation)

| Family | Status |
|--------|--------|
| Stock Electrum v1 as **`K[i]`** | **Not eliminated; no positive evidence** |
| Stock Armory as **`K[i]`** | **Not eliminated; no positive evidence** |
| Casascius BAU C1/C2 | **Concrete historical candidate** (source + test vector). **No Puzzle link.** |
| gmaxwell Type-1 / custom SHA indexed | Historical fit to 2011 language; not Puzzle-linked |
| BIP32 | Possible; R1–R7 only narrow paths |

Stock Electrum/Armory remain **weak as sole final address exporters** (uncompressed
defaults vs compressed `A[i]`). As `K[i]` feeders into unknown `T` + separate
compressed rebuild: possible, unproven.

## Cascade vs Casascius

Full matrix: **`CASCADE_COVERAGE.md`**.

- C2 exact: **never in R1–R7**  
- C1: not dedicated; `sha_seed_ascii` is not a Casascius claim  

## What not to do

- Call Casascius “likely” or Electrum/Armory “raised to medium probability”  
- Bulk passphrase grind because BAU exists  
- Treat `mask_be` as verified creator `T`  
- Seed-hunt Electrum/Armory without a justified seed

## Status sentence

Casascius C2 was not previously tested; without a historically justified
passphrase, **Puzzle comparison stays closed**. Gain: knowing exactly which
formulas were / were not covered.

## Cross-links

- `CASCADE_COVERAGE.md`  
- `CASASCIUS_BAU_DOSSIER.md`  
- `PUBKEY_FINGERPRINT.md` (`P→A` only)  
- `LEGACY_ELECTRUM_DOSSIER.md` / `ARMORY_DOSSIER.md`  
- `NEGATIVE_RESULTS.md`  
- `casascius_vector_selftest.py`  
