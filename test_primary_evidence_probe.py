#!/usr/bin/env python3
"""Tests for primary_evidence_probe grading/baseline/hash stability."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import primary_evidence_probe as pep

FIX = ROOT / "testdata" / "primary_evidence"


class PrimaryEvidenceProbeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.targets = pep.load_targets()

    def _grade_file(self, name: str, url: str) -> dict:
        body = (FIX / name).read_bytes()
        return pep.grade_candidate(body, url, f"fixture:{name}", self.targets)

    def test_baseline_2017_reject(self) -> None:
        r = self._grade_file(
            "baseline_2017.html",
            "https://bitcointalk.org/index.php?topic=1306983.msg18687273#msg18687273",
        )
        self.assertEqual(r["auto_status"], "REJECT_BASELINE")
        self.assertEqual(r["post_id"], "18687273")
        self.assertEqual(r["author"].lower(), "saatoshi_rising")
        self.assertTrue(r["published_at"])

    def test_same_thread_different_post_manual_g4(self) -> None:
        r = self._grade_file(
            "same_thread_new_post.html",
            "https://bitcointalk.org/index.php?topic=1306983.msg99999888#msg99999888",
        )
        # Must NOT be REJECT_BASELINE just because topic=1306983
        self.assertNotEqual(r["auto_status"], "REJECT_BASELINE")
        self.assertEqual(r["auto_status"], "MANUAL_REVIEW_G4")
        self.assertEqual(r["post_id"], "99999888")
        self.assertEqual(r["grade"], "pending")

    def test_article_citing_explorer_not_reject_explorer(self) -> None:
        r = self._grade_file(
            "article_cites_explorer.html",
            "https://example.com/research-note.html",
        )
        self.assertNotEqual(r["auto_status"], "REJECT")
        self.assertNotEqual(r["reason"], "source_is_explorer_host")
        # may be KEYWORD_HIT due to txid target
        self.assertIn(r["auto_status"], ("KEYWORD_HIT", "MANUAL_REVIEW_G5", "MANUAL_REVIEW_G3"))

    def test_fake_seed_puzzle_keyword_hit(self) -> None:
        r = self._grade_file("fake_seed_puzzle.html", "https://bitcointalk.org/index.php?topic=1.0")
        self.assertEqual(r["auto_status"], "KEYWORD_HIT")
        self.assertEqual(r["grade"], "pending")

    def test_mask_t_plus_txid_manual_review(self) -> None:
        r = self._grade_file("mask_t_plus_txid.py.txt", "fixture://mask_t_plus_txid.py.txt")
        self.assertIn(r["auto_status"], ("MANUAL_REVIEW_G3", "MANUAL_REVIEW_G5"))
        self.assertTrue(r["matched_targets"] or r["gate"] in ("G3", "G5"))

    def test_normalized_hash_stable_across_ads(self) -> None:
        a = self._grade_file("page_v1.html", "https://example.com/a")
        b = self._grade_file("page_v2_ads_changed.html", "https://example.com/b")
        self.assertNotEqual(a["raw_sha256"], b["raw_sha256"])
        self.assertEqual(a["normalized_content_sha256"], b["normalized_content_sha256"])
        # simulate state dedupe
        state = pep.load_state()
        state["seen_candidates"] = {}
        r1 = pep.ingest_bytes(
            (FIX / "page_v1.html").read_bytes(),
            "https://example.com/a",
            "t1",
            state,
            self.targets,
        )
        r2 = pep.ingest_bytes(
            (FIX / "page_v2_ads_changed.html").read_bytes(),
            "https://example.com/b",
            "t2",
            state,
            self.targets,
        )
        self.assertTrue(r1["is_new"])
        self.assertFalse(r2["is_new"])

    def test_tsv_targets_attached(self) -> None:
        r = self._grade_file(
            "baseline_2017.html",
            "https://bitcointalk.org/index.php?topic=1306983.msg18687273#msg18687273",
        )
        self.assertTrue(any("saatoshi" in t.lower() or "consecutive" in t.lower() for t in r["matched_targets"]))


if __name__ == "__main__":
    unittest.main()
