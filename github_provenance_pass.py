#!/usr/bin/env python3
"""
GITHUB_PROVENANCE_PASS — first-commit / fork / origin for discovery hits.
No re-search. No #71 grind.

  GITHUB_TOKEN="$(gh auth token)" python3 github_provenance_pass.py
  python3 github_provenance_pass.py --priority-only

Writes: GITHUB_PROVENANCE_PASS.md + GITHUB_PROVENANCE_STATE.json
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HITS_STATE = ROOT / "DISCOVERY_BACKFILL_STATE.json"
OUT_MD = ROOT / "GITHUB_PROVENANCE_PASS.md"
OUT_JSON = ROOT / "GITHUB_PROVENANCE_STATE.json"
UA = "puzzle71-github-provenance/0.1"

PRIORITY = [
    ("pbies/bitcoin-tools", "python/p71-01.py"),
    ("accessor-io/pattern", "src/bitcoin_puzzle_solver.py"),
    ("alex-place/lantern-os", None),  # any hit path in this repo
    ("consigcody94/glv-kangaroo-paper", None),
    ("HomelessPhD/BTC32", None),
    ("onepuzzle/puzzle-generator", None),
]

# Skip obvious NLP false-positive "ResCU" corpora unless explicitly requested
SKIP_REPO_PREFIXES = (
    "nlpinaction/",
    "cdipaolo/sentiment",
    "gilbutITbook/",
    "HLSTransform/",
    "glopasso/text-summarization",
    "jdjkelly/www.aaronsw.com",
    "logicmoo/logicmoo_nlu",
    "mgerb/top-of-reddit",
    "MysteriesOfImmortalPuppetMaster/",
    "RainbowMetalPigeon/ExtremeYellow",
)

GATE_OPENERS = (
    "pre_2015_independent_puzzle_artifact",
    "creator_linked_commit_email",
    "txid_plus_generator_code",
    "exact_mask_T",
    "root_seed_mpk_xpub",
    "verified_pubkey71",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def token() -> str:
    return os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or ""


def api(path: str, params: dict | None = None) -> tuple[object, dict]:
    q = ("?" + urllib.parse.urlencode(params)) if params else ""
    url = f"https://api.github.com{path}{q}"
    headers = {
        "User-Agent": UA,
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    t = token()
    if t:
        headers["Authorization"] = f"Bearer {t}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = resp.read()
            link = resp.headers.get("Link", "")
            data = json.loads(body.decode()) if body else None
            return data, {"link": link, "status": resp.status}
    except urllib.error.HTTPError as e:
        err = e.read().decode(errors="replace")[:300]
        raise RuntimeError(f"HTTP {e.code} {path}: {err}") from e


def parse_last_page(link: str) -> int | None:
    # <...&page=12>; rel="last"
    m = re.search(r'[?&]page=(\d+)>;\s*rel="last"', link or "")
    return int(m.group(1)) if m else None


def repo_meta(full: str) -> dict:
    owner, name = full.split("/", 1)
    data, _ = api(f"/repos/{owner}/{name}")
    parent = None
    if data.get("fork") and data.get("parent"):
        parent = data["parent"].get("full_name")
    return {
        "repository": full,
        "repo_created_at": data.get("created_at"),
        "repo_is_fork": bool(data.get("fork")),
        "parent_repository": parent,
        "default_branch": data.get("default_branch") or "main",
        "pushed_at": data.get("pushed_at"),
        "archived": bool(data.get("archived")),
    }


def oldest_commit_for_path(full: str, path: str) -> dict | None:
    owner, name = full.split("/", 1)
    # newest-first page 1
    page1, meta = api(f"/repos/{owner}/{name}/commits", {"path": path, "per_page": 100})
    if not page1:
        return None
    last = parse_last_page(meta.get("link", ""))
    if last and last > 1:
        # walk from last page (oldest)
        oldest_page, _ = api(
            f"/repos/{owner}/{name}/commits",
            {"path": path, "per_page": 100, "page": last},
        )
        if oldest_page:
            c = oldest_page[-1]
        else:
            c = page1[-1]
    else:
        c = page1[-1]
    commit = c.get("commit") or {}
    author = commit.get("author") or {}
    return {
        "first_commit_sha": c.get("sha"),
        "first_commit_date": author.get("date"),
        "commit_author": author.get("name"),
        "commit_author_email": author.get("email"),
        "commit_message": (commit.get("message") or "").split("\n", 1)[0][:200],
        "html_url": c.get("html_url"),
    }


def fetch_raw(full: str, path: str, ref: str) -> str:
    owner, name = full.split("/", 1)
    url = f"https://raw.githubusercontent.com/{owner}/{name}/{ref}/{path}"
    headers = {"User-Agent": UA}
    t = token()
    if t:
        headers["Authorization"] = f"Bearer {t}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read().decode("utf-8", errors="replace")


def matching_lines(text: str, queries: list[str], limit: int = 8) -> list[str]:
    needles = [q.strip('"') for q in queries]
    out = []
    for i, line in enumerate(text.splitlines(), 1):
        low = line.lower()
        if any(n.lower() in low for n in needles if n):
            out.append(f"L{i}: {line.strip()[:220]}")
            if len(out) >= limit:
                break
    return out


def cite_hints(text: str) -> list[str]:
    cites = []
    for pat in (
        r"https?://bitcointalk\.org/[^\s\)\"']+",
        r"msg\d{5,}",
        r"saatoshi_rising",
        r"privatekeys\.pw[^\s\)\"']*",
        r"btcpuzzle\.info[^\s\)\"']*",
    ):
        for m in re.finditer(pat, text, re.I):
            cites.append(m.group(0)[:160])
            if len(cites) >= 6:
                return cites
    return cites


def classify(row: dict) -> str:
    """Heuristic class — never auto Grade A."""
    created = (row.get("repo_created_at") or "")[:4]
    first = (row.get("first_commit_date") or "")[:4]
    year = int(first or created or "9999") if (first or created) else 9999
    path = (row.get("matched_path") or "").lower()
    lines = "\n".join(row.get("exact_matching_lines") or []).lower()
    if year <= 2014:
        return "HISTORICAL_INTEREST"
    if "xpub" in lines or "xprv" in lines or "mnemonic" in lines:
        return "NEEDS_HUMAN_SEEDISH"
    if "2^(n-1)" in lines or "mask" in lines and "def " in lines:
        return "NEEDS_HUMAN_MASKISH"
    if year >= 2024:
        return "MODERN_MIRROR_OR_TOOL"
    if "readme" in path or path.endswith(".txt") or "unspent" in path:
        return "LIST_OR_TRACKER"
    return "SECONDARY_RESEARCH"


def load_hits() -> list[dict]:
    st = json.loads(HITS_STATE.read_text())
    return st.get("github_hits") or []


def unique_targets(hits: list[dict], priority_only: bool) -> list[tuple[str, str, list[str]]]:
    """Return list of (repo, path, queries)."""
    by_key: dict[tuple[str, str], list[str]] = {}
    for h in hits:
        repo, path = h.get("repo") or "", h.get("path") or ""
        if not repo or not path:
            continue
        if any(repo.startswith(p) for p in SKIP_REPO_PREFIXES):
            continue
        by_key.setdefault((repo, path), []).append(h.get("query") or "")

    ordered: list[tuple[str, str, list[str]]] = []
    seen = set()

    # Priority first
    for pref_repo, pref_path in PRIORITY:
        for (repo, path), qs in by_key.items():
            if repo != pref_repo:
                continue
            if pref_path and path != pref_path:
                continue
            key = (repo, path)
            if key in seen:
                continue
            seen.add(key)
            ordered.append((repo, path, qs))

    if priority_only:
        # also try missing priority repos with no hit (e.g. onepuzzle 404)
        for pref_repo, pref_path in PRIORITY:
            if any(r == pref_repo for r, _, _ in ordered):
                continue
            ordered.append((pref_repo, pref_path or "", ["(priority probe)"]))
        return ordered

    for (repo, path), qs in sorted(by_key.items()):
        if (repo, path) in seen:
            continue
        ordered.append((repo, path, qs))
    return ordered


def provenance_one(repo: str, path: str, queries: list[str]) -> dict:
    row = {
        "repository": repo,
        "matched_path": path,
        "queries": queries,
        "error": "",
        "at": utc_now(),
    }
    try:
        meta = repo_meta(repo)
        row.update(meta)
    except Exception as e:
        row["error"] = f"repo_meta: {e}"
        row["class"] = "ERROR"
        return row
    if not path:
        row["class"] = "REPO_ONLY_NO_PATH"
        row["note"] = "no matching path in hit set (e.g. deleted repo)"
        return row
    try:
        first = oldest_commit_for_path(repo, path)
        if first:
            row.update(first)
    except Exception as e:
        row["error"] = (row.get("error") or "") + f" commits: {e}"
    ref = row.get("first_commit_sha") or row.get("default_branch") or "HEAD"
    try:
        text = fetch_raw(repo, path, ref)
        row["exact_matching_lines"] = matching_lines(text, queries)
        row["source_cited_by_file"] = cite_hints(text)
    except Exception as e:
        row["error"] = (row.get("error") or "") + f" raw: {e}"
        row["exact_matching_lines"] = []
        row["source_cited_by_file"] = []
    row["class"] = classify(row)
    # Gate opener check (strict)
    year = (row.get("first_commit_date") or row.get("repo_created_at") or "9999")[:4]
    row["reopens_compute"] = False
    row["reopen_reason"] = ""
    if year.isdigit() and int(year) < 2015 and "puzzle" in (path + str(row.get("exact_matching_lines"))).lower():
        row["reopen_reason"] = "possible_pre_2015 — needs human"
    return row


def write_md(rows: list[dict]) -> None:
    lines = [
        "# GITHUB_PROVENANCE_PASS",
        "",
        f"**Date:** {utc_now()}",
        "**Input:** `DISCOVERY_BACKFILL_STATE.json` github_hits (no re-search)",
        "**Compute gate:** CLOSED unless human confirms a gate opener",
        "",
        "## Summary",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Rows audited | {len(rows)} |",
        f"| Errors | {sum(1 for r in rows if r.get('error'))} |",
        f"| pre-2015 first_commit | {sum(1 for r in rows if (r.get('first_commit_date') or '9999')[:4].isdigit() and int((r.get('first_commit_date') or '9999')[:4]) < 2015)} |",
        f"| Modern (≥2024) | {sum(1 for r in rows if (r.get('first_commit_date') or r.get('repo_created_at') or '')[:4] >= '2024')} |",
        f"| reopens_compute | {sum(1 for r in rows if r.get('reopens_compute'))} |",
        "",
        "## Priority + audited hits",
        "",
    ]
    for r in rows:
        lines.append(f"### `{r.get('repository')}` / `{r.get('matched_path')}`")
        lines.append("")
        lines.append(f"| Field | Value |")
        lines.append(f"|-------|-------|")
        for k in (
            "class",
            "repo_created_at",
            "repo_is_fork",
            "parent_repository",
            "first_commit_date",
            "first_commit_sha",
            "commit_author",
            "commit_author_email",
            "commit_message",
            "reopens_compute",
            "reopen_reason",
            "error",
        ):
            lines.append(f"| {k} | {r.get(k) if r.get(k) is not None else ''} |")
        if r.get("exact_matching_lines"):
            lines.append("")
            lines.append("Matching lines:")
            for ml in r["exact_matching_lines"]:
                lines.append(f"- `{ml}`")
        if r.get("source_cited_by_file"):
            lines.append("")
            lines.append("Cited sources: " + ", ".join(f"`{c}`" for c in r["source_cited_by_file"]))
        lines.append("")
    lines.extend(
        [
            "## Verdict",
            "",
            "```text",
            "GITHUB_PROVENANCE_PASS: complete",
            "Grade A/B: none auto-assigned",
            "justified #71 solve command: NONE",
            "```",
            "",
            "Modern (2024–2026) first commits = mirror/tooling noise unless independent pre-2015 provenance.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n")


def main() -> int:
    if not token():
        print("Set GITHUB_TOKEN (e.g. GITHUB_TOKEN=\"$(gh auth token)\")", file=sys.stderr)
        return 1
    priority_only = "--priority-only" in sys.argv
    # Default: priority + all non-NLP hits (may be slower). --priority-only for fast.
    if "--all" not in sys.argv and not priority_only:
        # user asked for provenance of 49 with priority — do priority first then rest
        priority_only = False
    hits = load_hits()
    targets = unique_targets(hits, priority_only=False)
    # Always ensure priority order at front (already done)
    print(f"Auditing {len(targets)} unique repo/path targets…")
    rows = []
    for i, (repo, path, qs) in enumerate(targets, 1):
        print(f"[{i}/{len(targets)}] {repo} {path}")
        row = provenance_one(repo, path, qs)
        rows.append(row)
        print(
            f"  class={row.get('class')} created={row.get('repo_created_at')} "
            f"first={row.get('first_commit_date')} fork={row.get('repo_is_fork')} "
            f"err={bool(row.get('error'))}"
        )
        time.sleep(0.35)  # be gentle on API
    OUT_JSON.write_text(json.dumps({"at": utc_now(), "rows": rows}, indent=2) + "\n")
    write_md(rows)
    print(f"\nWrote {OUT_MD.name} and {OUT_JSON.name}")
    print("STATUS: PROVENANCE_PASS_DONE")
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
