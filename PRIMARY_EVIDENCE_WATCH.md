# Primary Evidence Watch

**Active after synthetic lab.** Tooling verified; #71 closed until human-confirmed G1–G5.

```bash
python3 primary_evidence_probe.py
python3 primary_evidence_probe.py --ingest 'https://bitcointalk.org/index.php?topic=1306983.msg18687273'
python3 primary_evidence_probe.py --ingest-file ./candidate.html
python3 primary_evidence_probe.py --confirm-grade <normalized_sha> A   # human only
python3 test_primary_evidence_probe.py -v
```

Inbox: `primary_evidence_inbox/` · Quarantine (binaries): `primary_evidence_quarantine/`  
State: `PRIMARY_EVIDENCE_STATE.json` · Targets: `PRIMARY_EVIDENCE_TARGETS.tsv`

---

## Auto statuses (never auto Grade A/B)

| Status | Meaning |
|--------|---------|
| `REJECT` / `REJECT_BASELINE` | Noise / known 2017 **post** (msg18687273) |
| `KEYWORD_HIT` | Target/phrase hit, no primary material |
| `MANUAL_REVIEW_G1`…`G5` | Human review queue → optional `--confirm-grade A\|B` |

## Baseline (post-level)

Known 2017 message is identified by **`post_id=18687273` + author `saatoshi_rising` + canonical phrase set** — **not** by `topic=1306983` alone. A new post in the same thread can become `MANUAL_REVIEW_G4`.

## Hashing

| Field | Role |
|-------|------|
| `raw_sha256` | Exact bytes |
| `normalized_content_sha256` | Scripts/styles/nav/time/whitespace stripped — dedupe key |

## Gates G1–G5

Unchanged (`REOPEN_GATE.md`). Compute reopens only after **human** Grade A / strong B confirm.

## Binaries

`.dat` / `.zip` / archives → quarantine + hash + static note; **never executed**.

## Cross-links

- `REOPEN_GATE.md` · `SYNTHETIC_PUZZLE_LAB.md` · `test_primary_evidence_probe.py`  
