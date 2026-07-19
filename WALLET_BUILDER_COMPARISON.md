# Wallet / TX Builder Comparison (2011–2015 era)

Last updated: 2026-07-20  
Question: **who could have built funding + puzzle transactions?**  
Not: who generated deterministic keys.

Observed TX traits (see `TX_BUILDER_FINGERPRINT.md`): version=1, locktime=0, seq=`ffffffff`, SIGHASH_ALL, compressed P2PKH spends, **low-S**, funding 5-out mixed + change not last, puzzle **256 ordered arithmetic P2PKH**, absolute fee **0.004 BTC**.

**Date constraint:** Puzzle **2015-01-15**; Core **0.10.0** released **2015-02-16**. Prefer “0.9.x / 0.10 pre-release / raw-RPC-compatible” over “≥0.9”.

| Family | Can build multi-out / raw TX? | low-S by Jan 2015? | Compressed spends typical? | Fit vs puzzle 256-loop | Fit vs funding layout | Notes |
|--------|-------------------------------|--------------------|----------------------------|------------------------|----------------------|-------|
| **Bitcoin Core 0.9.x / 0.10 pre / raw-RPC** | Yes (`createrawtransaction` / GUI / RPC) | **Yes** (wallet low-S since 0.9, Mar 2014) | Yes | **Strong** for scripted raw TX | Compatible; change position configurable in raw | Compatible, **not identified**. Released 0.10.0 post-dates puzzle. |
| **Bitcoin Core 0.10.0 release fee estimator** | Yes | Yes (libsecp256k1) | Yes | N/A for structure | N/A | **Historically weak** as explanation of puzzle fee (shipped after puzzle) |
| **Casascius BAU** | **No** | N/A (no signer) | KeyPair default **uncompressed** addresses | **Eliminated as TX builder** | Eliminated | Key export only → `CASASCIUS_BAU_ARCHAEOLOGY.md` |
| **Electrum** (1.x/early 2.x) | Yes | Updating toward low-S in this era; not unique | 1.x addresses often uncompressed; spends can still use compressed if key marked | Possible with plugin/script | Possible | Compatible, **not identified** |
| **Armory** | Yes (offline TX) | Library-dependent | Classic era often uncompressed **addresses** | Possible for advanced user | Possible | Compatible, **not identified** |
| **bitcoinj** | Yes | low-S for similar span to Core | Yes | Strong for custom Java loop | Compatible | Compatible, **not identified** |
| **pywallet / bitcoin-python** | Wallet.dat / helper; TX build via bitcoind or libs | Depends on signing stack | Varies | Weak as sole 256-builder | Weak | Usually not the multi-out assembler |
| **Early JS (bitaddress, bitcoinjs)** | Paper/key focus; limited broadcast | bitcoinjs later low-S | Varies | Weak for 256 funded TX | Weak | Unlikely sole puzzle builder |
| **Custom C# / C++ / Python script** | Yes | If using Core 0.9+ lib or OpenSSL canonicalize | Author chooses | **Strong** (matches 256 arithmetic loop) | **Strong** (manual vout order) | **Best structural fit** for puzzle TX layout; still **unproven** |

## What can be said

**Verified**

- BAU did not build these transactions.  
- Puzzle TX structure **strongly suggests** a scripted or raw multi-output builder; manual construction of 256 outputs is theoretically possible but operationally implausible.  
- Both spends are **low-S + compressed + SIGHASH_ALL** — consistent with Core 0.9.x and several peers.  
- Funding vout2 P2SH is WalletExplorer-attributed **Bitstamp.net** with on-chain **2-of-3** redeem + Bitstamp-labeled cospends (`FUNDING_SIBLING_CLUSTER.md`). **Not** second-source confirmed; **not** “Bitstamp created the puzzle.”

**Not verified**

- Exact wallet binary name.  
- Nonce RNG / RFC6979 vs random k.  
- Same process for funding vs puzzle (fee magnitudes differ).  
- Independent confirmation of Bitstamp label beyond WalletExplorer.

**Inferred / Speculative**

- Puzzle fee **0.004 BTC** ≈ manual absolute leftover (inferred).  
- Operator used Core 0.9.x raw RPC, bitcoinj, or custom script after offline key prep (speculative).  
- Funding’s non-last change + Bitstamp P2SH sibling looks like **explicit raw construction** (inferred).

## Cross-links

- `TX_BUILDER_FINGERPRINT.md`  
- `HISTORICAL_BUILDER_REPRODUCTION.md`  
- `FUNDING_SIBLING_CLUSTER.md`  
- `CASASCIUS_BAU_ARCHAEOLOGY.md`  
- `TX_STRUCTURE_FINGERPRINT.md`  
