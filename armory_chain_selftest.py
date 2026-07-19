#!/usr/bin/env python3
"""
Armory HD CKD formula lock — Alan Reiner gist 2012-04-27 ONLY.
No Puzzle #71 search. Exit 0 on match.

Source: https://gist.github.com/etotheipi/2513316 (ckd_output.txt)
Title: "Child Key Derivation Test Vector(s)"
Impl target: HDWalletCrypto().ChildKeyDeriv (EncryptionUtils era output)

Exact CKD (verified byte-for-byte vs gist PRIVATE Key Tree):
  I  = HMAC-SHA512(chain, uncompressed_pubkey(65B) || BE32(index))
  k' = (IL * k) mod n          # multiply, not BIP32-add
  c' = IR
Public path: K' = IL * K  (same I from uncompressed parent pub || BE32(i))
"""
from __future__ import annotations

import hashlib
import hmac
import sys

from coincurve import PrivateKey, PublicKey

N_ORDER = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# --- Fixed root from ckdTestVectors[] ---
ROOT_PRIV = bytes.fromhex("aa" * 32)
ROOT_PUB_UNCOMP = bytes.fromhex(
    "04"
    "6a04ab98d9e4774ad806e302dddeb63b"
    "ea16b5cb5f223ee77478e861bb583eb3"
    "36b6fbcb60b5b3d4f1551ac45e5ffc49"
    "36466e7d98f6c7c0ec736539f74691a6"
)
ROOT_CHAIN = bytes.fromhex("dd" * 32)

# Endianness display from gist (CKD serializes index as BE)
ENDIAN_CHECKS = {
    ("LE", 5): "05000000",
    ("LE", 4095): "ff0f0000",
    ("BE", 5): "00000005",
    ("BE", 4095): "00000fff",
}

# HDW_CHAIN_EXTERNAL=0, HDW_CHAIN_INTERNAL=1 (from tree layout M/0/0 vs M/0/1)
HDW_CHAIN_EXTERNAL = 0
HDW_CHAIN_INTERNAL = 1

# Full PRIVATE Key Tree from gist output (Priv, compressed Pub, Chain)
TREE: dict[str, tuple[str, str, str]] = {
    "M": (
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "026a04ab98d9e4774ad806e302dddeb63bea16b5cb5f223ee77478e861bb583eb3",
        "dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd",
    ),
    "M/0": (
        "c677f7e86462f30d22eaf35798206c5df65080e9b80378232896a06f24350e7e",
        "035acb1286d1f1a236418166739a20ba8e64a5ff3d7a5d5bb926c079b1b57c47fb",
        "38f8418a58c4519cbc652d41cbaf29a069b52a0e0825474a3b1b70628854c1fb",
    ),
    "M/1": (
        "9affe2ba65a020a102ff1685da2b8bbf8d25905c8e256613fe517d8a61df1234",
        "027ad1d2d23ad6d33ec066ff5f3d9dafcdfae568bd63ebf1c39a930c40f148343b",
        "c6fd4ddd712f3501965c212d7b70ff0e49f1a1c4a5b28e7ae43b40d7e8c31f87",
    ),
    "M/0/0": (
        "d15f204595f54e2debded3a57e16df2acdd295f31b0ac7d242aaea4ea76a51a9",
        "020432ee4f244c5766bf65bfcfa880887aec8059f9227a2d37f18aabb375dc810f",
        "c3487013281c251092fddedb6045f3437424803d91584976cf0aac2e60d3f34e",
    ),
    "M/0/1": (
        "67e7a036d42ba55f1f3371ed2d6684f661189a430f4087a5e48f85c53a4042c7",
        "033fdf5b94b9d749307db9410f3e611a26e87a8500ab844e6580b0f08288dd06df",
        "b146a80fd1e9c6b65feebe5d06445a160c493158bce1ba591a73524e51a8b7fa",
    ),
    "M/0/0/0": (
        "505eb7e856d61b8e1c36f25155209f91ab9f8ff928280ca7e886be792799e94b",
        "02c1030675e83209462ad2f31f216a43fce947c11917f813979593273437123431",
        "fd86b4212e10c2142b3f8b0e77c796742b9d809fc8fdacf7e7b1ac9f27e9c385",
    ),
    "M/0/0/1": (
        "afb43c36f45131cfa200a5cdf30aac2a9d645ed67bddb76af3093d943ccb88fd",
        "03443f05bf2be69afe7bafa34e36b7c07d764e7e84f8d2880d29f3b96694c0ee71",
        "760ace2164a0dd6b554c2052a6bb2e374c5f620f4c4729838234b3eee88d684b",
    ),
    "M/0/0/2": (
        "514fd336ef931272d7287dce62741197199ce7f87378eb93d765962c192c8cc4",
        "03fb76e19128cdd8732375638bfb8f8c44d93081c1a04679241e3eaf398b44a612",
        "18a9577e270124833006d577dc5471e4f4f9a2694cdc16cb3227406085c2faa8",
    ),
    "M/0/1/0": (
        "ff3d8971a5d8b8eca842b0baea167f97e10ef7dddabc0475d701459fc090dfc3",
        "0210d71ab1015089b8f9e975b57bfd5ee58dbbabf464ab36e42162da46dc038028",
        "39f476bf30270cf9b620056aa8e234672606bca4779b0b23bb76ce5799e73cfd",
    ),
    "M/0/1/1": (
        "7ec5b59a4b82d1a66b54a3437906a5026b8fee1116b4ff65f2eb9109df093a82",
        "0367b0c155b0ff3f639127eef736d0b5ccd8c38ea6c83150f44477f22db1f64562",
        "740895154a15e07cc6161ca291fba3e7bb2fa029b388dd6c2bc5416e8e63b09a",
    ),
    "M/0/1/2": (
        "5e3add13a3c969af0535a2533cc89f89b163876988109dade440130bd00b1b21",
        "035bcff1a8346db855b0a7077fb91d66e8917b9cc245ecc7785d4c110258dce077",
        "fd5d67a45e725a97af53814a90933c2eb9d47ef1e77d3ff2e97e9b1e7e9d6f56",
    ),
    "M/1/1": (
        "b8cb851ff2ff129504c87d5c605b2cad59753ce71bf0cd02aacde8c5aa05bf50",
        "031671a5707edb7b15b46f98d81d858b9ba506f26b6d656b876b1c08291b9db9a8",
        "4ed07788fbd1df7c09b33b0f661320e163aba116b3ac2daf6b3c503293f46e59",
    ),
    "M/1/1/4095": (
        "d129376c6a82dfbbcafaef5050699dd0457a90402e8216a344df99b835e97d96",
        "0294c504145432dd6f61205cb34f90bebddba48b8074ce77cbd5b30ef042cb1f89",
        "d2af3fd937b51d1c7f0d418ebc9e37becb475ebe5c25a4a85642ae35ea8836c9",
    ),
    "M/1/1/4294967295": (
        "7d499b6101bdc3fe80c705f1e1ac9df187e40fa70c6bdefb9dde5436c518cd27",
        "023bb281583caefcc48a744a56dfa794ab130d3567af99b70fa6f7771a3860126d",
        "7ffdc1161f63afe0576a7047edf57b2c0e02173724dcf912ebb5ea1aa026604e",
    ),
}

# First ≥5 address-level children on external chain (M/0/0/i) — byte Priv/Pub/Chain
FIRST5_EXTERNAL = ["M/0/0/0", "M/0/0/1", "M/0/0/2", "M/0/1/0", "M/0/1/1"]


def require(cond: bool, msg: str) -> None:
    if not cond:
        raise RuntimeError(msg)


def path_indices(path: str) -> list[int]:
    if path == "M":
        return []
    require(path.startswith("M/"), f"bad path {path}")
    return [int(x) for x in path[2:].split("/")]


def ckd_private(priv: bytes, chain: bytes, index: int) -> tuple[bytes, bytes]:
    """Historical Armory ChildKeyDeriv from extended private key."""
    pub_u = PrivateKey(priv).public_key.format(compressed=False)
    I = hmac.new(chain, pub_u + index.to_bytes(4, "big"), hashlib.sha512).digest()
    IL, IR = I[:32], I[32:]
    ki = (int.from_bytes(IL, "big") * int.from_bytes(priv, "big")) % N_ORDER
    require(ki != 0, "degenerate private child")
    return ki.to_bytes(32, "big"), IR


def ckd_public(pub_uncomp: bytes, chain: bytes, index: int) -> tuple[bytes, bytes]:
    """Same CKD from extended public key only (Priv empty)."""
    require(len(pub_uncomp) == 65 and pub_uncomp[0] == 0x04, "need uncompressed pub")
    I = hmac.new(chain, pub_uncomp + index.to_bytes(4, "big"), hashlib.sha512).digest()
    IL, IR = I[:32], I[32:]
    Ki = PublicKey(pub_uncomp).multiply(IL)
    return Ki.format(compressed=False), IR


def walk_private(indices: list[int]) -> tuple[bytes, bytes]:
    k, c = ROOT_PRIV, ROOT_CHAIN
    for i in indices:
        k, c = ckd_private(k, c, i)
    return k, c


def walk_public(indices: list[int]) -> tuple[bytes, bytes]:
    K, c = ROOT_PUB_UNCOMP, ROOT_CHAIN
    for i in indices:
        K, c = ckd_public(K, c, i)
    return K, c


def main() -> int:
    print("Armory CKD vector self-test (etotheipi/2513316)")

    # Endianness display lock (gist preamble)
    for (endian, n), hexv in ENDIAN_CHECKS.items():
        got = n.to_bytes(4, "little" if endian == "LE" else "big").hex()
        require(got == hexv, f"endian {endian}({n}): {got} != {hexv}")
    print("  endianness display: PASS")

    # Root pubkey consistency
    root_comp = PrivateKey(ROOT_PRIV).public_key.format(compressed=True)
    root_uncomp = PrivateKey(ROOT_PRIV).public_key.format(compressed=False)
    require(root_uncomp == ROOT_PUB_UNCOMP, "root uncompressed pub mismatch")
    require(root_comp.hex() == TREE["M"][1], "root compressed pub mismatch")
    print("  root Priv→Pub: PASS")

    # Full tree: private derivation byte-for-byte
    for path, (ep, epu, ec) in TREE.items():
        k, c = walk_private(path_indices(path))
        pub = PrivateKey(k).public_key.format(compressed=True)
        require(k.hex() == ep, f"{path} priv")
        require(c.hex() == ec, f"{path} chain")
        require(pub.hex() == epu, f"{path} pub")
    print(f"  private tree: PASS ({len(TREE)} nodes)")

    # Public derivation vs private (same pubs + chains) — gist equality tests
    for path in TREE:
        idxs = path_indices(path)
        k, c_priv = walk_private(idxs)
        K, c_pub = walk_public(idxs)
        pub_from_priv = PrivateKey(k).public_key.format(compressed=False)
        require(pub_from_priv == K, f"pub≠priv at {path}")
        require(c_priv == c_pub, f"chain≠ at {path}")
    print(f"  private↔public equality: PASS ({len(TREE)} nodes)")

    # Explicit first-5 external/internal address children
    for path in FIRST5_EXTERNAL:
        k, c = walk_private(path_indices(path))
        ep, epu, ec = TREE[path]
        require(k.hex() == ep and c.hex() == ec, path)
        require(
            PrivateKey(k).public_key.format(compressed=True).hex() == epu,
            path + " pub",
        )
    print(f"  first {len(FIRST5_EXTERNAL)} child byte-lock: PASS")

    # Account / chain constants from gist code structure
    require(HDW_CHAIN_EXTERNAL == 0 and HDW_CHAIN_INTERNAL == 1, "chain constants")
    k_ex, _ = walk_private([0, HDW_CHAIN_EXTERNAL])
    k_in, _ = walk_private([0, HDW_CHAIN_INTERNAL])
    require(k_ex.hex() == TREE["M/0/0"][0], "EXTERNAL≠M/0/0")
    require(k_in.hex() == TREE["M/0/1"][0], "INTERNAL≠M/0/1")
    print("  HDW_CHAIN_EXTERNAL/INTERNAL: PASS")

    # Large indices from gist
    for path in ("M/1/1/4095", "M/1/1/4294967295"):
        k, c = walk_private(path_indices(path))
        require(k.hex() == TREE[path][0] and c.hex() == TREE[path][2], path)
    print("  large indices 4095 / UINT32_MAX: PASS")

    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:
        print(f"RESULT: FAIL ({e})", file=sys.stderr)
        raise SystemExit(1)
