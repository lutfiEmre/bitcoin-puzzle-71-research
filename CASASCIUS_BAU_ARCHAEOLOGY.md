# Casascius BAU — Source Archaeology (2011–2015)

Last updated: 2026-07-20  
Repo clone used: `_research_bau/Bitcoin-Address-Utility`  
Remote: https://github.com/casascius/Bitcoin-Address-Utility  
**No tags/releases in git.** Binary historically: `https://casascius.com/btcaddress-alpha.zip` (blog 2013-01-26).

## Verdict (role boundary)

| Capability | Status | Evidence |
|------------|--------|----------|
| Deterministic consecutive keys (C1/C2) | **Yes** | `Walletgen.cs` history |
| Bulk CSV / importprivkey text export | **Yes** | commit `244030e` 2011-09-09 |
| Create / sign / broadcast Bitcoin TX | **No** | No RPC/raw-tx/send path; only prints `./bitcoind importprivkey …` |
| Default address serialization from `KeyPair(bytes)` | **Uncompressed** (`compressed=false` default) | `Model/KeyPair.cs` |

**Implied chain if BAU were ever used for puzzle keys:**

```text
BAU → K[i] (export CSV/WIF)
  → unknown T (custom script)
  → compressed A[i]
  → Bitcoin Core / Electrum / other builder → funding + puzzle TX
```

BAU alone **cannot** explain the puzzle transaction. It can only be a **key-material** candidate.

---

## Commit timeline (verified)

| Date | Commit | Fact |
|------|--------|------|
| 2011-08-03 | `591eb23` | First GitHub commit. `Walletgen.cs` **only C2** hardcoded: `i + "/" + pass + "/" + i + "/BITCOIN"`. Loop **fixed i=1..10**. |
| 2011-08-08 | `cfe60e7` | Single-address SHA256 passphrase box on Form1. |
| 2011-09-07 | `c564481` | User-chosen count **1–999**; passphrase warning bypass. |
| 2011-09-09 | `244030e` | **CSV** + **Import script** (`./bitcoind importprivkey`) output modes. |
| 2011-09-09 | `572ec93` | **C1 added** (`passphrase + n`) via label double-click. Field `GenerationFormula`; **default = 0 → C2 still default**. |
| 2012-11-07 | `8b09119` | **Default flips to C1** (`GenerationFormula = 1`). Double-click unlocks C2. Max count **9999**. Uses `KeyPair`. |
| 2012–2013 | BIP38 / escrow / inserts | Key/paper utilities; still **not** a TX broadcaster. |
| (HEAD) | — | Same C1-default / C2-via-double-click as post-`8b09119`. |

**No third walletgen formula** found in `git log -S '/BITCOIN'` / `GenerationFormula` history.

### Formula availability by era

| Era | C2 (`…/BITCOIN`) | C1 (`pass‖n`) | UI default |
|-----|------------------|---------------|------------|
| 2011-08-03 → 2011-09-08 | Only | Absent | C2 |
| 2011-09-09 → 2012-11-06 | Yes | Yes (double-click) | **C2** |
| 2012-11-07 → present | Yes (double-click) | Yes | **C1** |

Published sample WIF matches **C2** — consistent with **2011 default**, not with post-2012 default.

---

## Export formats (verified, `Walletgen.cs`)

| Mode | Format |
|------|--------|
| Normal | `Bitcoin Address #i: <addr>` + `Private Key: <WIF>` |
| CSV | `{i},"{addr}","{WIF}"` |
| Import script | `# i: addr` + `./bitcoind importprivkey {WIF}` |

To assemble a 256-output puzzle TX after export, **another tool** is required (Core raw TX, Electrum, bitcoinj, custom script, etc.).

---

## Transaction capability (verified negative)

Searched tree for network/TX builders: no `createrawtransaction`, `sendrawtransaction`, `signrawtransaction`, RPC client, or P2PKH spend assembler used to broadcast.

`Forms/EscrowTools.cs` / `KeyCombiner.cs`: offline escrow **codes** and key combination → still produce **keys/addresses**, not chain transactions.

`Debug.WriteLine("./bitcoind importprivkey …")` in Form1 confirms intended handoff to **bitcoind**.

---

## Passphrase UX (verified)

On show: 80-char CSPRNG string over  
`123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz*#_%+!`  
Warns if length &lt; 20 or `PassphraseTooSimple`.

---

## Authorship / Puzzle link

| Claim | Status |
|-------|--------|
| BAU is a documented 2011 consecutive-key generator | **Verified** |
| BAU built puzzle/funding TX | **Contradicted** by source (no TX builder) |
| Puzzle used BAU for `K[i]` | **Unknown** — no on-chain or message link |
| Mike Caldwell = puzzle creator | **No evidence** |

---

## Cross-links

- `CASASCIUS_BAU_DOSSIER.md` — formulas + test vector  
- `TX_BUILDER_FINGERPRINT.md` — who built the TXs  
- `EVIDENCE_CANDIDATES.md` — demo strings only  
- `casascius_vector_selftest.py` — C2 lock  
