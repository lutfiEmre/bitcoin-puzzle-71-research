# GITHUB_PROVENANCE_PASS

**Date:** 2026-07-20  
**Input:** 49 `github_hits` → 37 unique non-NLP repo/path (10 ResCU NLP false-positives skipped)  
**Tool:** `github_provenance_pass.py`  
**Compute gate:** **CLOSED** — no auto Grade A/B

---

## Verdict (short)

| Question | Answer |
|----------|--------|
| New primary Puzzle evidence? | **No** |
| Pre-2015 Puzzle artifact in hit set? | **No** |
| Creator-linked commit/email? | **No** |
| Verified #71 pubkey / seed / T? | **No** |
| What are the 2014 dates? | **bitcoinj BIP32 library history** (Matija-era code), not Puzzle |

Priority targets are all **2021–2026** mirrors/tools/research notes.

```text
justified #71 solve command: NONE
```

---

## Priority targets

| Repo / path | Repo created | First commit on match | Class |
|-------------|--------------|----------------------|-------|
| `pbies/bitcoin-tools` `python/p71-01.py` | 2021-10 | **2026-02-16** | MODERN_MIRROR_OR_TOOL |
| `accessor-io/pattern` `bitcoin_puzzle_solver.py` | 2024-12 | **2025-04-20** | MODERN_MIRROR_OR_TOOL |
| `alex-place/lantern-os` (2 paths) | 2026-05 | **2026-06-16** | MODERN_MIRROR_OR_TOOL |
| `consigcody94/glv-kangaroo-paper` (2 paths) | 2026-03 | **2026-03-21/22** | MODERN_MIRROR_OR_TOOL |
| `HomelessPhD/BTC32` lists/README | 2021-03 | **2021-03-14** | LIST_OR_TRACKER |
| `onepuzzle/puzzle-generator` | — | **not in hit set / CDX empty** | missing upstream |

---

## Historical interest (not Puzzle bridge)

| Repo | First path commit | Meaning |
|------|-------------------|---------|
| `bitcoinj/bitcoinj` `DeterministicHierarchy.java` | 2014-09-30 | BIP32 classes era — ResCU/Mazi **C+** context only |
| bitcoinj forks with same blob date | 2014-09-30 | Copied bitcoinj history |
| `bitcoinj.github.io` release-notes | 2014-04-30 | Release docs, not Puzzle |

---

## Full data

- Machine-readable: `GITHUB_PROVENANCE_STATE.json` (37 rows: author, email, sha, matching lines, cites)
- Re-run: `GITHUB_TOKEN="$(gh auth token)" python3 github_provenance_pass.py`

### Class counts (approx)

- `MODERN_MIRROR_OR_TOOL` — majority (2024–2026)
- `LIST_OR_TRACKER` — address/TXID lists
- `HISTORICAL_INTEREST` — bitcoinj BIP32 lineage
- `SECONDARY_RESEARCH` — dashj / elastos / verimobile copies

---

## What this closes

Re-running `discovery_backfill` on the same strings will not change this. These hits are **provenance-dated**: modern copies + bitcoinj library history.

Next evidence must be **new** (new post ID, bridged gist, new CDX digest, verified pubkey) — not another pass over these 49.

Watcher may stay for disclosure catch; fixed-URL research polling is low value.
