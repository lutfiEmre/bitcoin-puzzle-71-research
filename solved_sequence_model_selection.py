#!/usr/bin/env python3
"""
Solved-sequence model-selection probes — public solved keys ONLY.
No seed/root scan. No #71 search.

Run: python3 solved_sequence_model_selection.py
"""
from __future__ import annotations

import json
import math
import random
import sys
from collections import Counter
from math import gcd
from pathlib import Path

N_ORDER = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
KEYS_PATH = Path(__file__).with_name("solved_keys.json")


def require(cond: bool, msg: str) -> None:
    if not cond:
        raise RuntimeError(msg)


def load_keys() -> dict[int, int]:
    raw = json.loads(KEYS_PATH.read_text())
    return {int(k): int(v, 16) for k, v in raw.items()}


def low_bits(n: int, p: int) -> int:
    return p & ((1 << (n - 1)) - 1)


def main() -> int:
    P = load_keys()
    Ns = sorted(P)
    require(len(Ns) == 82, f"expected 82 solved, got {len(Ns)}")
    require(all((1 << (n - 1)) <= P[n] < (1 << n) for n in Ns), "window invariant")

    pairs = [(n, n + 1) for n in Ns if (n + 1) in P]

    # pooled free-bit balance
    ones = zeros = 0
    pos_ones: Counter[int] = Counter()
    pos_tot: Counter[int] = Counter()
    for n in Ns:
        L = low_bits(n, P[n])
        for b in range(n - 1):
            pos_tot[b] += 1
            if (L >> b) & 1:
                ones += 1
                pos_ones[b] += 1
            else:
                zeros += 1
    p1 = ones / (ones + zeros)

    chi_sig = 0
    chi_n = 0
    for b, t in pos_tot.items():
        if t < 20:
            continue
        chi_n += 1
        o = pos_ones[b]
        e = t / 2
        chi = ((o - e) ** 2 + ((t - o) - e) ** 2) / e
        if chi > 3.84:
            chi_sig += 1

    # consecutive XOR of shared-width low bits
    pops: list[float] = []
    circ: list[float] = []
    g_gt1 = 0
    for n, m in pairs:
        w = n - 1
        if w == 0:
            continue
        Ln = low_bits(n, P[n])
        Lm = low_bits(m, P[m]) & ((1 << w) - 1)
        pops.append(bin(Ln ^ Lm).count("1") / w)
        if w >= 8:
            d = (Lm - Ln) % (1 << w)
            d = min(d, (1 << w) - d)
            circ.append(d / (1 << w))
        if gcd(P[n], P[m]) > 1:
            g_gt1 += 1
    xor_mean = sum(pops) / len(pops)
    circ_mean = sum(circ) / len(circ)

    # Monte Carlo: uniform-in-window null
    random.seed(0)

    def rand_window(n: int) -> int:
        return (1 << (n - 1)) | random.getrandbits(n - 1)

    def trial_stats() -> tuple[float, float, int]:
        store: dict[int, int] = {}

        def gp(n: int) -> int:
            if n not in store:
                store[n] = rand_window(n)
            return store[n]

        o = z = 0
        for n in Ns:
            L = gp(n) & ((1 << (n - 1)) - 1)
            for b in range(n - 1):
                if (L >> b) & 1:
                    o += 1
                else:
                    z += 1
        xp: list[float] = []
        g = 0
        for n, m in pairs:
            w = n - 1
            if w == 0:
                continue
            Ln = gp(n) & ((1 << w) - 1)
            Lm = gp(m) & ((1 << w) - 1)
            xp.append(bin(Ln ^ Lm).count("1") / w)
            if gcd(gp(n), gp(m)) > 1:
                g += 1
        return o / (o + z), sum(xp) / len(xp), g

    mc = [trial_stats() for _ in range(300)]
    mc_p1 = sorted(t[0] for t in mc)
    mc_xor = sorted(t[1] for t in mc)
    mc_g = sorted(t[2] for t in mc)

    def pct(val: float, arr: list[float]) -> float:
        return sum(1 for a in arr if a <= val) / len(arr)

    # synthetic family XOR means (masked) — should collapse together
    def xor_of(D: dict[int, int]) -> float:
        xs = []
        for n, m in pairs:
            w = n - 1
            if w == 0:
                continue
            xs.append(
                bin((D[n] & ((1 << w) - 1)) ^ (D[m] & ((1 << w) - 1))).count("1") / w
            )
        return sum(xs) / len(xs)

    def synth_casa() -> dict[int, int]:
        return {n: (1 << (n - 1)) | (random.getrandbits(256) & ((1 << (n - 1)) - 1)) for n in Ns}

    def synth_elec() -> dict[int, int]:
        M = random.randrange(1, N_ORDER)
        out = {}
        for n in Ns:
            k = (M + random.randrange(0, N_ORDER)) % N_ORDER
            out[n] = (1 << (n - 1)) | (k & ((1 << (n - 1)) - 1))
        return out

    def synth_arm() -> dict[int, int]:
        k = random.randrange(1, N_ORDER)
        out = {}
        for n in Ns:
            k = (random.randrange(1, N_ORDER) * k) % N_ORDER
            out[n] = (1 << (n - 1)) | (k & ((1 << (n - 1)) - 1))
        return out

    random.seed(2)
    fam_means = {}
    for name, fn in ("casa", synth_casa), ("elec", synth_elec), ("arm", synth_arm):
        fam_means[name] = sum(xor_of(fn()) for _ in range(80)) / 80

    print("Solved-sequence model-selection")
    print(f"  solved={len(Ns)} consecutive_pairs={len(pairs)}")
    print(f"  free-bit p1={p1:.4f}  MC_pct={pct(p1, mc_p1):.2f}")
    print(f"  bit-pos chi2>3.84: {chi_sig}/{chi_n} (expect ~5% false +)")
    print(f"  consec XOR popfrac={xor_mean:.4f}  MC_pct={pct(xor_mean, mc_xor):.2f}")
    print(f"  circ |ΔL|/2^w={circ_mean:.4f}  (uniform≈0.25)")
    print(f"  consec gcd>1={g_gt1}/{len(pairs)}  MC_pct={pct(float(g_gt1), [float(x) for x in mc_g]):.2f}")
    print(
        f"  synth XOR means casa={fam_means['casa']:.4f} "
        f"elec={fam_means['elec']:.4f} arm={fam_means['arm']:.4f} real={xor_mean:.4f}"
    )

    # Separation gate: families must not leave a detectable residue vs null
    require(abs(p1 - 0.5) < 0.03, "free-bit balance anomaly")
    require(abs(xor_mean - 0.5) < 0.03, "XOR independence anomaly")
    require(abs(circ_mean - 0.25) < 0.05, "ΔL circular anomaly")
    require(0.05 < pct(float(g_gt1), [float(x) for x in mc_g]) < 0.95, "gcd outlier vs MC")
    spread = max(fam_means.values()) - min(fam_means.values())
    require(spread < 0.02, "synthetic families separated on XOR")
    require(all(abs(fam_means[k] - xor_mean) < 0.03 for k in fam_means), "real far from synth")

    print("VERDICT: PRELIMINARY_NO_SEPARATION")
    print("NOTE: synth_* are randomized stubs — see exact_generator_model_selection.py")
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:
        print(f"RESULT: FAIL ({e})", file=sys.stderr)
        raise SystemExit(1)
