#!/usr/bin/env python3
"""
Archive inventory probe — respects not_before / not_after per row.
Prefers raw/tarball over GitHub HTML. No #71 seed scan.

Usage:
  python3 archive_index_probe.py --list-priority
  python3 archive_index_probe.py                 # CDX fill URL rows in their windows
  python3 archive_index_probe.py --download      # fetch last-in-window body + sha256
"""
from __future__ import annotations

import csv
import hashlib
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TSV_PATH = ROOT / "ARCHIVE_TARGETS.tsv"
ART_DIR = ROOT / "archive_artifacts"
UA = "puzzle71-archive-probe/0.2 (research; windowed; no seed grind)"

COLUMNS = [
    "family",
    "search_term",
    "original_url",
    "not_before",
    "not_after",
    "archive_url",
    "first_in_window",
    "last_in_window",
    "artifact_name",
    "artifact_sha256",
    "source_commit",
    "source_date",
    "mime_type",
    "is_source_code",
    "is_primary_source",
    "exact_formula_found",
    "test_vector_found",
    "puzzle_link",
    "evidence_grade",
    "notes",
]


def ymd(s: str) -> str:
    """Normalize YYYY-MM-DD or YYYYMMDD… → YYYYMMDD."""
    s = (s or "").strip()
    if not s:
        return ""
    return s.replace("-", "")[:8]


def load_rows() -> list[dict[str, str]]:
    with TSV_PATH.open(newline="", encoding="utf-8") as f:
        return [{c: (r.get(c) or "").strip() for c in COLUMNS} for r in csv.DictReader(f, delimiter="\t")]


def save_rows(rows: list[dict[str, str]]) -> None:
    with TSV_PATH.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, delimiter="\t", lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in COLUMNS})


def cdx_query(url: str, limit: int = 2000) -> list[list[str]]:
    qs = urllib.parse.urlencode(
        {
            "url": url,
            "matchType": "prefix" if url.rstrip("/").endswith("*") or "/*" in url else "exact",
            "output": "json",
            "fl": "timestamp,original,statuscode,mimetype,digest,length",
            "filter": "statuscode:200",
            "limit": str(limit),
        }
    )
    # normalize wildcard for CDX: bitaddress.org/* → url=bitaddress.org/* matchType=prefix
    req = urllib.request.Request(
        f"https://web.archive.org/cdx/search/cdx?{qs}",
        headers={"User-Agent": UA},
    )
    with urllib.request.urlopen(req, timeout=90) as resp:
        data = json.loads(resp.read().decode("utf-8", errors="replace"))
    return data[1:] if data and len(data) > 1 else []


def in_window(ts: str, not_before: str, not_after: str) -> bool:
    d = ts[:8]
    nb, na = ymd(not_before), ymd(not_after)
    if nb and d < nb:
        return False
    if na and d > na:
        return False
    return True


def pick_window(entries: list[list[str]], not_before: str, not_after: str) -> tuple[str, str, str, str]:
    """first_in_window, last_in_window, archive_url, mimetype."""
    win = [e for e in entries if e and in_window(e[0], not_before, not_after)]
    if not win:
        return "", "", "", ""
    win.sort(key=lambda e: e[0])
    first, last = win[0], win[-1]
    archive = f"https://web.archive.org/web/{last[0]}/{last[1]}"
    mime = last[3] if len(last) > 3 else ""
    return first[0], last[0], archive, mime


def download_artifact(archive_url: str, family: str) -> tuple[str, str, str]:
    ART_DIR.mkdir(exist_ok=True)
    req = urllib.request.Request(archive_url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as resp:
        body = resp.read()
        ctype = resp.headers.get("Content-Type", "application/octet-stream").split(";")[0].strip()
    ext = {
        "text/html": ".html",
        "text/plain": ".txt",
        "application/javascript": ".js",
        "application/zip": ".zip",
        "application/gzip": ".tar.gz",
        "application/x-gzip": ".tar.gz",
    }.get(ctype, ".bin")
    digest = hashlib.sha256(body).hexdigest()
    # dedupe by sha256
    for existing in ART_DIR.iterdir():
        if existing.is_file() and hashlib.sha256(existing.read_bytes()).hexdigest() == digest:
            return existing.name, digest, ctype
    name = f"{family}_{digest[:12]}{ext}"
    (ART_DIR / name).write_bytes(body)
    return name, digest, ctype


def list_priority(rows: list[dict[str, str]]) -> None:
    print("ARCHIVE_TARGETS (windowed). Evidence C/D only unless puzzle_link set.\n")
    for r in rows:
        print(
            f"  [{r['evidence_grade'] or '?'}] {r['family']}  "
            f"window={r['not_before']}→{r['not_after']}"
        )
        print(f"       {r['search_term'][:70]}")
        print(f"       url={r['original_url'] or '(search-only)'}")
        print(f"       in_window last={r['last_in_window'] or '—'}\n")


def fill_cdx(rows: list[dict[str, str]], family_filter: str | None, do_download: bool) -> None:
    for r in rows:
        if family_filter and r["family"] != family_filter:
            continue
        url = r["original_url"]
        if not url or url == "pending":
            print(f"skip (no url): {r['family']}")
            continue
        print(f"CDX {r['family']} window {r['not_before']}→{r['not_after']}: {url}")
        try:
            # CDX: strip trailing /* for matchType handling
            qurl = url.replace("/*", "/") if url.endswith("/*") else url
            if url.endswith("/*") or "*" in url:
                qurl = url.rstrip("*").rstrip("/")
                entries = cdx_query(qurl + "/*")  # may still need matchType
                # fallback prefix
                if not entries:
                    qs = urllib.parse.urlencode(
                        {
                            "url": qurl + "/*",
                            "matchType": "prefix",
                            "output": "json",
                            "fl": "timestamp,original,statuscode,mimetype,digest,length",
                            "filter": "statuscode:200",
                            "limit": "2000",
                        }
                    )
                    req = urllib.request.Request(
                        f"https://web.archive.org/cdx/search/cdx?{qs}",
                        headers={"User-Agent": UA},
                    )
                    with urllib.request.urlopen(req, timeout=90) as resp:
                        data = json.loads(resp.read().decode())
                    entries = data[1:] if data and len(data) > 1 else []
            else:
                entries = cdx_query(url)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            print(f"  FAIL: {e}")
            continue
        first, last, archive, mime = pick_window(entries, r["not_before"], r["not_after"])
        r["first_in_window"] = first
        r["last_in_window"] = last
        if archive:
            r["archive_url"] = archive
        if mime:
            r["mime_type"] = mime
        print(f"  total_cdx={len(entries)} in_window last={last or '—'}")
        if do_download and archive and not r["artifact_sha256"]:
            try:
                name, digest, ctype = download_artifact(archive, r["family"])
                r["artifact_name"] = name
                r["artifact_sha256"] = digest
                r["mime_type"] = ctype
                r["source_date"] = last[:8] if last else ""
                r["is_source_code"] = "yes" if any(
                    x in ctype for x in ("javascript", "python", "zip", "gzip", "plain")
                ) else "no"
                r["is_primary_source"] = "no" if "html" in ctype else r.get("is_primary_source") or "yes"
                print(f"  saved {name} sha256={digest[:16]}…")
            except (urllib.error.URLError, TimeoutError) as e:
                print(f"  download FAIL: {e}")


def main() -> int:
    args = sys.argv[1:]
    rows = load_rows()
    if "--list-priority" in args or "--list" in args:
        list_priority(rows)
        return 0
    family_filter = None
    if "--family" in args:
        family_filter = args[args.index("--family") + 1]
    do_download = "--download" in args
    print(f"rows={len(rows)} download={do_download}")
    fill_cdx(rows, family_filter, do_download)
    save_rows(rows)
    print(f"Wrote {TSV_PATH}")
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:
        print(f"RESULT: FAIL ({e})", file=sys.stderr)
        raise SystemExit(1)
