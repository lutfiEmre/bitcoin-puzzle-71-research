# Bitcoin Puzzle — Historical Research Dossier (no key hunt)

**Status: [`CLOSED_PENDING_NEW_PRIMARY_EVIDENCE`](RESEARCH_CLOSURE.md)** · reopen only via [`REOPEN_GATE.md`](REOPEN_GATE.md) · [`REPRODUCIBILITY_MANIFEST.json`](REPRODUCIBILITY_MANIFEST.json)

Public research notes on the **2015 Bitcoin Puzzle** funding / transaction construction and early deterministic-wallet tooling.

**This repository does not claim to have recovered Puzzle #71's key.**

**Correct bound:** #71 is not proven absolutely unsolvable; with current public evidence there is **no verifiable, computationally justified solution path**.

**It documents reproducible historical and on-chain evidence concerning**

**the generator, masking methodology and funding provenance.**



What is new here (bounded claims)


| Finding                                                                                                       | Status                                           |
| ------------------------------------------------------------------------------------------------------------- | ------------------------------------------------ |
| Casascius BAU **C2** formula `SHA256(i/passphrase/i/BITCOIN)` + 2011 published WIF vector                     | Verified (`casascius_vector_selftest.py`)        |
| Exact C2 **not** covered by prior indexed cascade families                                                    | Documented (`CASCADE_COVERAGE.md`)               |
| Compressed puzzle addresses **do not** eliminate Electrum/Armory as *source* `K[i]` sequences                 | Methodology (`SOURCE_SEQUENCE_REASSESSMENT.md`)  |
| Casascius BAU **cannot** build the puzzle TX (export-only)                                                    | Archaeology (`CASASCIUS_BAU_ARCHAEOLOGY.md`)     |
| Funding outpoint `9b11…1662:2` (100 BTC P2SH) spend reveals **2-of-3** redeem; cospent with other 2-of-3 P2SH | Verified on-chain (`FUNDING_SIBLING_CLUSTER.md`) |
| WalletExplorer attributes that P2SH cluster to **Bitstamp.net**                                               | Attributed — **not** second-source confirmed     |
| Puzzle TX builder fingerprint (v1/locktime0/low-S/256 ordered outs/0.004 BTC fee)                             | Verified (`TX_BUILDER_FINGERPRINT.md`)           |


## What is *not* established

- Casascius / Mike Caldwell created the Puzzle  
- Bitstamp created or funded the Puzzle  
- `173ujrh…` belongs to Bitstamp  
- Any passphrase, seed, BIP32 path, or mask transform `T` for #71  
- Exact wallet binary that signed the puzzle TX

Creator’s public technical line remains: consecutive keys from a deterministic wallet, masked for difficulty. Forum “HMAC / BIP32 / …” recipes without primary sources are **user guesses**, not verified creator method.

## Reproduce the Casascius C2 vector only

```bash
python3 -m pip install 'base58==2.1.1'
python3 casascius_vector_selftest.py
```

Expected: `RESULT: PASS` (published 2011 sample WIF).

## Document map


| File                              | Topic                                                        |
| --------------------------------- | ------------------------------------------------------------ |
| `GENERATOR_CENSUS_PRE2015.md`     | **Next primary track:** pre-2015 deterministic/bulk generators |
| `CREATOR_ARCHIVE.md`              | Forum / saatoshi_rising archive bounds                       |
| `FUNDING_PROVENANCE.md`           | Same-day funding chronology                                  |
| `FUNDING_SIBLING_CLUSTER.md`      | vout2 redeemScript, siblings, Bitstamp attribution (bounded) |
| `TX_BUILDER_FINGERPRINT.md`       | Funding + puzzle serialization / fee / low-S                 |
| `TX_STRUCTURE_FINGERPRINT.md`     | 256-output arithmetic uniqueness notes                       |
| `CASASCIUS_BAU_DOSSIER.md`        | C1/C2 formulas + test vector                                 |
| `CASASCIUS_BAU_ARCHAEOLOGY.md`    | 2011–2015 git history; no TX builder                         |
| `SOURCE_SEQUENCE_REASSESSMENT.md` | `K → T → P → A`; `T` unknown                                 |
| `CASCADE_COVERAGE.md`             | What R1–R7 did / did not test                                |
| `EVIDENCE_CANDIDATES.md`          | A/B/C/D string gate (test set empty)                         |


Optional related notes in the working tree (may or may not be in this publish set): `WALLET_BUILDER_COMPARISON.md`, `PUBKEY_FINGERPRINT.md`, `HISTORICAL_BUILDER_REPRODUCTION.md`.

## Information request (why this is public)

If you have **primary** material that intersects this dossier, please open an issue or reply on Bitcointalk with sources:

1. Second independent label for `3NTKgoHrYuktTXczxYfhLifTzfuNKcEc9B` / spend `aba0cf6f…`
2. Contemporaneous Bitstamp/BitGo deposit-address samples (Jan 2015) for redeem-script comparison
3. Archive links for Casascius BAU forum sample post / early ZIP binaries beyond GitHub
4. Any **documented** 2011–2015 generator that matches “consecutive deterministic keys” with a published test vector (not a new guess) — see `GENERATOR_CENSUS_PRE2015.md`
5. Corrections to WalletExplorer cluster claims with reproducible methodology
6. Deleted Bitcointalk/SourceForge/Google Code attachments of bulk/deterministic generators with exact formulas

Do **not** send private keys, seed phrases, or requests to sweep addresses.

## License / ethics

Research documentation and the published Casascius **throwaway** test vector only.  
No assistance for theft, sweeping, or attacking third-party wallets.