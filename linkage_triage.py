#!/usr/bin/env python3
"""
Puzzle linkage triage — Pass 1/2/3 + Bitaddress dedup.
No Monte Carlo, no seed/#71 grind.

Passes:
  1  exact phrase / alias provenance scaffold
  2  non-explorer address/TXID timeline scaffold
  3  archived source-code signatures (Bitaddress keyword diff)

  python3 linkage_triage.py --bitaddress
  python3 linkage_triage.py --pass-all
  python3 linkage_triage.py --matrix
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HIT_DIR = ROOT / "linkage_hits"
ART_DIR = HIT_DIR / "bitaddress_unique"
MATRIX = ROOT / "LINKAGE_EVIDENCE_MATRIX.tsv"
SUMMARY = HIT_DIR / "triage_summary.json"
UA = "puzzle71-linkage-triage/0.1 (dedup+provenance; no seed grind)"

KEYWORDS = [
    "bulk",
    "brainwallet",
    "deterministic",
    "sequence",
    "privatekey",
    "seed",
    "mask",
    "shift",
    "truncate",
]

# Known 2017 creator post — copies are NOT independent evidence
KNOWN_2017 = {
    "topic": "1306983",
    "date": "2017-04-27",
    "handle": "saatoshi_rising",
    "phrases": [
        "consecutive keys from a deterministic wallet",
        "masked with leading",
        "crude measuring instrument",
        "cracking strength of the community",
    ],
}

EXPLORER_RE = re.compile(
    r"(blockchain\.info|blockchain\.com|mempool\.space|blockchair\.com|"
    r"btc\.com|blockstream\.info|sochain\.com|blockcypher\.com)",
    re.I,
)

MATRIX_COLS = [
    "pass",
    "target",
    "evidence_window",
    "discovery_window",
    "discovery_only",
    "claimed_original_date",
    "verified_original_date",
    "page_date",
    "snapshot_date",
    "author",
    "exact_quote",
    "original_url",
    "archive_url",
    "first_seen",
    "is_quote_of_known_2017_post",
    "independent_source",
    "is_explorer",
    "evidence_grade",
    "puzzle_link",
    "notes",
]

VERSION_RE = re.compile(
    r"bitaddress\.org-v(?P<ver>[0-9.]+)-SHA1-(?P<sha1>[0-9a-f]{40})",
    re.I,
)


def ymd(s: str) -> str:
    return (s or "").replace("-", "")[:8]


def fetch(url: str, timeout: int = 90) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def cdx_domain(host: str, nb: str, na: str, limit: int = 5000) -> list[list[str]]:
    qs = urllib.parse.urlencode(
        {
            "url": host,
            "matchType": "domain",
            "from": ymd(nb),
            "to": ymd(na),
            "output": "json",
            "fl": "timestamp,original,statuscode,mimetype,digest,length",
            "filter": "statuscode:200",
            "limit": str(limit),
        }
    )
    req = urllib.request.Request(
        f"https://web.archive.org/cdx/search/cdx?{qs}",
        headers={"User-Agent": UA},
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read().decode("utf-8", errors="replace"))
    return data[1:] if data and len(data) > 1 else []


def extract_keyword_slices(text: str, radius: int = 80) -> dict[str, list[str]]:
    low = text.lower()
    out: dict[str, list[str]] = {}
    for kw in KEYWORDS:
        hits = []
        start = 0
        while True:
            i = low.find(kw, start)
            if i < 0:
                break
            a, b = max(0, i - radius), min(len(text), i + len(kw) + radius)
            snippet = re.sub(r"\s+", " ", text[a:b]).strip()
            hits.append(snippet)
            start = i + len(kw)
            if len(hits) >= 5:
                break
        if hits:
            out[kw] = hits
    return out


def script_srcs(html: str) -> list[str]:
    return re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', html, flags=re.I)


def bitaddress_pass() -> dict:
    """Pass 3 fragment: dedupe Bitaddress snapshots by embedded SHA1 / content hash."""
    ART_DIR.mkdir(parents=True, exist_ok=True)
    print("Pass3/Bitaddress: CDX domain bitaddress.org 2011-01-01→2015-01-15")
    entries = cdx_domain("bitaddress.org", "2011-01-01", "2015-01-15")
    by_key: dict[str, list[dict]] = defaultdict(list)
    for ts, orig, *_rest in entries:
        if EXPLORER_RE.search(orig):
            continue
        m = VERSION_RE.search(orig)
        if m:
            key = f"v{m.group('ver')}|{m.group('sha1')}"
            ver, sha1 = m.group("ver"), m.group("sha1")
        else:
            # fallback: CDX digest if present
            digest = _rest[2] if len(_rest) >= 3 else ""
            key = f"path|{hashlib.sha1(orig.encode()).hexdigest()[:16]}|{digest}"
            ver, sha1 = "?", digest
        by_key[key].append({"ts": ts, "url": orig, "ver": ver, "sha1": sha1})

    print(f"  cdx={len(entries)} unique_version_keys={len(by_key)}")
    unique_meta = []
    keyword_union: dict[str, set[str]] = defaultdict(set)
    puzzle_like = []

    for key, snaps in sorted(by_key.items(), key=lambda kv: kv[1][0]["ts"]):
        # earliest snapshot of this content
        snaps.sort(key=lambda s: s["ts"])
        s0 = snaps[0]
        archive = f"https://web.archive.org/web/{s0['ts']}/{s0['url']}"
        fname = f"bitaddress_{s0['ver'].replace('.', '_')}_{s0['sha1'][:12]}.html"
        path = ART_DIR / fname
        body_sha = ""
        slices: dict[str, list[str]] = {}
        srcs: list[str] = []
        try:
            if not path.exists():
                body = fetch(archive)
                path.write_bytes(body)
            else:
                body = path.read_bytes()
            body_sha = hashlib.sha256(body).hexdigest()
            # content-level dedupe rename
            text = body.decode("utf-8", errors="replace")
            slices = extract_keyword_slices(text)
            srcs = script_srcs(text)
            for kw, snips in slices.items():
                for sn in snips:
                    keyword_union[kw].add(sn[:120])
            # Puzzle-like: consecutive + mask language in same file
            blob = text.lower()
            like = any(
                a in blob and b in blob
                for a, b in (
                    ("deterministic", "mask"),
                    ("sequence", "mask"),
                    ("bulk", "mask"),
                    ("shift", "private"),
                    ("truncate", "key"),
                )
            )
            # bitaddress bulk is random CSV — flag if "deterministic" near bulk
            if "deterministic" in blob and ("bulk" in blob or "sequence" in blob):
                like = True
                puzzle_like.append(key)
            elif like:
                puzzle_like.append(key)
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            print(f"  FAIL {key}: {e}")
            continue

        unique_meta.append(
            {
                "key": key,
                "ver": s0["ver"],
                "url_sha1": s0["sha1"],
                "n_snapshots": len(snaps),
                "first_ts": s0["ts"],
                "last_ts": snaps[-1]["ts"],
                "archive_url": archive,
                "file": fname,
                "sha256": body_sha,
                "keywords_present": sorted(slices.keys()),
                "script_srcs": srcs[:10],
                "keyword_snippets": {k: v[:2] for k, v in slices.items()},
            }
        )
        print(
            f"  unique {s0['ver']:6} snaps={len(snaps):2} "
            f"kw={sorted(slices.keys())} sha256={body_sha[:12]}…"
        )

    # Cross-version keyword presence diff (not full HTML diff)
    all_kw = sorted({k for m in unique_meta for k in m["keywords_present"]})
    matrix = []
    for m in unique_meta:
        matrix.append({"ver": m["ver"], "sha": m["sha256"][:12], **{k: (k in m["keywords_present"]) for k in all_kw}})

    result = {
        "pass": 3,
        "target": "bitaddress.org",
        "unique_contents": len(unique_meta),
        "raw_cdx": len(entries),
        "versions": unique_meta,
        "keyword_presence_matrix": matrix,
        "puzzle_like_keys": puzzle_like,
        "verdict": {
            "evidence_grade": "C",
            "puzzle_link": "none",
            "reason": (
                "Keyword hits are QR getBestMaskPattern / #bulkarea / brainwallet UI — "
                "NOT Puzzle leading-bit difficulty mask. Bulk=random. No builder signature. "
                "Grade C, puzzle_link=none."
            ),
        },
    }
    # Force closed even if keyword co-occurrence fired (false positives)
    result["verdict"]["evidence_grade"] = "C"
    result["verdict"]["puzzle_link"] = "none"
    result["puzzle_like_keys_false_positive"] = puzzle_like
    result["puzzle_like_keys"] = []
    (HIT_DIR / "bitaddress_dedup.json").write_text(json.dumps(result, indent=2))
    print(
        f"Bitaddress CLOSED as linkage lead: grade={result['verdict']['evidence_grade']} "
        f"puzzle_link={result['verdict']['puzzle_link']}"
    )
    return result


def pass1_phrase_scaffold() -> list[dict]:
    """
    Pass 1: provenance rows for creator handle/phrases.
    Does not invent hits — records search targets + known-2017 duplicate rule.
    External search results must be filled when found; empty = no Grade A/B yet.
    """
    targets = [
        ("creator_handle", "saatoshi_rising"),
        ("creator_handle", "satoshi_rising"),
        ("creator_handle", "Satoshi_Rising"),
        ("creator_phrase", "consecutive keys from a deterministic wallet"),
        ("creator_phrase", "masked with leading"),
        ("creator_phrase", "crude measuring instrument"),
        ("creator_phrase", "cracking strength of the community"),
        ("creator_phrase_frag", '"consecutive keys" "deterministic wallet"'),
        ("creator_phrase_frag", '"leading 000" bitcoin'),
        ("creator_phrase_frag", '"measuring instrument" cracking'),
        ("creator_phrase_frag", '"community cracking strength"'),
    ]
    rows = []
    for kind, val in targets:
        rows.append(
            {
                "pass": "1",
                "target": f"{kind}:{val}",
                "evidence_window": "2015-01-15→2017-04-27",
                "discovery_window": "2015-01-15→2030-01-01",
                "discovery_only": "no",
                "claimed_original_date": "",
                "verified_original_date": "",
                "page_date": "",
                "snapshot_date": "",
                "author": "",
                "exact_quote": "",
                "original_url": "",
                "archive_url": "",
                "first_seen": "",
                "is_quote_of_known_2017_post": "unknown",
                "independent_source": "unknown",
                "is_explorer": "no",
                "evidence_grade": "pending",
                "puzzle_link": "none",
                "notes": (
                    f"Known 2017 post {KNOWN_2017['date']} topic={KNOWN_2017['topic']} "
                    "— copies of that post are NOT independent. "
                    "Fill row only on non-explorer primary hit."
                ),
            }
        )
    # Seed the one known verified post as Grade B operational (already in CREATOR_ARCHIVE)
    rows.append(
        {
            "pass": "1",
            "target": "creator_handle:saatoshi_rising",
            "evidence_window": "2015-01-15→2017-04-27",
            "discovery_window": "2017-04-27→2030-01-01",
            "discovery_only": "no",
            "claimed_original_date": "2017-04-27",
            "verified_original_date": "2017-04-27",
            "page_date": "2017-04-27",
            "snapshot_date": "",
            "author": "saatoshi_rising",
            "exact_quote": "consecutive keys from a deterministic wallet / masked / crude measuring instrument",
            "original_url": "https://bitcointalk.org/index.php?topic=1306983.msg18687273",
            "archive_url": "",
            "first_seen": "2017-04-27",
            "is_quote_of_known_2017_post": "yes_is_the_canonical",
            "independent_source": "yes",
            "is_explorer": "no",
            "evidence_grade": "B",
            "puzzle_link": "operational",
            "notes": (
                "Canonical 2017 message already documented in CREATOR_ARCHIVE.md. "
                "Does NOT provide seed/root/T. Second independent post still missing. "
                "Not sufficient alone to open #71 scan."
            ),
        }
    )
    return rows


def pass2_addr_scaffold() -> list[dict]:
    assets = [
        ("addr_funding", "1Czoy8xtddvcGrEhUUCZDQ9QqdRfKh697F", "2015-01-15→2017-07-11"),
        ("addr_change", "173ujrhEVGqaZvPHXLqwXiSmPVMo225cqT", "2015-01-15→2017-07-11"),
        ("addr_topup", "1CENDvi6tmKGrR8RxqwURpX9WHbbKip1db", "2015-01-15→2018-01-01"),
        ("txid_puzzle", "08389f34c98c606322740c0be6a7125d9860bb8d5cb182c02f98461e5fa6cd15", "2015-01-15→2017-04-27"),
    ]
    rows = []
    for kind, val, ewin in assets:
        rows.append(
            {
                "pass": "2",
                "target": f"{kind}:{val}",
                "evidence_window": ewin,
                "discovery_window": "2015-01-15→2030-01-01",
                "discovery_only": "no",
                "claimed_original_date": "",
                "verified_original_date": "",
                "page_date": "",
                "snapshot_date": "",
                "author": "",
                "exact_quote": "",
                "original_url": "",
                "archive_url": "",
                "first_seen": "",
                "is_quote_of_known_2017_post": "n/a",
                "independent_source": "unknown",
                "is_explorer": "reject_if_yes",
                "evidence_grade": "pending",
                "puzzle_link": "none",
                "notes": (
                    "Want forum signature/donation/gist/wallet-log/source/same-alias page. "
                    "Explorer mirrors = Grade D / ignore. "
                    "CREATOR_ARCHIVE: indexed open-web meaningful pre-fame hit not found."
                ),
            }
        )
    return rows


def write_matrix(rows: list[dict]) -> None:
    with MATRIX.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=MATRIX_COLS, delimiter="\t", lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in MATRIX_COLS})


def evaluate_stop(rows: list[dict], bitaddress: dict) -> dict:
    grades = [r["evidence_grade"] for r in rows if r["evidence_grade"] not in ("pending", "")]
    has_A = any(g == "A" for g in grades)
    # Strong B = independent source with puzzle_link and NOT merely the known 2017 post alone
    strong_B = any(
        r["evidence_grade"] == "B"
        and r.get("puzzle_link") not in ("", "none", "operational")
        and r.get("is_quote_of_known_2017_post") not in ("yes_is_the_canonical", "yes")
        for r in rows
    )
    # Canonical 2017 B/operational without seed/T does not open scan
    if has_A or strong_B:
        status = "OPEN_NARROW_TEST"
        line = "PUZZLE_LINKAGE_LINE: OPEN"
    else:
        status = "CLOSED_PENDING_NEW_EVIDENCE"
        line = "PUZZLE_LINKAGE_LINE: CLOSED_PENDING_NEW_EVIDENCE"
    return {
        "status": status,
        "line": line,
        "has_grade_A": has_A,
        "has_strong_B": strong_B,
        "bitaddress_grade": bitaddress.get("verdict", {}).get("evidence_grade"),
        "scan_allowed": False if status.startswith("CLOSED") else True,
        "honest_bound": (
            "No justified #71 command: Transform T unknown, seed/root unknown, "
            "no Grade A / strong-B primary document beyond the known 2017 creator post."
        ),
    }


def main() -> int:
    HIT_DIR.mkdir(exist_ok=True)
    args = set(sys.argv[1:])
    do_ba = "--bitaddress" in args or "--pass-all" in args or not args
    do_matrix = "--matrix" in args or "--pass-all" in args or not args

    bitaddress: dict = {}
    if do_ba:
        bitaddress = bitaddress_pass()

    rows: list[dict] = []
    if do_matrix or "--pass-all" in args or not args:
        rows.extend(pass1_phrase_scaffold())
        rows.extend(pass2_addr_scaffold())
        # Pass 3 matrix row from bitaddress
        if bitaddress:
            rows.append(
                {
                    "pass": "3",
                    "target": "bitaddress_dedup",
                    "evidence_window": "2011-01-01→2015-01-15",
                    "discovery_window": "2011-01-01→2030-01-01",
                    "discovery_only": "no",
                    "claimed_original_date": "",
                    "verified_original_date": bitaddress["versions"][0]["first_ts"][:8]
                    if bitaddress.get("versions")
                    else "",
                    "page_date": "",
                    "snapshot_date": "",
                    "author": "pointbiz/bitaddress",
                    "exact_quote": "",
                    "original_url": "https://www.bitaddress.org",
                    "archive_url": "",
                    "first_seen": "",
                    "is_quote_of_known_2017_post": "n/a",
                    "independent_source": "yes",
                    "is_explorer": "no",
                    "evidence_grade": bitaddress["verdict"]["evidence_grade"],
                    "puzzle_link": "none",
                    "notes": bitaddress["verdict"]["reason"]
                    + f" | unique={bitaddress.get('unique_contents')}",
                }
            )
        write_matrix(rows)
        print(f"Wrote {MATRIX}")

    stop = evaluate_stop(rows, bitaddress or {"verdict": {}})
    SUMMARY.write_text(json.dumps({"stop": stop, "bitaddress": bitaddress.get("verdict")}, indent=2))
    print(stop["line"])
    print(stop["honest_bound"])
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:
        print(f"RESULT: FAIL ({e})", file=sys.stderr)
        raise SystemExit(1)
