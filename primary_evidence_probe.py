#!/usr/bin/env python3
"""
Primary evidence watcher — G1..G5 candidate catcher (manual grade only).

Auto statuses: REJECT | KEYWORD_HIT | MANUAL_REVIEW_G1..G5
Grade A/B assigned only via --confirm-grade (human).

No seed/#71 grind. No execute of .dat/ZIP binaries (quarantine+hash).

  python3 primary_evidence_probe.py
  python3 primary_evidence_probe.py --ingest HTTPS_URL
  python3 primary_evidence_probe.py --ingest-file PATH
  python3 primary_evidence_probe.py --confirm-grade NORM_SHA A|B
  python3 primary_evidence_probe.py --list
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TARGETS = ROOT / "PRIMARY_EVIDENCE_TARGETS.tsv"
STATE_PATH = ROOT / "PRIMARY_EVIDENCE_STATE.json"
INBOX = ROOT / "primary_evidence_inbox"
ALERT_DIR = ROOT / "primary_evidence_alerts"
QUARANTINE = ROOT / "primary_evidence_quarantine"
UA = "puzzle71-primary-evidence-watch/0.2 (post-level baseline; no grind)"

EXPLORER_HOST_RE = re.compile(
    r"(^|\.)(blockchain\.info|blockchain\.com|mempool\.space|blockchair\.com|"
    r"btc\.com|blockstream\.info|sochain\.com|blockcypher\.com|"
    r"tradeblock\.com|smartbit\.com\.au|biteasy\.com|btcscan\.org)(/|$)",
    re.I,
)

BINARY_SUFFIXES = {".dat", ".zip", ".gz", ".tgz", ".tar", ".7z", ".rar", ".exe", ".dll", ".so", ".bin"}

# Post-level baseline for known 2017 creator message (NOT whole topic=1306983)
BASELINE_2017 = {
    "post_id": "18687273",
    "author": "saatoshi_rising",
    "msg_url_substr": "msg18687273",
    "date": "2017-04-27",
    "canonical_phrases": [
        "consecutive keys from a deterministic wallet",
        "masked with leading",
        "crude measuring instrument",
        "cracking strength of the community",
    ],
}

FORUM_GUESS_RE = re.compile(
    r"(i think|probably|maybe|could be|must be)\s+(electrum|armory|bip32|casascius|hmac)",
    re.I,
)


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def normalize_html(text: str) -> str:
    """Strip scripts/styles/nav-ish noise and collapse whitespace for stable hashing."""
    t = text
    t = re.sub(r"(?is)<script[^>]*>.*?</script>", " ", t)
    t = re.sub(r"(?is)<style[^>]*>.*?</style>", " ", t)
    t = re.sub(r"(?is)<nav[^>]*>.*?</nav>", " ", t)
    t = re.sub(r"(?is)<!--.*?-->", " ", t)
    # dynamic timestamps / counters often in these attrs/classes
    t = re.sub(r'(?i)\bdatetime="[^"]*"', 'datetime=""', t)
    t = re.sub(r"(?i)\bdata-time=\"[^\"]*\"", 'data-time=""', t)
    t = re.sub(r"(?is)<time[^>]*>.*?</time>", " ", t)
    t = re.sub(r"(?i)viewed?\s+\d+\s+times?", " ", t)
    t = re.sub(r"(?is)<[^>]+>", " ", t)
    t = re.sub(r"\s+", " ", t).strip().lower()
    return t


def baseline_canonical_hash() -> str:
    """Stable hash of known 2017 message phrase set (not full HTML)."""
    blob = "\n".join(p.lower() for p in BASELINE_2017["canonical_phrases"])
    return sha256_bytes(blob.encode())


def load_targets() -> list[dict[str, str]]:
    with TARGETS.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def load_state() -> dict:
    if STATE_PATH.exists():
        st = json.loads(STATE_PATH.read_text())
    else:
        st = {}
    st.setdefault("version", 2)
    st.setdefault("created", utc_now())
    st.setdefault("baseline_2017", {
        "post_id": BASELINE_2017["post_id"],
        "author": BASELINE_2017["author"],
        "canonical_content_sha256": baseline_canonical_hash(),
    })
    st.setdefault("known_baseline_normalized_sha256", [baseline_canonical_hash()])
    st.setdefault("seen_candidates", {})  # key = normalized_content_sha256
    st.setdefault("alerts", [])
    st.setdefault("quarantine", [])
    st.setdefault("last_run", None)
    st.setdefault("last_status", None)
    return st


def save_state(state: dict) -> None:
    state["last_run"] = utc_now()
    STATE_PATH.write_text(json.dumps(state, indent=2) + "\n")


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def parse_bitcointalk_meta(html: str, url: str) -> dict:
    """Extract post_id, author, published_at, canonical_url when present."""
    meta = {
        "post_id": "",
        "author": "",
        "published_at": "",
        "canonical_url": url,
        "archive_url": "",
    }
    m = re.search(r"msg(\d+)", url, re.I)
    if m:
        meta["post_id"] = m.group(1)
    m = re.search(r'id="msg(\d+)"', html, re.I)
    if m and not meta["post_id"]:
        meta["post_id"] = m.group(1)
    # Bitcointalk classic: <a href="...">saatoshi_rising</a> near poster
    m = re.search(
        r'class="[^"]*poster[^"]*"[^>]*>.*?href="[^"]*"[^>]*>([^<]+)</a>',
        html,
        re.I | re.S,
    )
    if m:
        meta["author"] = re.sub(r"\s+", " ", m.group(1)).strip()
    if not meta["author"]:
        m = re.search(r'title="View the profile of ([^"]+)"', html, re.I)
        if m:
            meta["author"] = m.group(1).strip()
    # published: <div class="smalltext">... April 27, 2017 ...
    m = re.search(
        r"(January|February|March|April|May|June|July|August|September|October|November|December)"
        r"\s+\d{1,2},\s+\d{4}",
        html,
    )
    if m:
        meta["published_at"] = m.group(0)
    # ISO-ish
    m2 = re.search(r"\b(20\d{2}-\d{2}-\d{2})\b", html)
    if m2 and not meta["published_at"]:
        meta["published_at"] = m2.group(1)
    if "web.archive.org/web/" in url:
        meta["archive_url"] = url
        m = re.search(r"web\.archive\.org/web/(\d{14})/(https?://\S+)", url)
        if m:
            meta["canonical_url"] = m.group(2)
            meta["snapshot_from_archive"] = m.group(1)
    return meta


def match_targets(text: str, url: str, targets: list[dict[str, str]]) -> list[dict[str, str]]:
    """Return TSV rows whose search_value tokens appear in text/url."""
    blob = (text + "\n" + url).lower()
    hits = []
    for row in targets:
        raw = row.get("search_value", "")
        # split on OR for alternatives; AND within a branch via spaces of quoted/unquoted tokens
        branches = [b.strip() for b in re.split(r"\s+OR\s+", raw, flags=re.I)]
        matched = False
        for br in branches:
            # tokens: quoted phrases or words
            toks = re.findall(r'"([^"]+)"|(\S+)', br)
            parts = [(a or b).lower() for a, b in toks if (a or b)]
            if parts and all(p in blob for p in parts):
                matched = True
                break
        if matched:
            hits.append(row)
    return hits


def is_baseline_2017_post(meta: dict, normalized: str) -> bool:
    """True only for the known message (post_id+author+phrase content), not whole thread."""
    if meta.get("post_id") == BASELINE_2017["post_id"]:
        if meta.get("author", "").lower() == BASELINE_2017["author"].lower() or not meta.get("author"):
            # content must look like the canonical post
            phrase_hits = sum(1 for p in BASELINE_2017["canonical_phrases"] if p.lower() in normalized)
            if phrase_hits >= 2:
                return True
    # Exact msg URL of the known post
    if BASELINE_2017["msg_url_substr"] in (meta.get("canonical_url") or "").lower():
        phrase_hits = sum(1 for p in BASELINE_2017["canonical_phrases"] if p.lower() in normalized)
        if phrase_hits >= 2:
            return True
    # Reprint of canonical phrase set without new technical material
    phrase_hits = sum(1 for p in BASELINE_2017["canonical_phrases"] if p.lower() in normalized)
    if phrase_hits >= 3 and "saatoshi" in normalized and "msg18687273" in normalized:
        return True
    return False


def source_is_pure_explorer(url: str) -> bool:
    """True if the *source document* is an explorer page, not an article that merely cites one."""
    u = (url or "").lower()
    if u.startswith("inbox://") or u.startswith("file://") or u.startswith("fixture://"):
        return False
    # host check
    m = re.match(r"^https?://([^/]+)/", u)
    if not m:
        return False
    host = m.group(1).split("@")[-1]
    return bool(EXPLORER_HOST_RE.search(host + "/"))


def classify_status(
    text: str,
    url: str,
    meta: dict,
    target_hits: list[dict[str, str]],
    normalized: str,
) -> tuple[str, str, str, str]:
    """
    Returns (auto_status, gate, material_type, reason).
    auto_status in REJECT_* | KEYWORD_HIT | MANUAL_REVIEW_G*
    grade stays pending until --confirm-grade.
    """
    # Pure explorer document → reject (articles citing explorers are OK)
    if source_is_pure_explorer(url):
        return "REJECT", "G?", "explorer", "source_is_explorer_host"

    if is_baseline_2017_post(meta, normalized):
        return "REJECT_BASELINE", "G4", "creator_message_baseline", "known_2017_post_id_author_phrases"

    # Gate from TSV hits (prefer first matching gate priority G1..G5)
    gate = ""
    material = ""
    hits = list(target_hits)
    if hits:
        order = {"G1": 0, "G2": 1, "G3": 2, "G4": 3, "G5": 4}
        hits = sorted(hits, key=lambda r: order.get(r.get("gate", "G9"), 9))
        gate = hits[0]["gate"]
        material = hits[0].get("material_type_hint", "")

    # Fake seed=puzzle style → KEYWORD_HIT (before forum-guess reject)
    if re.search(r"seed\s*=\s*['\"]?puzzle", text, re.I) and not re.search(
        r"xpub[a-zA-Z0-9]{80,}", text
    ):
        return "KEYWORD_HIT", gate or "G5", material or "keyword_context", "seed_equals_puzzle_without_material"

    if FORUM_GUESS_RE.search(text) and not any(
        x in normalized for x in ("xpub", "wallet.dat", "chain code", "2^(n-1)", "def ", "function")
    ):
        return "REJECT", "G?", "forum_guess", "forum_guess_without_material"

    # Strong material heuristics → MANUAL_REVIEW only (never auto A/B)
    has_xpub = bool(re.search(r"xpub[a-zA-Z0-9]{80,}", text))
    has_backup = bool(re.search(r"(wallet\.dat|electrum[^\n]{0,40}backup|mnemonic|root.?key\s*[:=])", text, re.I))
    has_t_code = bool(
        re.search(r"(2\s*\^\s*\(\s*n\s*-\s*1\s*\)|leading.?bit\s*mask|mask.*private\s*key)", text, re.I)
    ) and bool(re.search(r"\b(def|function|return|<<|>>|&)\b", text))
    has_txid = "08389f34c98c606322740c0be6a7125d9860bb8d5cb182c02f98461e5fa6cd15" in text.lower()
    has_creator = "saatoshi_rising" in normalized or "satoshi_rising" in normalized
    different_post = meta.get("post_id") and meta["post_id"] != BASELINE_2017["post_id"]

    if has_backup and (has_creator or "puzzle" in normalized):
        return "MANUAL_REVIEW_G1", "G1", "wallet_backup", "backup_marker_needs_human"
    if has_xpub and (has_txid or "puzzle" in normalized):
        return "MANUAL_REVIEW_G2", "G2", "mpk_root_xpub", "xpub_plus_puzzle_marker_needs_human"
    if has_t_code and (has_txid or "puzzle" in normalized):
        return "MANUAL_REVIEW_G3", "G3", "mask_T_code", "mask_code_plus_puzzle_needs_human"
    if has_creator and different_post and any(
        p.lower() in normalized for p in BASELINE_2017["canonical_phrases"][:2]
    ):
        return "MANUAL_REVIEW_G4", "G4", "creator_message", "same_author_different_post_needs_human"
    if has_t_code and has_txid:
        return "MANUAL_REVIEW_G5", "G5", "builder_or_mask_txid", "code_plus_txid_needs_human"
    if has_txid and has_backup:
        return "MANUAL_REVIEW_G5", "G5", "seed_binding", "backup_plus_txid_needs_human"

    # TSV keyword hit without strong material
    if hits or any(p.lower() in normalized for p in BASELINE_2017["canonical_phrases"]):
        return "KEYWORD_HIT", gate or "G4", material or "keyword_context", "target_or_phrase_hit_no_primary_material"

    return "REJECT", gate or "G?", "noise", "no_primary_markers"


def in_evidence_window(published_at: str, target_hits: list[dict[str, str]]) -> str:
    """Return ok|unknown|out_of_window note; discovery still allowed."""
    if not published_at or not target_hits:
        return "unknown"
    # extract year
    m = re.search(r"(20\d{2})", published_at)
    if not m:
        return "unknown"
    year = int(m.group(1))
    # use tightest start among hits
    starts = []
    for t in target_hits:
        s = (t.get("evidence_window_start") or "")[:4]
        if s.isdigit():
            starts.append(int(s))
    if not starts:
        return "unknown"
    if year < min(starts):
        return "before_evidence_window_discovery_only"
    return "in_or_after_evidence_window"


def grade_candidate(
    body: bytes,
    url: str,
    source_label: str,
    targets: list[dict[str, str]] | None = None,
) -> dict:
    targets = targets if targets is not None else load_targets()
    text_s = body.decode("utf-8", errors="replace")
    raw_sha = sha256_bytes(body)
    normalized = normalize_html(text_s)
    norm_sha = sha256_bytes(normalized.encode())

    meta = parse_bitcointalk_meta(text_s, url)
    target_hits = match_targets(text_s, url, targets)
    auto_status, gate, material, reason = classify_status(text_s, url, meta, target_hits, normalized)
    window_note = in_evidence_window(meta.get("published_at", ""), target_hits)

    excerpt = ""
    for p in BASELINE_2017["canonical_phrases"] + [t["search_value"][:40] for t in target_hits[:3]]:
        i = normalized.find(p.lower()[:30]) if p else -1
        if i >= 0:
            excerpt = normalized[max(0, i - 20) : i + 80]
            break
    if not excerpt:
        excerpt = normalized[:160]

    return {
        "source_url": url or source_label,
        "archive_url": meta.get("archive_url", ""),
        "canonical_url": meta.get("canonical_url", url),
        "author": meta.get("author", ""),
        "published_at": meta.get("published_at", ""),
        "snapshot_at": utc_now(),
        "post_id": meta.get("post_id", ""),
        "exact_excerpt": excerpt,
        "independent_source": "unknown",
        "creator_link": "baseline" if auto_status == "REJECT_BASELINE" else "none",
        "puzzle_link": "none",
        "material_type": material,
        "auto_status": auto_status,
        "grade": "pending",  # A/B only after --confirm-grade
        "gate": gate,
        "matched_targets": [t["search_value"] for t in target_hits],
        "evidence_window_note": window_note,
        "raw_sha256": raw_sha,
        "normalized_content_sha256": norm_sha,
        "reason": reason,
        "ingested_via": source_label,
    }


def quarantine_binary(path: Path, state: dict) -> dict:
    """Do not execute; hash + static metadata only."""
    QUARANTINE.mkdir(exist_ok=True)
    body = path.read_bytes()
    raw = sha256_bytes(body)
    dest = QUARANTINE / f"{raw[:16]}_{path.name}"
    if not dest.exists():
        dest.write_bytes(body)
    rec = {
        "source_url": f"inbox://{path.name}",
        "archive_url": "",
        "canonical_url": "",
        "author": "",
        "published_at": "",
        "snapshot_at": utc_now(),
        "post_id": "",
        "exact_excerpt": f"binary quarantine size={len(body)} suffix={path.suffix}",
        "independent_source": "unknown",
        "creator_link": "none",
        "puzzle_link": "none",
        "material_type": "binary_quarantine",
        "auto_status": "MANUAL_REVIEW_G1" if path.suffix.lower() == ".dat" else "KEYWORD_HIT",
        "grade": "pending",
        "gate": "G1" if path.suffix.lower() == ".dat" else "G?",
        "matched_targets": [],
        "evidence_window_note": "unknown",
        "raw_sha256": raw,
        "normalized_content_sha256": raw,  # binary: same
        "reason": "binary_quarantined_not_executed",
        "ingested_via": f"quarantine:{path.name}",
        "quarantine_path": str(dest.relative_to(ROOT)),
    }
    state["quarantine"].append({"raw_sha256": raw, "path": rec["quarantine_path"], "at": utc_now()})
    return rec


def ingest_bytes(body: bytes, url: str, label: str, state: dict, targets: list[dict] | None = None) -> dict:
    rec = grade_candidate(body, url, label, targets)
    key = rec["normalized_content_sha256"]
    prev = state["seen_candidates"].get(key)
    # also treat known baseline normalized list
    if key in state.get("known_baseline_normalized_sha256", []):
        rec["auto_status"] = "REJECT_BASELINE"
        rec["reason"] = "known_baseline_normalized_sha256"
    rec["is_new"] = prev is None
    # preserve human grade if re-seen
    if prev and prev.get("grade") in ("A", "B"):
        rec["grade"] = prev["grade"]
    state["seen_candidates"][key] = {k: v for k, v in rec.items() if k != "is_new"}
    return rec


def scan_inbox(state: dict, targets: list[dict]) -> list[dict]:
    INBOX.mkdir(exist_ok=True)
    out = []
    for p in sorted(INBOX.iterdir()):
        if not p.is_file() or p.name.startswith(".") or p.name == "README.md":
            continue
        if p.suffix.lower() in BINARY_SUFFIXES:
            rec = quarantine_binary(p, state)
            key = rec["normalized_content_sha256"]
            prev = state["seen_candidates"].get(key)
            rec["is_new"] = prev is None
            state["seen_candidates"][key] = {k: v for k, v in rec.items() if k != "is_new"}
            out.append(rec)
            continue
        out.append(ingest_bytes(p.read_bytes(), f"inbox://{p.name}", f"inbox:{p.name}", state, targets))
    return out


def maybe_alert(rec: dict, state: dict) -> bool:
    """Alert only on NEW MANUAL_REVIEW_* (not auto A/B)."""
    if not rec.get("is_new"):
        return False
    if not str(rec.get("auto_status", "")).startswith("MANUAL_REVIEW_"):
        return False
    ALERT_DIR.mkdir(exist_ok=True)
    path = ALERT_DIR / f"REVIEW_{rec['auto_status']}_{rec['normalized_content_sha256'][:12]}.json"
    path.write_text(json.dumps(rec, indent=2) + "\n")
    state["alerts"].append(
        {
            "normalized_content_sha256": rec["normalized_content_sha256"],
            "auto_status": rec["auto_status"],
            "gate": rec["gate"],
            "file": path.name,
            "at": utc_now(),
        }
    )
    return True


def confirm_grade(state: dict, norm_sha: str, grade: str) -> None:
    grade = grade.upper()
    if grade not in ("A", "B"):
        raise ValueError("grade must be A or B")
    rec = state["seen_candidates"].get(norm_sha)
    if not rec:
        raise KeyError(f"unknown normalized sha {norm_sha}")
    if not str(rec.get("auto_status", "")).startswith("MANUAL_REVIEW_"):
        raise RuntimeError("confirm-grade only allowed on MANUAL_REVIEW_* candidates")
    rec["grade"] = grade
    rec["grade_confirmed_at"] = utc_now()
    state["seen_candidates"][norm_sha] = rec


def list_targets() -> None:
    for r in load_targets():
        print(f"  [{r['gate']}] {r['search_value'][:70]}")
        print(f"       window {r['evidence_window_start']}→{r['discovery_window_end']}")


def main() -> int:
    args = sys.argv[1:]
    state = load_state()
    targets = load_targets()

    if "--list" in args:
        list_targets()
        print("RESULT: PASS")
        return 0

    if "--confirm-grade" in args:
        i = args.index("--confirm-grade")
        confirm_grade(state, args[i + 1], args[i + 2])
        save_state(state)
        print(f"CONFIRMED grade={args[i + 2].upper()} sha={args[i + 1][:16]}…")
        print("RESULT: PASS")
        return 0

    results: list[dict] = []

    if "--ingest" in args:
        if args.index("--ingest") + 1 >= len(args):
            print("USAGE: --ingest https://…")
            print("STATUS: NO_NEW_PRIMARY_EVIDENCE")
            print("RESULT: PASS")
            return 0
        url = args[args.index("--ingest") + 1]
        if url.upper() == "URL" or not re.match(r"^https?://", url, re.I):
            print(f"INVALID_INGEST: {url!r} — pass a real https URL")
            print("STATUS: NO_NEW_PRIMARY_EVIDENCE")
            print("RESULT: PASS")
            return 0
        try:
            results.append(ingest_bytes(fetch(url), url, "ingest-url", state, targets))
        except (urllib.error.URLError, TimeoutError, OSError, ValueError) as e:
            print(f"INGEST_FAIL {url}: {e}")

    if "--ingest-file" in args:
        path = Path(args[args.index("--ingest-file") + 1])
        if path.suffix.lower() in BINARY_SUFFIXES:
            results.append(quarantine_binary(path, state))
            key = results[-1]["normalized_content_sha256"]
            results[-1]["is_new"] = key not in state["seen_candidates"] or results[-1].get("is_new", True)
        else:
            results.append(
                ingest_bytes(path.read_bytes(), f"file://{path}", f"file:{path.name}", state, targets)
            )

    results.extend(scan_inbox(state, targets))

    seen = set()
    uniq = []
    for r in results:
        k = r["normalized_content_sha256"]
        if k in seen:
            continue
        seen.add(k)
        uniq.append(r)

    alerts = []
    for r in uniq:
        print(
            f"  status={r['auto_status']} new={r['is_new']} gate={r['gate']} "
            f"grade={r['grade']} author={r.get('author') or '-'} "
            f"post={r.get('post_id') or '-'} reason={r['reason']}"
        )
        if maybe_alert(r, state):
            alerts.append(r)

    if alerts:
        state["last_status"] = "NEW_MANUAL_REVIEW_CANDIDATE"
        save_state(state)
        print("\nSTATUS: NEW_MANUAL_REVIEW_CANDIDATE")
        for a in alerts:
            print(f"  → primary_evidence_alerts/ ({a['auto_status']})")
            print("  human: review then --confirm-grade <norm_sha> A|B to reopen gate")
        print("RESULT: PASS")
        return 0

    state["last_status"] = "NO_NEW_PRIMARY_EVIDENCE"
    save_state(state)
    print("\nSTATUS: NO_NEW_PRIMARY_EVIDENCE")
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:
        print(f"RESULT: FAIL ({e})", file=sys.stderr)
        raise SystemExit(1)
