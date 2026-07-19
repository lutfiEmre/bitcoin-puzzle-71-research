# Puzzle Linkage Hunt

Last updated: 2026-07-20  
**Status:** `PUZZLE_LINKAGE_LINE: CLOSED_PENDING_NEW_EVIDENCE`  
See `PUZZLE_LINKAGE_TRIAGE.md` for Pass 1–3 results and stop rule.

Active inventory remains for when **new** primary evidence appears; do not expand compute.

Inventory: `PUZZLE_LINKAGE_TARGETS.tsv`  
Probe: `puzzle_linkage_probe.py`  
Related (generic tools, dated windows): `ARCHIVE_TARGETS.tsv` + `archive_index_probe.py`

```bash
python3 puzzle_linkage_probe.py --list
python3 puzzle_linkage_probe.py --bitaddress-wild   # CDX wildcards in-window
python3 puzzle_linkage_probe.py --cdx-url URL --not-before YYYY-MM-DD --not-after YYYY-MM-DD
```

---

## Date windows (critical)

| Target | `not_before` | `not_after` |
|--------|--------------|-------------|
| Generator / wallet tool source | tool birth | **2015-01-15** |
| Puzzle TXID `08389f34…` | **2015-01-15** | ~2017-04-27 (early discussion) |
| Funding / change / top-up addrs | first on-chain appearance (~**2015-01-15**) | early discussion era |
| Creator phrase / handle | **2015-01-15** (puzzle exists) | known post **2017-04-27** (hunt *earlier* same wording) |
| Redistrib TXID `5d45587c…` | **2017-07-11** | +1y announcements |
| Mask `T` code | may be **pre-2015** | through **2017-04-27** |

**Do not** CDX-filter the puzzle TXID under ≤2015-01-14 — the TX did not exist.

---

## Evidence grades

| Grade | Meaning | Re-opens compute? |
|-------|---------|-------------------|
| **A** | Creator-linked root / MPK / exact `T` / builder script | **Yes** (narrow) |
| **B** | Same original code or phrase **before** public puzzle fame / before known 2017 post, with date proof | **Yes** if strong |
| **C** | Date-fit generic generator (Casascius/Electrum/…) | **No** scan |
| **D** | Forum guess, numerology, prefix list, explorer mirror | **No** |

Only **A** or strong **B** reopen a calculation line.

---

## Priority A — Creator identity / language

Handles: `saatoshi_rising`, `Satoshi_Rising`  

Exact + fragments:

```text
"consecutive keys from a deterministic wallet"
"masked with leading 000...0001"
"crude measuring instrument"
"cracking strength of the community"
"consecutive keys" "deterministic wallet"
"leading zeros" masked bitcoin puzzle
"measuring instrument" bitcoin cracking
```

Goal: older post / gist / paste / README by the **same person**, not formula encyclopedias.

---

## Priority B — First web appearance of chain objects

```text
1Czoy8xtddvcGrEhUUCZDQ9QqdRfKh697F
173ujrhEVGqaZvPHXLqwXiSmPVMo225cqT
1CENDvi6tmKGrR8RxqwURpX9WHbbKip1db
08389f34c98c606322740c0be6a7125d9860bb8d5cb182c02f98461e5fa6cd15
5d45587cfd1d5b0fb826805541da7d94c61fe432259e68ee26f4a04544384164
```

**Reject:** blockchain.com / mempool.space / btc.com / blockchair explorer copies.  
**Want:** forum, paste, gist, wallet debug, script, donation line, same-alias reuse.

---

## Priority C — Structural code constants

```text
256 outputs
100000 satoshi
0.001 * index
0.01 * key length
161 256 deterministic
0000000000000001 mask
```

Anonymous gist/paste of a **puzzle builder** beats another generic HD wallet.

---

## Artifact quality rules

Prefer: raw file, git commit, release tarball, tag archive, zip/tar.gz, forum attachment, gist **raw revision**.  
Deprecate: GitHub repo homepage HTML as technical source.

Per artifact record: `source_commit`, `source_date`, `archive_snapshot`, `sha256`, `mime_type`, `is_source_code`, `is_primary_source`.  

Same bytes → one file; multiple TSV rows may share `artifact_sha256`.

Armory gist missing from Wayback: **OK** — original gist revision/date is primary.

---

## Bitaddress CDX wildcards

```text
bitaddress.org/*
www.bitaddress.org/*
bitaddress.org/*.html
bitaddress.org/*.zip
bitaddress.org/*.js
```

Apex-only CDX emptiness ≠ no child paths.

---

## Status

| Item | State |
|------|--------|
| Justified #71 scan candidates | **None** |
| Grade A/B hits in TSV | **pending / empty** |
| Next work | Fill linkage TSV from Wayback/forum/paste — not expand generator MC |

## Cross-links

- `PUZZLE_LINKAGE_TARGETS.tsv`  
- `CREATOR_ARCHIVE.md`  
- `ARCHIVE_TARGETS.tsv`  
- `PRE2015_ARCHIVE_HUNT.md`  
- `REDISTRIBUTION_MAPPING_AUDIT.md`  
