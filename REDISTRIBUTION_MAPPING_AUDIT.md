# Redistribution Mapping Audit (2017-07-11)

Last updated: 2026-07-20  
**TXID:** `5d45587cfd1d5b0fb826805541da7d94c61fe432259e68ee26f4a04544384164`  
**Block:** `475240` · time `1499749253`  
**Explorer:** https://mempool.space/tx/5d45587cfd1d5b0fb826805541da7d94c61fe432259e68ee26f4a04544384164

**Scope:** on-chain input/output ↔ original Puzzle address map.  
**Not:** seed, generator ID, or #71 solve.

Original funding TX: `08389f34c98c606322740c0be6a7125d9860bb8d5cb182c02f98461e5fa6cd15` (256 outs, value = `n × 100000` sat).

---

## Input map (97 vins)

| vin range | Puzzle `n` | Value | Pubkey | Address match to original `vout[n-1]` |
|-----------|------------|-------|--------|----------------------------------------|
| `0 … 95` | **161 … 256** sequential | `n × 100000` sat | **96× compressed** | **96/96 exact** |
| `96` | — (not a puzzle UTXO) | `8 353 100 000` sat | **1× uncompressed** | Address `1CENDvi6tmKGrR8RxqwURpX9WHbbKip1db` **∉** puzzle set |

```text
vin[i]  = puzzle #(161 + i)   for i = 0..95
vin[96] = fee / top-up (uncompressed spend)
```

**Verified:** Input order is strictly ascending puzzle number **161→256**, then one non-puzzle top-up last.

---

## Output map (109 vouts)

| vout | Puzzle `n` | Value | Match original address |
|------|------------|-------|------------------------|
| `0` | **1** | `900000` = `9 × 100000` | **Yes** (`1BgGZ9tcN4rm9KBzDn7KprQz87SZ26SAMH`) |
| `1 … 108` | **53 … 160** sequential | `n × 900000` = `9 × (n × 100000)` | **108/108 Yes** |

```text
vout[0]     → puzzle #1   (+0.009 BTC)
vout[1 + k] → puzzle #(53 + k)  for k = 0..107  → #53..#160
```

Community “~10× lower range” story matches: each of #53–#160 receives an **additional 9×** its original unit prize; #1 receives a single `9×0.001` top-up; #2–#52 untouched by this TX.

Fee: `2 000 000` sat.  
`sum(vin) − sum(vout) = fee` (Verified).

---

## Script / construction fingerprint

| Question | Finding |
|----------|---------|
| Auto vs hand-built input list? | **Ordered by puzzle index** (value = `n×1e5` ascending). Strongly consistent with a **scripted** loop `for n in 161..256`, not a random wallet coin-select. |
| Uncompressed input = puzzle key? | **No** — sole uncompressed vin is the **top-up**, not #161–#256. |
| Puzzle keys in redistrib | All **compressed** spends (96/96). |
| Output order | `#1`, then `#53..#160` ascending — again script-like. |
| `i = n` vs `i = n−1` generator offset? | **No on-chain evidence.** Redistrib addresses are the **same** Puzzle `P→A` outputs; mapping is puzzle-number identity, not wallet derivation index. |

---

## What this does / does not show

| Shows | Does not show |
|-------|----------------|
| Creator could spend #161–#256 in index order | Which generator produced `K[i]` |
| Construction was almost certainly automated by puzzle number | Electrum change vs receiving |
| Top-up key path ≠ puzzle compressed path (one uncompressed) | Exact `T` or seed |
| Lower-range prize boost targets #53–#160 (+ tiny #1) | Offset between wallet `i` and puzzle `n` |

---

## Net

Redistribution is a **clean puzzle-number bookkeeping TX**. It is one of the last on-chain clues for creator tooling style (scripted, index-ordered, compressed puzzle keys + separate uncompressed funder), but it **does not** separate Casascius / Electrum / Armory and **does not** open a seed scan.

## Cross-links

- `PUBKEY_FINGERPRINT.md` (96C + 1U)  
- `CREATOR_ARCHIVE.md`  
- `EXACT_GENERATOR_MONTE_CARLO.md`  
