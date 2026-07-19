#!/usr/bin/env python3
"""
Electrum 1.x (pre-BIP32) formula lock — published throwaway vectors ONLY.
No Puzzle #71 search. Exit 0 on match.

Vectors: bip_utils tests (comment: verified with official Electrum wallet)
  https://github.com/ebellocchia/bip_utils/blob/master/tests/electrum/
Formula mirror: spesmilo/electrum electrum/keystore.py Old_KeyStore
"""
from __future__ import annotations

import hashlib
import sys

import base58
from coincurve import PrivateKey

# --- Vector A: entropy → 100k stretch → master seed + first receiving address ---
# Source: tests/electrum/mnemonic/test_electrum_v1_mnemonic.py
STRETCH_VECTORS = [
    {
        "entropy_hex": "00000000000000000000000000000000",
        "seed_hex": "7c2548ab89ffea8a6579931611969ffc0ed580ccf6048d4230762b981195abe5",
        "address0": "1FHsTashEBUNPQwC1CwVjnKUxzwgw73pU4",
    },
    {
        "entropy_hex": "e6914a31dc45fe52a979acde7128cfb4",
        "seed_hex": "151d19768f1c2bc0986c276975996bb8e63e0c5bc7779fffe381ec93a10da5ed",
        "address0": "1KxCSrMZLH2haDyaZ6VjfgmCx7od6voX8u",
    },
]

# --- Vector B: stretched master → first 5 receiving addresses ---
# Source: tests/electrum/test_electrum_v1.py
ADDR5_VECTOR = {
    "master_hex": "0bbe2537d7527f2d7376d4bb9de8ac42ca202dbae310471b88f2cbb0492e6e73",
    "master_wif": "5HuTXx6TC56nonxHfw3DmM72CurZ22zh24azdCmz3gh3We2Ujvk",
    "addresses": [
        "1P5Ai2wW2x93onQW5ZSDfHhu5LTgBPNx7r",
        "1dGnYwstcGq5fsEkSkV3jpgbfKQf2wgR1",
        "1CcNXYJW7DEtqLECPQGoTr8mhZEC7X9i8X",
        "12Gq5N1tDRUx7Tn7nEgHunazoAcDK1p6sw",
        "1L828t7SY3qzpKf3u3LfNNVvUHKtcQxBk8",
    ],
}

N_ORDER = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
STRETCH_ROUNDS = 100_000


def require(cond: bool, msg: str) -> None:
    if not cond:
        raise RuntimeError(msg)


def sha256(b: bytes) -> bytes:
    return hashlib.sha256(b).digest()


def sha256d(b: bytes) -> bytes:
    return sha256(sha256(b))


def electrum_stretch(hex_seed: str) -> bytes:
    """Old_KeyStore.stretch_key — hex_seed is ASCII hex string (typically 32 chars)."""
    encoded = hex_seed.encode("ascii")
    x = encoded
    for _ in range(STRETCH_ROUNDS):
        x = sha256(x + encoded)
    return x


def mpk_hex_from_master(master32: bytes) -> str:
    """Uncompressed pubkey without 04 prefix (Electrum mpk storage)."""
    pub = PrivateKey(master32).public_key.format(compressed=False)
    require(pub[0] == 0x04 and len(pub) == 65, "expected uncompressed pubkey")
    return pub[1:].hex()


def get_sequence(mpk_hex: str, for_change: int, n: int) -> int:
    """Old_KeyStore.get_sequence: SHA256d( f\"{n}:{for_change}:\" || mpk_bytes )."""
    msg = f"{n}:{for_change}:".encode("ascii") + bytes.fromhex(mpk_hex)
    return int.from_bytes(sha256d(msg), "big")


def child_priv(master32: bytes, for_change: int, n: int) -> bytes:
    mpk = mpk_hex_from_master(master32)
    secexp = (int.from_bytes(master32, "big") + get_sequence(mpk, for_change, n)) % N_ORDER
    if secexp == 0:
        secexp = 1
    return secexp.to_bytes(32, "big")


def addr_uncompressed(priv32: bytes) -> str:
    pub = PrivateKey(priv32).public_key.format(compressed=False)
    h160 = hashlib.new("ripemd160", sha256(pub)).digest()
    return base58.b58encode_check(b"\x00" + h160).decode()


def wif_uncompressed(priv32: bytes) -> str:
    return base58.b58encode_check(b"\x80" + priv32).decode()


def main() -> int:
    print("Electrum v1 vector self-test")
    print(f"  stretch rounds: {STRETCH_ROUNDS}")
    print("  index: receiving n=0..4, for_change=0 (0-based)")
    print("  addresses: uncompressed P2PKH")

    for i, v in enumerate(STRETCH_VECTORS):
        stretched = electrum_stretch(v["entropy_hex"])
        require(
            stretched.hex() == v["seed_hex"],
            f"stretch mismatch vector[{i}]",
        )
        a0 = addr_uncompressed(child_priv(stretched, 0, 0))
        require(a0 == v["address0"], f"address0 mismatch vector[{i}]: {a0}")
        print(f"  stretch[{i}] OK → {v['address0']}")

    master = bytes.fromhex(ADDR5_VECTOR["master_hex"])
    require(
        wif_uncompressed(master) == ADDR5_VECTOR["master_wif"],
        "master WIF mismatch",
    )
    for n, expect in enumerate(ADDR5_VECTOR["addresses"]):
        got = addr_uncompressed(child_priv(master, 0, n))
        require(got == expect, f"addr[{n}] got {got} want {expect}")
        print(f"  addr[{n}] OK → {expect}")

    # change chain smoke: different from receiving for same n
    c0 = addr_uncompressed(child_priv(master, 1, 0))
    require(c0 != ADDR5_VECTOR["addresses"][0], "change==receiving unexpectedly")
    print(f"  change[0] distinct OK → {c0}")

    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as e:
        print(f"RESULT: FAIL ({e})", file=sys.stderr)
        raise SystemExit(1)
