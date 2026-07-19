# Funding Sibling Cluster

Last updated: 2026-07-20  
Funding TX: `9b11b90a212c27c982013bafe1d4a0730e01357245f0d074051a988e4bba1662`  
Sources: mempool.space APIs; WalletExplorer.com; Bitstamp public blog 2015-01-09.  
**No seed search. WalletExplorer labels = attributed, not independently re-clustered. No second tagging provider confirmed yet.**

---

## Legend

| Tag | Meaning |
|-----|---------|
| **Verified** | On-chain parse / API |
| **Attributed** | Third-party label (WalletExplorer) |
| **Historical** | Contemporary public announcement |
| **Inferred** | Bounded reading of the above |
| **Speculative** | Hypothesis |

---

## Bitstamp-linked sibling — bounded conclusion

Funding transaction **vout2** sent **100 BTC** to P2SH address  
`3NTKgoHrYuktTXczxYfhLifTzfuNKcEc9B`.

WalletExplorer attributes this address to the **Bitstamp.net** cluster. The address later appears as an input in multiple transactions independently labelled by WalletExplorer as Bitstamp sender transactions (examples noted in WE history include large consolidations on later dates), strengthening the **internal consistency** of that attribution.

This attribution has **not** been confirmed by a second independent tagging provider.

**Historical context:** Bitstamp relaunched on **2015-01-09** after its January security breach, introduced **BitGo** multisig infrastructure, and instructed customers to use newly issued deposit addresses ([Bitstamp blog](https://blog.bitstamp.net/post/bitstamp-is-open-for-business-better-than-ever/); CoinDesk / contemporaneous coverage). The puzzle funding transaction was created on **2015-01-15**, six days after that relaunch.

**Bounded inference:** the 100 BTC output **may** have been a deposit into Bitstamp’s newly deployed multisig deposit infrastructure.

**Not established:**

- that Bitstamp created or funded the Puzzle;  
- that `173ujrh…` belongs to Bitstamp;  
- that the Puzzle creator was a Bitstamp employee;  
- that the exchange connection reveals the deterministic wallet, seed, or mask transform `T`.

**Most sober scenario (speculative):** creator / funding-address controller was a **Bitstamp customer** moving funds while staging the puzzle — not an insider claim.

---

## Exact outpoint analysis: `9b11…1662:2` (Verified)

| Field | Value |
|-------|--------|
| Outpoint | `9b11b90a212c27c982013bafe1d4a0730e01357245f0d074051a988e4bba1662:2` |
| Value | 10000000000 sat (100 BTC) |
| Address | `3NTKgoHrYuktTXczxYfhLifTzfuNKcEc9B` |
| **spend_txid** | `aba0cf6fdad0e55b4be381154db7a8bdfab43cc7ead2daa90fbd03804d0b7e21` |
| spend block / time | **339053** / `1421325826` (~1.2 h after funding) |
| **vin index** | **7** |
| scriptSig layout | `OP_0` + sig(72) + sig(71) + redeemScript(105) |
| **redeemScript** | `OP_2 <33B> <33B> <33B> OP_3 OP_CHECKMULTISIG` |
| Threshold | **2-of-3** |
| Pubkey count | **3** (all compressed, 33 bytes) |
| Pubkeys | `027d43d28e…abe1` · `03a550421b…8234` · `029ecf43f7…70c0` |
| Signatures used | **2** (low-S class lengths 72+71) |

Redeem hex (full):

```text
5221027d43d28eb51dcb4ccff779dfc0729466278c5a4929cf07fa74def735c5dbabe12103a550421bc0182d715bf661f86d40c81d80664cbafd66f4d3d07604bbd48d823421029ecf43f7d1b5a2d85b71a12e8d011c78a953f8a3c45e73ea7995e279a15570c053ae
```

Local artifact: `_research_bau/siblings/vout2_redeem_summary.json`

### Co-spent inputs (Verified + Attributed)

Spend TX: 9 vin / 9 vout, fee 40000 sat, size 2987.

| vin | Address | Value | Redeem | WE label |
|-----|---------|-------|--------|----------|
| 0–6, 8 | distinct P2SH | various | **all 2-of-3 compressed (105 B)** | **all Bitstamp.net** |
| **7** | `3NTKg…` (our outpoint) | 100 BTC | 2-of-3 | **Bitstamp.net** |

Each co-spent P2SH uses a **different** 3-pubkey set (not the same redeem as vout2) — consistent with **per-deposit HD multisig addresses**, not a single reused script.

Change-like output of that spend: `34kMwo8CjWLEsYBzQxfTyHFyY9xJwu48WR` (P2SH) — also WE **Bitstamp.net**.

**Inferred:** Exact outpoint was swept inside a **Bitstamp-labeled 2-of-3 P2SH consolidation**, matching the public Bitstamp+BitGo “new deposit address” era.  
**Caveat:** 2-of-3 alone ≠ Bitstamp (BitGo and others use the same template). Strength comes from **WE cluster + cospend + historical timing**, still awaiting a second label source.

---

## All funding outputs — first spends (Verified)

| vout | Address | Value | First spend | Δ | Notes |
|------|---------|-------|-------------|---|-------|
| 0 | `1Aru8…` | 1.5 | `c27a73ae…` @ 339062 | ~2.7 h | Cospends stay in WE `[0000af469f]` (unnamed) |
| 1 | `19gpJ…` | 2.0 | `30f40406…` @ 339046 | **~6 min** | See below |
| 2 | `3NTKg…` | 100 | `aba0cf6f…` @ 339053 | ~1.2 h | Bitstamp-linked P2SH (above) |
| 3 | `173uj…` | 45.47989 | `a306c99f…` @ 339055 | ~1.7 h | 5 BTC → Poloniex-labeled (below) |
| 4 | `1Czoy…` | 32.9 | `08389f34…` @ 339085 | ~6.55 h | Puzzle TX |

---

## Other siblings (Attributed / Verified)

### vout1 `19gpJ…` (2 BTC)

First spend outs (WE):

| Value | Address | WE |
|-------|---------|-----|
| 2.0 BTC | `1HAgN76TfcFEMCiH2u6cFCJyhYq5vip1gY` | **Bitfinex.com-old2** |
| 1.0 BTC | `1EcHMWzdMb2VVi8DNMvK3sszC56L2mciKQ` | **BitBargain.co.uk** |
| dust | `1BCDRx…` | same cluster as `19gpJ…` `[0031299692]` |

**Inferred:** Within minutes, part of the funding fan-out reached **other exchange/merchant-labeled** sinks (WE). Still single-provider attribution.

### vout0 `1Aru8…` (1.5 BTC)

First spend consolidates with other `[0000af469f]` inputs; primary out ~2.01 BTC to unnamed `[000022f990]`. **No named exchange label** in this pass.

### vout3 change → `1BRJeZ…` (5 BTC)

WE label: **Poloniex.com**.  
Fee on that spend: **1000 sat** (same absolute fee as funding TX).

**Inferred:** `173ujrh…` operator also moved value toward a Poloniex-labeled address ~1.7 h after funding — multi-venue activity, not Bitstamp-only.

### Activity scale (Verified)

| Address | Funded TXOs | Lifetime sum |
|---------|-------------|--------------|
| `1Aru8…` | 1582 | ~11 871 BTC |
| `19gpJ…` | 1054 | ~1 935 BTC |
| `3NTKg…` | 250 | ~18 017 BTC |
| `173uj…` | 10127 | ~1 121 839 BTC |
| `1Czoy…` | 6 | ~32.9 BTC |

WE wallets: five funding outs → **five different** clusters (`1Czoy…` thin staging; `173uj…` huge unlabeled hub).

---

## Priority (updated)

| Priority | Item | Status |
|----------|------|--------|
| 1 | Exact `9b11…:2` redeemScript + cospend | **Done this pass** |
| 2 | Second independent Bitstamp label source | Open |
| 3 | Other siblings (19gp / 1Aru8 / Poloniex hop) | **Partial** |
| 4 | Core 0.9.3 reproduction lab | Secondary (unlikely to ID binary) |
| — | Casascius passphrase / cascade grind | **Closed** |

---

## Cross-links

- `FUNDING_PROVENANCE.md`  
- `TX_BUILDER_FINGERPRINT.md`  
- `WALLET_BUILDER_COMPARISON.md`  
- `HISTORICAL_BUILDER_REPRODUCTION.md`  
- `EVIDENCE_CANDIDATES.md`  
