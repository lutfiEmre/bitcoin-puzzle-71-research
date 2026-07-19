# Transaction-Structure Fingerprint — Results

Last updated: 2026-07-20  
**Private key / seed araması değildir.**

## Puzzle referansı

TXID: `08389f34c98c606322740c0be6a7125d9860bb8d5cb182c02f98461e5fa6cd15`  
Fingerprint: 256 P2PKH outputs, value[i]=(i+1)*100000 sat, sum=3289600000 sat.

## BigQuery execution

| Madde | Değer |
|-------|--------|
| Project | `abiding-casing-454317-t3` |
| Dataset (attempt) | `puzzle_research` (US) — created; table create failed on quota |
| Smoke tests | `SELECT 1` OK; block 339085 output_count=2346 OK |

### Strict query — COMPLETED

File: `sql/tx_fingerprint_strict.sql`  
Window: block_timestamp ∈ [2014-01-01, 2016-01-01)  
CSV: `bq_results/strict_20260719T211751Z.csv`

| transaction_hash | block_number | block_timestamp | output_count | exact_position_matches | output_sum |
|------------------|--------------|-----------------|--------------|------------------------|------------|
| `08389f34c98c606322740c0be6a7125d9860bb8d5cb182c02f98461e5fa6cd15` | 339085 | 2015-01-15 18:07:14 | 256 | 256 | 3289600000 |

**Exactly one matching transaction.**

#### Interpretation (bounded)

- In the queried period, **no second transaction** shares this exact 256-output arithmetic fingerprint.
- This **weakens** “the same exact builder pattern was reused elsewhere with the same output schedule.”
- This **does not** prove the script was used only once (different output counts / step / totals possible).
- This **does not** reveal seed, wallet name, derivation path, or Puzzle #71 private key.

### Arith-256 / Arith-50+ — NOT COMPLETED

| Query | Dry-run bytes (upper bound) | Status |
|-------|----------------------------|--------|
| `tx_fingerprint_arith256.sql` | ~896 GB | **Quota exceeded** — not run |
| `tx_fingerprint_arith50plus.sql` | ~207 GB | **Quota exceeded** — not run |
| CREATE TABLE tx_256_candidates | — | **Quota exceeded** — table empty / not created |

**No conclusion is drawn from incomplete broader scans.**

Free-tier scan quota exhausted for this project. Do not retry the same wide scans until quota resets or billing is intentionally enabled.

## What this did / did not do for Puzzle #71

| Did | Did not |
|-----|---------|
| Answer: sibling exact-fingerprint TX in 2014–2016 window? → **only Puzzle TX** | Find seed or #71 key |
| Narrow “copy-paste same funding ritual elsewhere” hope | Eliminate custom Type-1/Type-2/BIP32 |
| Documentable negative-ish structural result | Replace need for historical evidence |

## Program status

| Hat | Statü |
|-----|--------|
| Cascade | **Kapalı** |
| Native random | **Kapalı** (piyango) |
| BigQuery strict fingerprint | **Tamamlandı** |
| BigQuery geniş fingerprint | **Kota — tamamlanmadı** |
| Overall | **Yeni belge bekliyor** |

Yeniden hesaplama açma koşulları değişmedi: creator mesajı, script, wallet backup formatı, veya yeni on-chain bağlantı.

## Cross-links

- `CREATOR_ARCHIVE.md`  
- `PUBKEY_FINGERPRINT.md`  
- `NEGATIVE_RESULTS.md`  
- `sql/*.sql` / `run_bq_fingerprint.sh`
