#!/usr/bin/env python3
"""
Synthetic Puzzle Lab — controlled generator → T → compressed P2PKH → recovery.

NOT Bitcoin Puzzle #71. Throwaway roots only. Proves tooling end-to-end.

  python3 synthetic_puzzle_lab.py           # n=1..32 quick
  python3 synthetic_puzzle_lab.py --full    # n=1..256
"""
from __future__ import annotations

import hashlib
import hmac
import json
import sys
from pathlib import Path

import base58
from coincurve import PrivateKey

N_ORDER = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
STRETCH_ROUNDS = 100_000
OUT = Path(__file__).with_name("synthetic_lab_out")

# Fixed throwaway roots (reproducible; NEVER use on mainnet value)
CASA_PASS = b"synthetic-lab-passphrase-DO-NOT-USE-ON-MAINNET"
ELEC_ENTROPY_HEX = "00112233445566778899aabbccddeeff"
ARMORY_ROOT = bytes.fromhex("11" * 32)
ARMORY_CHAIN = bytes.fromhex("22" * 32)


def sha256(b: bytes) -> bytes:
    return hashlib.sha256(b).digest()


def sha256d(b: bytes) -> bytes:
    return sha256(sha256(b))


def require(cond: bool, msg: str) -> None:
    if not cond:
        raise RuntimeError(msg)


def t_low(k: int, n: int) -> int:
    """Leading-bit window mask (lab T — known by construction)."""
    return (1 << (n - 1)) | (k & ((1 << (n - 1)) - 1))


def hash160(b: bytes) -> bytes:
    return hashlib.new("ripemd160", sha256(b)).digest()


def addr_p2pkh_compressed(priv32: bytes) -> str:
    pub = PrivateKey(priv32).public_key.format(compressed=True)
    return base58.b58encode_check(b"\x00" + hash160(pub)).decode()


def priv_from_int(x: int) -> bytes:
    x = x % N_ORDER
    if x == 0:
        x = 1
    return x.to_bytes(32, "big")


# --- Locked generators ---


def casa_c1(passphrase: bytes, i: int) -> bytes:
    require(i >= 1, "casa i>=1")
    return sha256(passphrase + str(i).encode("ascii"))


def electrum_stretch(hex_seed: str) -> bytes:
    enc = hex_seed.encode("ascii")
    x = enc
    for _ in range(STRETCH_ROUNDS):
        x = sha256(x + enc)
    return x


def electrum_child(master: bytes, n: int, change: int = 0) -> bytes:
    pub = PrivateKey(master).public_key.format(compressed=False)
    mpk = pub[1:].hex()
    msg = f"{n}:{change}:".encode("ascii") + bytes.fromhex(mpk)
    seq = int.from_bytes(sha256d(msg), "big")
    return priv_from_int(int.from_bytes(master, "big") + seq)


def armory_ckd(priv: bytes, chain: bytes, index: int) -> tuple[bytes, bytes]:
    pub_u = PrivateKey(priv).public_key.format(compressed=False)
    I = hmac.new(chain, pub_u + index.to_bytes(4, "big"), hashlib.sha512).digest()
    IL, IR = I[:32], I[32:]
    ki = (int.from_bytes(IL, "big") * int.from_bytes(priv, "big")) % N_ORDER
    require(ki != 0, "degenerate")
    return ki.to_bytes(32, "big"), IR


def armory_external_child(root: bytes, chain: bytes, i: int) -> bytes:
    """Hypothesis path M/0/0/i — lab-only layout."""
    k, c = root, chain
    k, c = armory_ckd(k, c, 0)
    k, c = armory_ckd(k, c, 0)
    ki, _ = armory_ckd(k, c, i)
    return ki


def source_K(family: str, puzzle_n: int, roots: dict) -> bytes:
    if family == "casa_c1":
        return casa_c1(roots["casa_pass"], puzzle_n)  # i = n
    if family == "elec_recv":
        return electrum_child(roots["elec_master"], puzzle_n - 1, 0)  # i = n-1
    if family == "armory":
        return armory_external_child(roots["arm_root"], roots["arm_chain"], puzzle_n - 1)
    raise ValueError(family)


def build_series(family: str, roots: dict, n_max: int) -> list[dict]:
    rows = []
    for n in range(1, n_max + 1):
        K = int.from_bytes(source_K(family, n, roots), "big")
        P = t_low(K, n)
        require((1 << (n - 1)) <= P < (1 << n), f"window {n}")
        priv = priv_from_int(P)
        rows.append(
            {
                "n": n,
                "K_hex": f"{K:064x}",
                "P_hex": f"{P:064x}",
                "address": addr_p2pkh_compressed(priv),
            }
        )
    return rows


def recover(family: str, roots: dict, series: list[dict]) -> bool:
    for row in series:
        n = row["n"]
        K = int.from_bytes(source_K(family, n, roots), "big")
        P = t_low(K, n)
        addr = addr_p2pkh_compressed(priv_from_int(P))
        if addr != row["address"] or f"{P:064x}" != row["P_hex"]:
            return False
    return True


def main() -> int:
    full = "--full" in sys.argv
    n_max = 256 if full else 32
    print(f"Synthetic Puzzle Lab  n=1..{n_max}  (NOT real #71)")
    OUT.mkdir(exist_ok=True)

    elec_master = electrum_stretch(ELEC_ENTROPY_HEX)
    roots = {
        "casa_pass": CASA_PASS,
        "elec_master": elec_master,
        "arm_root": ARMORY_ROOT,
        "arm_chain": ARMORY_CHAIN,
    }
    wrong_roots = {
        "casa_pass": CASA_PASS + b"x",
        "elec_master": electrum_stretch("ff" * 16),
        "arm_root": bytes.fromhex("33" * 32),
        "arm_chain": ARMORY_CHAIN,
    }

    report = {"n_max": n_max, "T": "T_low", "families": {}}

    for family in ("casa_c1", "elec_recv", "armory"):
        print(f"\n--- {family} ---")
        series = build_series(family, roots, n_max)
        ok = recover(family, roots, series)
        bad = recover(family, wrong_roots, series)
        require(ok, f"{family} recovery failed")
        require(not bad, f"{family} wrong-root unexpectedly recovered")
        path = OUT / f"{family}_n1_{n_max}.json"
        path.write_text(json.dumps({"family": family, "T": "T_low", "series": series}, indent=2))
        print(f"  built {len(series)}  recovery=PASS  wrong_root_rejected=PASS")
        print(f"  sample n=1 addr={series[0]['address']}")
        print(f"  sample n={n_max} addr={series[-1]['address']}")
        print(f"  wrote {path.name}")
        report["families"][family] = {
            "recovery": True,
            "wrong_root_rejected": True,
            "addr_1": series[0]["address"],
            "addr_n": series[-1]["address"],
            "file": path.name,
        }

    # Cross-family: under T_low, n=1 always P=1 (0 free bits) → same addr.
    # Distinctness checked at n=16 where free bits exist.
    addrs16 = []
    for family in ("casa_c1", "elec_recv", "armory"):
        series = json.loads((OUT / report["families"][family]["file"]).read_text())["series"]
        addrs16.append(series[15]["address"])  # n=16
    require(len(set(addrs16)) == 3, "cross-family addr collision at n=16")
    print("\n  cross-family n=16 distinct: PASS")
    print("  note: n=1 under T_low ⇒ P=1 for every family (0 free bits)")

    (OUT / "lab_report.json").write_text(json.dumps(report, indent=2))
    print("\nRESULT: PASS")
    print("NOTE: This does not solve or search Puzzle #71.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:
        print(f"RESULT: FAIL ({e})", file=sys.stderr)
        raise SystemExit(1)
