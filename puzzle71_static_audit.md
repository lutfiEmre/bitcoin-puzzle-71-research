# Puzzle 71 Static Audit

Reviewed: 2026-07-19

## Scope

This is a source-level review of the current local files. No real Puzzle 71
search was run and no private-key, seed-recovery, or target-address search
logic was added or changed.

## Verified Findings

1. The `electrum_v1` mode is not a faithful legacy Electrum v1 implementation.
   It feeds the stretched hash into the sequence calculation as a placeholder
   for the master public key. Therefore `hits=0` in this mode cannot rule out
   legacy Electrum v1 as a historical possibility.

2. `--timestamp-window` materializes both all timestamp seeds and all jobs in
   memory. A +/- seven-day window contains 1,209,601 timestamps. With the
   current 12 indexed families and five offsets, this creates 72,576,060
   indexed jobs before chain jobs are included. A quick completion claim for
   this exact implementation is not credible.

3. The current command-line interface has no `--encodings` argument.
   Timestamp generation currently creates only four-byte big-endian values.
   A no-hit result does not cover other timestamp representations.

4. `first_is_hash` is redundant for short seeds only in the single-SHA chain
   case: both branches start from `SHA256(seed)`. It is not redundant when the
   double-hash option is selected, because the two branches then use different
   first states.

5. `mask_le` is not a clean little-endian numeric masking model. It masks the
   ordinary numeric value and then reverses its 32-byte representation before
   comparison. Its negative results should not be treated as evidence against
   meaningful endian alternatives.

6. Chain values are recalculated from the seed for each requested puzzle index.
   This makes the existing chain evaluation materially more expensive than its
   mathematical model requires. It also means the shared `QUICK` order is a
   poor performance proxy for every generator family.

7. Each cascade match overwrites `puzzle71_CANDIDATE.txt`, so multiple matches
   would not be retained. A cascade-only match also does not independently
   establish that any resulting value corresponds to the Puzzle 71 address.

8. The hunter uses `Queue.empty()`, which is not reliable across processes, and
   accepts invalid range and worker parameters without preflight checks. Its
   random mode has no durable coverage record and can revisit the same blocks.

9. The native artifacts are present in this workspace: `build_native.sh`,
   `puzzle71_native.c`, `puzzle71_native`, and `run_max.sh`. Any report saying
   they are absent describes a different or older copy of the folder.

## Interpretation

The current code can support limited synthetic or historical comparison work,
but it cannot support strong exclusion claims about legacy wallet families,
timestamp encodings, or endian behavior. In particular, a no-hit result from
the current Electrum, timestamp, or `mask_le` paths should be recorded as
inconclusive rather than negative evidence.

## Boundary

The issues above are documented without implementing target-search
optimizations, real wallet derivation, seed recovery, or address validation.
Those changes would materially increase real private-key recovery capability
and are outside the safe scope of this workspace.
