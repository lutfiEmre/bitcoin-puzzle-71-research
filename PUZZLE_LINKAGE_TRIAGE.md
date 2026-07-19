# Puzzle Linkage Triage

Last updated: 2026-07-20  

```bash
python3 linkage_triage.py --pass-all
```

Artifacts: `LINKAGE_EVIDENCE_MATRIX.tsv` · `linkage_hits/bitaddress_dedup.json` · `linkage_hits/triage_summary.json`

---

## Stop rule (applied)

```text
PUZZLE_LINKAGE_LINE: CLOSED_PENDING_NEW_EVIDENCE
```

After Pass 1–3: **no Grade A**, **no strong Grade B** (independent of the known 2017 post) that yields seed / root / exact `T`.

Canonical `saatoshi_rising` 2017-04-27 message remains **operational Grade B** (`CREATOR_ARCHIVE.md`) — it does **not** open a #71 scan by itself.

---

## Date model

| Field | Role |
|-------|------|
| `evidence_window` | Dates that can **count as proof** |
| `discovery_window` | Later pages allowed as **pointers** only (`discovery_only=yes`) |
| `claimed_original_date` / `verified_original_date` | Claim vs verified origin |

A 2020 post citing a 2015 gist URL = discovery tool, not evidence, until the 2015 artifact is verified.

---

## Pass results

### Pass 3 — Bitaddress (closed fast)

| Metric | Value |
|--------|--------|
| CDX in-window | 81 |
| Unique content keys | 32 (dedup by version+SHA1 / path) |
| Downloaded unique HTML | ~18 (some Wayback RST) |
| Keywords scanned | bulk, brainwallet, deterministic, sequence, privateKey, seed, mask, shift, truncate |
| Grade | **C** |
| `puzzle_link` | **none** |

`mask` / `shift` hits are stock JS/UI (bit operations, form fields), **not** Puzzle “leading 000…0001” difficulty masking. Bulk = random CSV. Brain = single-key.  

→ Bitaddress is **not** a Puzzle builder lead. Do not re-open.

### Pass 1 — Creator phrase / alias

| Item | Status |
|------|--------|
| Targets scaffolded in matrix | handle + exact + fragments |
| Canonical 2017 post | Logged (not a new find) |
| Independent earlier post / gist / paste | **Not found this pass** |
| Copies of 2017 wording on later pages | Explicitly **non-evidence** (`is_quote_of_known_2017_post`) |

### Pass 2 — Address / TXID timeline

| Asset | Status |
|-------|--------|
| `1Czoy…`, `173uj…`, `1CEND…`, `08389f34…` | Matrix rows pending independent non-explorer first-seen |
| Indexed open-web (prior `CREATOR_ARCHIVE`) | Meaningful non-explorer hit **not found** |
| Explorer mirrors | **Ignore / Grade D** |

---

## Evidence grades (reopen rule)

| Grade | Reopen #71 compute? |
|-------|---------------------|
| **A** creator-linked root/MPK/exact T/builder script | Yes (narrow) |
| **Strong B** independent pre-fame original code/phrase with date proof | Yes if strong |
| Known 2017 post alone | **No** |
| **C** / **D** | **No** |

---

## Puzzle #71 — what you do next (honest)

**You do not “solve #71” from current public math + solved keys.**

Closed / exhausted for justified attack:

1. Solved-key generator ID (Casascius / Electrum / Armory masked sequences)  
2. Exact-generator Monte Carlo separation  
3. Cascade / random / prefix grind without Gate-5 document  
4. Bitaddress / generic tool linkage  
5. This linkage triage pending **new** primary evidence  

**Still unknown (blocking):**

| Unknown | Needed |
|---------|--------|
| Seed / root / passphrase | Grade A document or tiny justified set |
| Transform `T` | Creator code or equivalent |
| Generator family as Puzzle source | Still unlinked |

**Only path that advances #71 with integrity:**

1. Find Grade **A** or strong **B** outside this frozen line (new archive drop, leak, second creator post with material, wallet backup).  
2. Then — and only then — open a **narrow** verify against known addresses.  
3. Without that, more GPU / more Monte Carlo / more phrase lists does **not** produce a justified solve command.

```text
#71 solve command: NONE
Justified candidate set: EMPTY
Next: wait / hunt primary documents — not compute
```

## Cross-links

- `linkage_triage.py`  
- `LINKAGE_EVIDENCE_MATRIX.tsv`  
- `PUZZLE_LINKAGE_HUNT.md`  
- `CREATOR_ARCHIVE.md`  
- `EXACT_GENERATOR_MONTE_CARLO.md`  
