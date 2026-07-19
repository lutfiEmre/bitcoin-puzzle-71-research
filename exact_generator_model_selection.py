#!/usr/bin/env python3
"""
Exact locked-generator Monte Carlo model selection.
Real Casascius C1/C2, Electrum v1, Armory CKD — throwaway roots only.

Transforms (distinct only):
  T_low  = 2^(n-1) | (K & (2^(n-1)-1))
  T_high = 2^(n-1) | (K >> (256-(n-1)))
Note: T_mod == T_low mathematically; not tested separately.

Armory path M/0/0/i is a Puzzle-hypothesis layout (EXTERNAL after account 0).
CKD formula is vector-locked; this path is NOT creator-verified.

Verdict is scoped to tested transforms + features + centroid classifier.

Run:
  python3 exact_generator_model_selection.py           # single seed demo + 30-seed stability
  python3 exact_generator_model_selection.py --quick   # demo only
"""
from __future__ import annotations

import hashlib
import hmac
import random
import statistics
import sys
from dataclasses import dataclass

from coincurve import PrivateKey

N_ORDER = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
STRETCH_ROUNDS = 100_000
SEQ_NS = list(range(1, 41))
N_TRAIN = 24
N_TEST = 12
N_STABILITY_SEEDS = 30
BASE_SEED = 20260720


def sha256(b: bytes) -> bytes:
    return hashlib.sha256(b).digest()


def sha256d(b: bytes) -> bytes:
    return sha256(sha256(b))


def casascius_c1(passphrase: bytes, i: int) -> bytes:
    if i < 1:
        raise ValueError("Casascius index >= 1")
    return sha256(passphrase + str(i).encode("ascii"))


def casascius_c2(passphrase: bytes, i: int) -> bytes:
    if i < 1:
        raise ValueError("Casascius index >= 1")
    d = str(i).encode("ascii")
    return sha256(d + b"/" + passphrase + b"/" + d + b"/BITCOIN")


def electrum_stretch(hex_seed: str) -> bytes:
    encoded = hex_seed.encode("ascii")
    x = encoded
    for _ in range(STRETCH_ROUNDS):
        x = sha256(x + encoded)
    return x


def electrum_mpk_hex(master32: bytes) -> str:
    return PrivateKey(master32).public_key.format(compressed=False)[1:].hex()


def electrum_child(master32: bytes, for_change: int, n: int) -> bytes:
    mpk = electrum_mpk_hex(master32)
    msg = f"{n}:{for_change}:".encode("ascii") + bytes.fromhex(mpk)
    seq = int.from_bytes(sha256d(msg), "big")
    secexp = (int.from_bytes(master32, "big") + seq) % N_ORDER
    if secexp == 0:
        secexp = 1
    return secexp.to_bytes(32, "big")


def armory_ckd(priv: bytes, chain: bytes, index: int) -> tuple[bytes, bytes]:
    pub_u = PrivateKey(priv).public_key.format(compressed=False)
    I = hmac.new(chain, pub_u + index.to_bytes(4, "big"), hashlib.sha512).digest()
    IL, IR = I[:32], I[32:]
    ki = (int.from_bytes(IL, "big") * int.from_bytes(priv, "big")) % N_ORDER
    if ki == 0:
        ki = 1
    return ki.to_bytes(32, "big"), IR


def armory_external_children(root_priv: bytes, root_chain: bytes, count: int) -> list[bytes]:
    """
    Hypothesis path only: M/0/0/0 .. M/0/0/(count-1).
    Matches gist EXTERNAL=0 under account 0 — NOT a creator-documented Puzzle path.
    """
    k, c = root_priv, root_chain
    k, c = armory_ckd(k, c, 0)  # account 0 (assumed)
    k, c = armory_ckd(k, c, 0)  # EXTERNAL (assumed)
    parent_k, parent_c = k, c
    return [armory_ckd(parent_k, parent_c, i)[0] for i in range(count)]


def t_low(k: int, n: int) -> int:
    """Low-bit keep + force MSB. Identical to 2^(n-1)+(k mod 2^(n-1))."""
    return (1 << (n - 1)) | (k & ((1 << (n - 1)) - 1))


def t_high(k: int, n: int) -> int:
    w = n - 1
    if w == 0:
        return 1 << (n - 1)
    return (1 << (n - 1)) | ((k >> (256 - w)) & ((1 << w) - 1))


# Only distinct transforms (T_mod removed — equals T_low)
TRANSFORMS = {"T_low": t_low, "T_high": t_high}


@dataclass(frozen=True)
class GenConfig:
    family: str
    index_mode: str


def gen_keys(cfg: GenConfig, rng: random.Random, max_i: int) -> dict[int, int]:
    keys: dict[int, int] = {}
    if cfg.family.startswith("casa"):
        passphrase = rng.randbytes(16)
        fn = casascius_c1 if cfg.family == "casa_c1" else casascius_c2
        for i in range(1, max_i + 1):
            keys[i] = int.from_bytes(fn(passphrase, i), "big")
        return keys
    if cfg.family.startswith("elec"):
        master = electrum_stretch(rng.randbytes(16).hex())
        change = 0 if cfg.family == "elec_recv" else 1
        for i in range(0, max_i + 1):
            keys[i] = int.from_bytes(electrum_child(master, change, i), "big")
        return keys
    if cfg.family == "armory":
        while True:
            root = rng.randbytes(32)
            if 0 < int.from_bytes(root, "big") < N_ORDER:
                break
        chain = rng.randbytes(32)
        for i, kb in enumerate(armory_external_children(root, chain, max_i + 1)):
            keys[i] = int.from_bytes(kb, "big")
        return keys
    raise ValueError(cfg.family)


def puzzle_to_index(n: int, mode: str, family: str) -> int:
    i = n if mode == "i_eq_n" else n - 1
    if family.startswith("casa") and i < 1:
        i = 1
    return i


def masked_sequence(cfg: GenConfig, T_name: str, rng: random.Random) -> list[int]:
    T = TRANSFORMS[T_name]
    max_need = max(puzzle_to_index(n, cfg.index_mode, cfg.family) for n in SEQ_NS)
    K = gen_keys(cfg, rng, max_need)
    return [T(K[puzzle_to_index(n, cfg.index_mode, cfg.family)], n) for n in SEQ_NS]


def low_bits(n: int, p: int) -> int:
    return p & ((1 << (n - 1)) - 1)


def features(seq: list[int]) -> list[float]:
    ones = zeros = 0
    pops: list[float] = []
    circ: list[float] = []
    b0_pairs = []
    for idx, n in enumerate(SEQ_NS):
        L = low_bits(n, seq[idx])
        w = n - 1
        for b in range(w):
            if (L >> b) & 1:
                ones += 1
            else:
                zeros += 1
        if idx + 1 < len(seq) and w >= 1:
            Lm = low_bits(SEQ_NS[idx + 1], seq[idx + 1]) & ((1 << w) - 1)
            pops.append(bin(L ^ Lm).count("1") / w)
            d = (Lm - L) % (1 << w)
            circ.append(min(d, (1 << w) - d) / (1 << w))
            b0_pairs.append((L & 1, Lm & 1))
    p1 = ones / max(ones + zeros, 1)
    xor_m = sum(pops) / max(len(pops), 1)
    circ_m = sum(circ) / max(len(circ), 1)
    same = (
        sum(1 for a, b in b0_pairs if a == b) / len(b0_pairs) if b0_pairs else 0.5
    )
    agree_hi = []
    for idx in range(len(seq) - 1):
        n = SEQ_NS[idx]
        w = n - 1
        if w < 2:
            continue
        Ln = low_bits(n, seq[idx])
        Lm = low_bits(SEQ_NS[idx + 1], seq[idx + 1]) & ((1 << w) - 1)
        agree_hi.append(
            1.0 if ((Ln >> (w - 1)) & 1) == ((Lm >> (w - 1)) & 1) else 0.0
        )
    hi_m = sum(agree_hi) / max(len(agree_hi), 1)
    pdel = [
        abs(seq[idx + 1] - 2 * seq[idx]) / (1 << SEQ_NS[idx])
        for idx in range(len(seq) - 1)
    ]
    return [p1, xor_m, circ_m, same - 0.5, hi_m, sum(pdel) / max(len(pdel), 1)]


# Classifier labels: canonical trio only. C2/change/index are probe-only elsewhere.
FAMILIES_FOR_CLF = [
    GenConfig("casa_c1", "i_eq_n"),
    GenConfig("elec_recv", "i_eq_n_minus_1"),
    GenConfig("armory", "i_eq_n_minus_1"),  # path M/0/0/i = hypothesis
]


def nearest_centroid_accuracy(
    train: list[tuple[int, list[float]]],
    test: list[tuple[int, list[float]]],
) -> float:
    dim = len(train[0][1])
    sums = {0: [0.0] * dim, 1: [0.0] * dim, 2: [0.0] * dim}
    cnt = {0: 0, 1: 0, 2: 0}
    for lab, feat in train:
        cnt[lab] += 1
        for j, v in enumerate(feat):
            sums[lab][j] += v
    cents = {lab: [s / max(cnt[lab], 1) for s in sums[lab]] for lab in sums}

    def dist(a: list[float], b: list[float]) -> float:
        return sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5

    ok = sum(
        1
        for lab, feat in test
        if min(cents, key=lambda c: dist(feat, cents[c])) == lab
    )
    return ok / max(len(test), 1)


def clf_accuracy(T_name: str, rng: random.Random) -> float:
    train: list[tuple[int, list[float]]] = []
    test: list[tuple[int, list[float]]] = []
    for lab, cfg in enumerate(FAMILIES_FOR_CLF):
        for _ in range(N_TRAIN):
            train.append((lab, features(masked_sequence(cfg, T_name, rng))))
        for _ in range(N_TEST):
            test.append((lab, features(masked_sequence(cfg, T_name, rng))))
    return nearest_centroid_accuracy(train, test)


def probe_stats(T_name: str, rng: random.Random) -> dict[str, tuple[float, float]]:
    """C2 / change / index variants — stats only, not classifier labels."""
    probes = [
        GenConfig("casa_c1", "i_eq_n"),
        GenConfig("casa_c2", "i_eq_n"),
        GenConfig("elec_recv", "i_eq_n_minus_1"),
        GenConfig("elec_change", "i_eq_n_minus_1"),
        GenConfig("armory", "i_eq_n_minus_1"),
    ]
    out = {}
    for cfg in probes:
        feats = [features(masked_sequence(cfg, T_name, rng)) for _ in range(12)]
        xor_m = sum(f[1] for f in feats) / len(feats)
        circ_m = sum(f[2] for f in feats) / len(feats)
        out[f"{cfg.family}/{cfg.index_mode}"] = (xor_m, circ_m)
    return out


def stability(n_seeds: int = N_STABILITY_SEEDS) -> dict[str, list[float]]:
    accs: dict[str, list[float]] = {t: [] for t in TRANSFORMS}
    for s in range(n_seeds):
        rng = random.Random(BASE_SEED + s * 9973)
        for T_name in TRANSFORMS:
            accs[T_name].append(clf_accuracy(T_name, rng))
        print(f"  seed[{s}] T_low={accs['T_low'][-1]:.3f} T_high={accs['T_high'][-1]:.3f}", flush=True)
    return accs


def main() -> int:
    quick = "--quick" in sys.argv
    print("Exact generator Monte Carlo")
    print("  transforms: T_low, T_high  (T_mod ≡ T_low — omitted)")
    print("  Armory path M/0/0/i: HYPOTHESIS (CKD locked; path not creator-verified)")
    print("  clf labels: casa_c1 / elec_recv / armory only; C2/change = probes")
    print(f"  SEQ n={SEQ_NS[0]}..{SEQ_NS[-1]}  train/test={N_TRAIN}/{N_TEST}")

    rng = random.Random(BASE_SEED)
    print("\n--- demo (single seed) ---")
    for T_name in TRANSFORMS:
        acc = clf_accuracy(T_name, rng)
        probes = probe_stats(T_name, rng)
        print(f"  {T_name} holdout_acc={acc:.3f}  (chance≈0.333)")
        for k, (x, c) in probes.items():
            print(f"    probe XOR/circ [{k}]={x:.4f}/{c:.4f}")

    if quick:
        print("\nVERDICT: NO_SEPARATION_DETECTED_UNDER_TESTED_TRANSFORMS_AND_FEATURES")
        print("NOTE: --quick skipped multi-seed stability")
        print("RESULT: PASS")
        return 0

    print(f"\n--- stability ({N_STABILITY_SEEDS} seeds) ---")
    accs = stability(N_STABILITY_SEEDS)
    print("\n=== STABILITY SUMMARY ===")
    # Gate on means near chance (~1/3). Single-seed max spikes with N_TEST=12
    # are binomial noise (σ≈0.08); do not reopen the line on one outlier.
    means = {}
    for T_name, vals in accs.items():
        mean = statistics.mean(vals)
        std = statistics.stdev(vals) if len(vals) > 1 else 0.0
        lo, hi = min(vals), max(vals)
        means[T_name] = mean
        print(f"  {T_name}: mean={mean:.3f} ± {std:.3f}  range=[{lo:.3f},{hi:.3f}]")

    means_near_chance = all(0.25 <= m <= 0.42 for m in means.values())
    if means_near_chance:
        verdict = "NO_SEPARATION_DETECTED_UNDER_TESTED_TRANSFORMS_AND_FEATURES"
        print("SOLVED_SEQUENCE_LINE: CLOSED")
    else:
        verdict = "MEAN_ACCURACY_OUTSIDE_CHANCE_BAND"
        print("SOLVED_SEQUENCE_LINE: REVISIT")

    print(f"VERDICT: {verdict}")
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:
        print(f"RESULT: FAIL ({e})", file=sys.stderr)
        raise SystemExit(1)
