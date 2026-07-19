# Historical Builder Reproduction Lab

Last updated: 2026-07-20  
Purpose: narrow **TX builder family** using **synthetic regtest data only**.  
**Forbidden:** real puzzle keys, real funding keys, mainnet broadcast, passphrase grind.

## Why this lab

Puzzle TX date: **2015-01-15**.  
Bitcoin Core **0.10.0** released **2015-02-16** (libsecp256k1 signing, new fee estimation).  

Therefore a normally released Core signer for the puzzle is more likely:

- **0.9.x**, or  
- **0.10 RC/pre-release** (unproven), or  
- **non-Core raw-RPC-compatible stack**

Calling the candidate set “Core ≥0.9” is too coarse. Prefer:

> Bitcoin Core **0.9.x / 0.10 pre-release / raw-RPC-compatible stack**

## Synthetic target template (matches puzzle structure, fake keys)

| Field | Value |
|-------|--------|
| Inputs | 1 × synthetic P2PKH UTXO |
| Outputs | 256 × P2PKH |
| `value(i)` | `(i + 1) * 100000` sat |
| version | builder default (expect 1) |
| locktime | builder default (expect 0) |
| Addresses | freshly generated throwaway keys on regtest |

Fee policy variants to test separately:

1. Explicit absolute fee **400000** sat (puzzle-like round remainder)  
2. Builder automatic fee estimation (Core 0.10+)  
3. Fixed fee rate (e.g. 50 sat/byte)

## Matrix to run

| Build ID | Software | Pin |
|----------|----------|-----|
| C093 | Bitcoin Core | **0.9.3** tag |
| C100 | Bitcoin Core | **0.10.0** tag (post-puzzle release; control) |
| BJ15 | bitcoinj | nearest release/tag ≤ 2015-01-15 |
| EL1 | Electrum | 1.9.x or last 1.x before 2.0 |
| AR15 | Armory | stable ≤ 2015-01-15 |
| PYRAW | Custom Python | `createraw`-style: ordered outs, no auto-change |
| CSRAW | Custom C# | same as PYRAW |

## Measurements (record per build)

| Metric | How |
|--------|-----|
| Output order preserved? | Compare vout[i] address/value to input list order |
| Auto-change added? | Extra output beyond 256? |
| Change position | Index if present |
| version / locktime / sequence | Parse raw hex |
| low-S? | Parse DER S vs curve order/2 |
| Sig length class | 71 vs 72 byte push |
| Fee mode | absolute leftover vs estimator vs rate |
| Accepts 256 recipients? | Success / UI limit / RPC error |
| Raw RPC order stable? | `createrawtransaction` JSON array order vs serialized outs |

## Pass / fail vs puzzle fingerprint

| Puzzle trait | Compatible if |
|--------------|---------------|
| 256 outs, values `(i+1)*1e5` | Exact |
| No extra change output | Exact (puzzle has none) |
| version=1, locktime=0, seq=`ffffffff` | Exact |
| low-S + compressed | Exact |
| Absolute fee 0.004 BTC | Match when fee forced; **mismatch** if only 0.10 estimator used without override |

## Status of this lab

| Item | Status |
|------|--------|
| Protocol defined | **Done** (this file) |
| Core 0.9.3 / 0.10.0 Docker runs | **Not executed** — **deprioritized** vs Bitstamp outpoint work |
| Expected outcome if run | Likely “Core/custom/bitcoinj all compatible; exact binary unknown” |
| Higher priority | `FUNDING_SIBLING_CLUSTER.md` (exact vout2 redeem — done; 2nd label source open) |

## Expected interpretive bounds

Even after runs:

- Matching Core 0.9.3 raw RPC **does not prove** creator used Core.  
- Failing Electrum GUI 256-send **does not eliminate** Electrum+external raw.  
- Fee leftover `0.004` BTC is **inferred** as likely manual absolute fee — testable by whether estimators spontaneously produce exactly 400000 sat (unlikely).

## Cross-links

- `TX_BUILDER_FINGERPRINT.md`  
- `WALLET_BUILDER_COMPARISON.md`  
- `FUNDING_SIBLING_CLUSTER.md`  
