#!/usr/bin/env python3
"""
Puzzle linkage probe — identity / phrase / addr / TXID / code-constant hunt.
Respects per-row not_before / not_after. Rejects explorer mirrors.
No seed/#71 grind.

Usage:
  python3 puzzle_linkage_probe.py --list
  python3 puzzle_linkage_probe.py --bitaddress-wild
  python3 puzzle_linkage_probe.py --cdx-url URL --not-before 2015-01-15 --not-after 2017-04-27
  python3 puzzle_linkage_probe.py --classify PATH   # grade a local hit file
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
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TSV_PATH = ROOT / "PUZZLE_LINKAGE_TARGETS.tsv"
HIT_DIR = ROOT / "linkage_hits"
UA = "puzzle71-linkage-probe/0.1 (windowed; reject explorers; no seed grind)"

COLUMNS = [
    "target_type",
    "search_value",
    "not_before",
    "not_after",
    "source",
    "archived_url",
    "snapshot_time",
    "author_or_alias",
    "exact_context",
    "creator_link",
    "generator_link",
    "mask_T_link",
    "evidence_grade",
    "notes",
]

EXPLORER_RE = re.compile(
    r"(blockchain\.info|blockchain\.com|mempool\.space|blockchair\.com|"
    r"btc\.com|blockstream\.info|sochain\.com|blockcypher\.com|"
    r"tradeblock\.com|smartbit\.com\.au|biteasy\.com)",
    re.I,
)


def ymd(s: str) -> str:
    return (s or "").replace("-", "")[:8]


def load_rows() -> list[dict[str, str]]:
    with TSV_PATH.open(newline="", encoding="utf-8") as f:
        return [{c: (r.get(c) or "").strip() for c in COLUMNS} for r in csv.DictReader(f, delimiter="\t")]


def save_rows(rows: list[dict[str, str]]) -> None:
    with TSV_PATH.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, delimiter="\t", lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in COLUMNS})


def in_window(ts: str, not_before: str, not_after: str) -> bool:
    d = ts[:8]
    nb, na = ymd(not_before), ymd(not_after)
    if nb and d < nb:
        return False
    if na and d > na:
        return False
    return True


def is_explorer(url: str) -> bool:
    return bool(EXPLORER_RE.search(url or ""))


def cdx_domain(
    host: str,
    not_before: str,
    not_after: str,
    limit: int = 5000,
) -> list[list[str]]:
    """Wayback domain crawl; use from/to YYYYMMDD (apex-only URL misses child paths)."""
    qs = urllib.parse.urlencode(
        {
            "url": host.replace("https://", "").replace("http://", "").strip("/"),
            "matchType": "domain",
            "from": ymd(not_before),
            "to": ymd(not_after),
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


def cdx_prefix(url: str, limit: int = 3000) -> list[list[str]]:
    host = url.replace("https://", "").replace("http://", "").split("/")[0]
    # Prefer domain match — apex URL alone under-reports bitaddress-style sites
    return cdx_domain(host, "1990-01-01", "2030-01-01", limit=limit)

def cdx_exact(url: str, limit: int = 500) -> list[list[str]]:
    qs = urllib.parse.urlencode(
        {
            "url": url,
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
    with urllib.request.urlopen(req, timeout=90) as resp:
        data = json.loads(resp.read().decode("utf-8", errors="replace"))
    return data[1:] if data and len(data) > 1 else []


def filter_window(entries: list[list[str]], not_before: str, not_after: str) -> list[list[str]]:
    out = []
    for e in entries:
        if not e or not in_window(e[0], not_before, not_after):
            continue
        if is_explorer(e[1]):
            continue
        out.append(e)
    return sorted(out, key=lambda x: x[0])


def list_targets(rows: list[dict[str, str]]) -> None:
    print("PUZZLE_LINKAGE_TARGETS — A/B reopen compute; C/D do not.\n")
    for r in rows:
        print(
            f"  [{r['evidence_grade']}] {r['target_type']}: {r['search_value'][:60]}"
        )
        print(f"       window {r['not_before']} → {r['not_after']}  source={r['source']}")
        if r["archived_url"]:
            print(f"       hit {r['snapshot_time']} {r['archived_url'][:70]}")
        print()


def bitaddress_wild(rows: list[dict[str, str]]) -> None:
    HIT_DIR.mkdir(exist_ok=True)
    nb, na = "2011-01-01", "2015-01-15"
    print(f"CDX matchType=domain bitaddress.org  window {nb}→{na}")
    try:
        entries = cdx_domain("bitaddress.org", nb, na)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
        print(f"  FAIL {e}")
        return
    win = filter_window(entries, nb, na)
    interesting = [
        e
        for e in win
        if any(e[1].lower().endswith(suf) for suf in (".js", ".html", ".zip", ".css"))
        or "/js/" in e[1].lower()
        or "bitaddress.org-" in e[1].lower()
    ]
    print(f"  cdx={len(entries)} in_window_non_explorer={len(win)} interesting={len(interesting)}")
    for e in interesting[:20]:
        print(f"    {e[0][:14]}  {e[1][:90]}")
    report = {
        "host": "bitaddress.org",
        "window": [nb, na],
        "cdx": len(entries),
        "in_window": len(win),
        "interesting": len(interesting),
        "samples": [{"ts": e[0], "url": e[1]} for e in interesting[:30]],
    }
    for r in rows:
        if r["target_type"] == "bitaddress_wild":
            if interesting:
                last = interesting[-1]
                r["archived_url"] = f"https://web.archive.org/web/{last[0]}/{last[1]}"
                r["snapshot_time"] = last[0]
                r["notes"] = (
                    f"domain CDX in_window={len(win)} interesting={len(interesting)}; "
                    f"last={last[1][:70]}"
                )
            r["evidence_grade"] = "D"
            r["source"] = "wayback-domain"
    save_rows(rows)
    (HIT_DIR / "bitaddress_wild_summary.json").write_text(json.dumps(report, indent=2))
    print(f"Wrote summary → {HIT_DIR / 'bitaddress_wild_summary.json'}")


def cdx_one(url: str, not_before: str, not_after: str) -> None:
    print(f"CDX {url} window {not_before}→{not_after}")
    if ymd(not_after) and ymd(not_before) and ymd(not_after) < ymd(not_before):
        print("ERROR: not_after < not_before")
        return
    # Guard: puzzle txid must not use pre-2015 window
    if "08389f34" in url and ymd(not_before) < "20150115":
        print("REFUSE: puzzle TXID window must start ≥2015-01-15")
        return
    try:
        entries = cdx_exact(url) if "*" not in url else cdx_prefix(url)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
        print(f"FAIL {e}")
        return
    win = filter_window(entries, not_before, not_after)
    explorers = sum(1 for e in entries if e and is_explorer(e[1]) and in_window(e[0], not_before, not_after))
    print(f"  raw={len(entries)} in_window_non_explorer={len(win)} explorer_rejected={explorers}")
    for e in win[:20]:
        print(f"    {e[0]}  {e[1][:90]}")


def classify_text(path: Path) -> None:
    text = path.read_text(errors="replace")
    low = text.lower()
    grade = "D"
    reasons = []
    if is_explorer(text[:2000]):
        reasons.append("explorer-like")
    phrases = [
        "consecutive keys from a deterministic wallet",
        "masked with leading",
        "crude measuring instrument",
        "cracking strength of the community",
        "saatoshi_rising",
    ]
    for p in phrases:
        if p.lower() in low:
            reasons.append(f"phrase:{p[:40]}")
            grade = "B"
    if "08389f34c98c606322740c0be6a7125d9860bb8d5cb182c02f98461e5fa6cd15" in low:
        reasons.append("puzzle_txid")
        if grade == "D":
            grade = "C"
    if re.search(r"256\s*outputs|100000\s*sat", low):
        reasons.append("code_const")
        if grade in ("D", "C"):
            grade = "B"
    print(f"file={path.name} provisional_grade={grade} reasons={reasons}")
    print("NOTE: human must confirm author_or_alias + dates before A/B promotion")


def main() -> int:
    args = sys.argv[1:]
    rows = load_rows()
    if not args or "--list" in args:
        list_targets(rows)
        if not args:
            print("RESULT: PASS")
            return 0
    if "--bitaddress-wild" in args:
        bitaddress_wild(rows)
    if "--cdx-url" in args:
        i = args.index("--cdx-url")
        url = args[i + 1]
        nb = args[args.index("--not-before") + 1] if "--not-before" in args else "2015-01-15"
        na = args[args.index("--not-after") + 1] if "--not-after" in args else "2017-04-27"
        cdx_one(url, nb, na)
    if "--classify" in args:
        classify_text(Path(args[args.index("--classify") + 1]))
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:
        print(f"RESULT: FAIL ({e})", file=sys.stderr)
        raise SystemExit(1)
