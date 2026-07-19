#!/usr/bin/env python3
"""
Casascius BAU formula lock — published 2011 test vector ONLY.
No passphrase search. Exit 0 on match, 1 on failure.
"""
from __future__ import annotations

import hashlib
import sys

import base58

PUBLISHED_PASSPHRASE = (
    b"Sample passphrase that should not be used for any real Bitcoin money transactions."
)
PUBLISHED_WIF_1 = "5JwH8jmznh4RbyMBYXMwzPL45pnr8FW9TtwunSKfTz1ibyao8Ym"
PUBLISHED_PRIV_HEX_1 = (
    "9392ac4225ccee1814c5e0958778dd5d2eeaf44cd2936bf15d632e7dbbf0a3f7"
)


def sha256(b: bytes) -> bytes:
    return hashlib.sha256(b).digest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _require_casascius_index(i: int) -> None:
    if i < 1:
        raise ValueError("Casascius BAU indexing starts at 1")


def casascius_c1(passphrase: bytes, i: int) -> bytes:
    """GenerationFormula == 1 (UI default): SHA256(passphrase || decimal(i))."""
    _require_casascius_index(i)
    return sha256(passphrase + str(i).encode("ascii"))


def casascius_c2(passphrase: bytes, i: int) -> bytes:
    """GenerationFormula == 0: SHA256(i/passphrase/i/BITCOIN)."""
    _require_casascius_index(i)
    d = str(i).encode("ascii")
    return sha256(d + b"/" + passphrase + b"/" + d + b"/BITCOIN")


def wif_uncompressed(priv32: bytes) -> str:
    return base58.b58encode_check(b"\x80" + priv32).decode()


def main() -> int:
    c1 = casascius_c1(PUBLISHED_PASSPHRASE, 1)
    c2 = casascius_c2(PUBLISHED_PASSPHRASE, 1)

    require(
        c2.hex() == PUBLISHED_PRIV_HEX_1,
        "C2 private-key vector mismatch",
    )
    require(
        casascius_c2(PUBLISHED_PASSPHRASE[:-1], 1).hex() != PUBLISHED_PRIV_HEX_1,
        "Trailing-period negative test failed",
    )
    require(c1 != c2, "C1 and C2 unexpectedly produced the same key")

    w1 = wif_uncompressed(c1)
    w2 = wif_uncompressed(c2)

    require(w2 == PUBLISHED_WIF_1, "Published C2 WIF mismatch")
    require(w1 != PUBLISHED_WIF_1, "C1 unexpectedly matches published WIF")

    print("Casascius BAU vector self-test")
    print(f"  C1 WIF: {w1}")
    print("  C1 match published: False")
    print(f"  C2 WIF: {w2}")
    print("  C2 match published: True")
    print("  C2 priv hex match: True")
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as e:
        print(f"RESULT: FAIL ({e})", file=sys.stderr)
        raise SystemExit(1)
