# Puzzle 71 Research Notes

Last updated: 2026-07-19

## Scope

This note captures historical findings from the latest review of the public record around Bitcoin Puzzle 71 and related early deterministic-wallet terminology.

It is intentionally non-operational. It does not add new derivation code, brute-force logic, or wallet-search procedures.

## Stronger Historical Findings

- The puzzle transaction date remains 2015-01-15.
- No indexed public announcement tying the creator to this puzzle has been found before 2015-01-15.
- The first broadly visible public discussion of the original transaction still appears to be the Bitcointalk thread opened on 2015-12-28 by `ryanc`, who described the discovery as incidental rather than linked to a prior announcement.
- The creator quote about "consecutive keys from a deterministic wallet" lines up more naturally with early Bitcoin-era technical terminology than with a vague later description.

## Terminology Context

- "Deterministic wallet" was already a concrete term in Bitcoin discussions by 2011.
- Early discussions split the idea into two broad families:
  - Hash-chain style sequential key generation.
  - Master-key plus sequence/derivation style generation.
- That makes the creator's wording historically meaningful rather than casual.

## Research Implications

- Treat the phrase "deterministic wallet" as a time-specific clue, not as proof of one modern standard.
- Legacy wallet families matter more than generic modern assumptions.
- Bitcoin Core keypool behavior is a weaker fit for the creator's wording than true deterministic systems.
- Legacy Electrum and Armory stay historically relevant as reference points for provenance analysis.
- BIP32 may still be historically possible, but the creator's wording alone does not strongly privilege modern path conventions.

## Negative Findings That Still Matter

- No pre-2015 public writeup has been found that clearly announces the 256-address puzzle structure in advance.
- No reliable evidence has been found for folklore explanations such as Fibonacci, golden ratio, clustering myths, or address-text-derived secrets.
- Public retellings continue to point back to the same creator statement: masked consecutive keys from a deterministic wallet, with no exploitable pattern promised.

## Safe Next Steps

- Keep a dated research log for source chronology and terminology shifts.
- Separate historical hypotheses from operational search code.
- Track wallet-family provenance questions as documentation work first.
- Only add code for harmless benchmarking or synthetic test fixtures that do not target real Bitcoin keys, addresses, or mnemonic recovery.

## Boundary

This workspace should not be extended with new logic that improves real private-key recovery, seed recovery, or address-targeted brute-force capability.
