# Pre-2015 Deterministic / Bulk-Key Generator Census

Last updated: 2026-07-20  
Cutoff: tools that **existed and were usable on or before 2015-01-15** (Puzzle TX day).  
Goal: find which software could have produced consecutive source keys `K[i]` — **not** to grind seeds.

Creator constraint (verbatim gist): consecutive keys from a **deterministic wallet**, then unknown mask `T` → Puzzle `P[i]`.

```text
deterministic generator → K[i] → T(unknown) → P[i] → compressed A[i]
```

Without a pinned generator family, seed / timestamp / path / random hunts stay blind.

**Hard rule:** document exact formula + index base + change flag + test vector.  
No passphrase cascade. Puzzle link column stays empty unless primary evidence appears.

---

## Legend

| Field | Meaning |
|-------|---------|
| **Fit** | Match to “consecutive deterministic keys” (not probability of being the Puzzle) |
| **Verified** | Formula pinned to source/commit/changelog |
| **Partial** | Family known; stretch/index/serialization still ambiguous |
| **Open** | Exists historically; exact formula not yet pinned here |
| **Vector** | Published throwaway test vector available? |

Fit scale: **High** / **Medium** / **Low** / **None** (for consecutive-from-seed).

---

## Master table

| ID | Tool | Era ≤2015-01-15 | Exact private-key formula | Index base | Change/recv? | Test vector? | Fit | Puzzle link |
|----|------|-----------------|---------------------------|------------|--------------|--------------|-----|-------------|
| G01 | **Casascius BAU C1** | 2011-09+ (default after 2012-11) | `SHA256(passphrase ‖ decimal(i))` | **1** | No | Yes (forum sample is C2, not C1) | **High** | None |
| G02 | **Casascius BAU C2** | 2011-08+ (early default) | `SHA256(decimal(i)‖"/"‖pass‖"/"‖decimal(i)‖"/BITCOIN")` | **1** | No | **Yes** — WIF `5JwH8jmz…8Ym` | **High** | None |
| G03 | **Electrum 1.x** | 2011–early 2015 | Stretch seed (~10⁵ SHA); `K = (master + seq) mod n`; `seq = SHA256d(str(i)+":"+str(change)+":"+mpk)` | **0** typical | **Yes** (0/1) | **Yes** — `ELECTRUM_V1_VECTOR_LOCK.md` | **High** | None |
| G04 | **Armory HD CKD** (2012 gist) | 2012-04-27+ | `HMAC-SHA512(c, uncomp_pub‖BE32(i))`; `k'=(IL×k) mod n` | **0** tree | EXTERNAL=0 / INTERNAL=1 | **Yes** — `ARMORY_VECTOR_LOCK.md` | **High** | None |
| G05 | **BIP32 HD** | BIP assigned 2012-02-11; usable builds 2013–2014+ | `HMAC-SHA512("Bitcoin seed", seed)` → CKD | path-dependent | Via path (e.g. change=1) | **Yes** (BIP32 wiki vectors) | **Medium–High** | None |
| G06 | **gmaxwell Type-1** | Documented mid-2011 | `Priv = H(n ‖ S ‖ type)` (serialization variants) | usually 0-based n | **Yes** (type) | Conceptual; exact H layout variants | **High** (language) | None |
| G07 | **gmaxwell Type-2** | 2011; Armory/Electrum lineage | `Priv = master + H(n ‖ S ‖ type)` | 0-based | **Yes** | Partial | **High** | None |
| G08 | **bitaddress.org Brain** | v1.4/v1.6+ (~2011–12) | `SHA256(passphrase)` → **single** key | N/A | No | Famous phrases (insecure) | **Low** | None |
| G09 | **bitaddress.org Bulk** | v0.7+ | **Random** keypairs → CSV (not seed-chained) | N/A | No | N/A | **None** as det. wallet | None |
| G10 | **brainwallet.org** | pre-2015 | `SHA256(passphrase)` single key (common) | N/A | No | `correct horse…` folklore | **Low** | None |
| G11 | **Type-1 pass+index clones** (e.g. brainvault-style) | various | `SHA256(passphrase ‖ decimal(i))` (often **0-based**) | **0** or 1 | Usually no | Some README examples | **Medium–High** | None |
| G12 | **pybitcointools** | 2013–2014 | Electrum-compatible + BIP32 helpers (`electrum_privkey`, `bip32_*`) | Electrum: 0 | Electrum: yes | Library demos | **High** (as Electrum/BIP32 host) | None |
| G13 | **bitcoinjs / early JS HD** | BIP32 ports ~2013–2014 | BIP32 CKD (impl-dependent) | path | path | Open per release | **Medium** | None |
| G14 | **Mycelium HD** | HD from **2014-10-07** | BIP32/BIP39/BIP44 | BIP44 | Yes | BIP39/44 vectors | **Medium** | None |
| G15 | **Schildbach Bitcoin Wallet** | pre-HD era dominant | Key pool / random until HD features later | N/A early | N/A | — | **Low** early | None |
| G16 | **libbitcoin** | early 2010s | Electrum-v1 + BIP32 modules (version-pin required) | depends | depends | Open | **Medium–High** | None |
| G17 | **BIP38 / Casascius physical** | 2012+ | Encryption of existing keys; intermediate codes | N/A | N/A | BIP38 vectors | **None** as consecutive `K[i]` source | None |
| G18 | **Custom SHA256 indexed scripts** | always | Any `H(seed‖i)` / `H(i‖seed‖…)` | author | optional | Rarely published | **High** if bulk | None |

---

## Detail cards (four required fields)

### G01 / G02 — Casascius BAU

| | |
|--|--|
| Formula | C1 / C2 — see `CASASCIUS_BAU_DOSSIER.md` |
| Index | **1** … n (max 999→9999) |
| Change | No |
| Vector | C2 published sample **PASS** (`casascius_vector_selftest.py`) |
| Sources | GitHub `casascius/Bitcoin-Address-Utility` commits `591eb23`, `572ec93`, `8b09119` |
| Notes | Export CSV/WIF only; **not** TX builder. Default flipped C2→C1 in Nov 2012. |

### G03 — Electrum 1.x

| | |
|--|--|
| Formula | `master = stretch(seed)`; `offset = SHA256d(f"{n}:{change}:" + mpk)`; `priv = (master + offset) mod n` |
| Index | **0-based** in standard clients |
| Change | **Yes** (`change` 0/1) |
| Vector | Needs dedicated throwaway pin in-repo (open) |
| Sources | Electrum history; pybitcointools `electrum_*`; StackExchange writeups |
| Notes | Stock addresses **uncompressed**. As `K[i]` before `T`, not eliminated (`SOURCE_SEQUENCE_REASSESSMENT.md`). |

### G04 — Armory HD CKD (locked)

| | |
|--|--|
| Formula | `I=HMAC-SHA512(chain, uncomp_pub‖BE32(i))`; `k'=(IL×k) mod n`; public: `K'=IL×K` |
| Index | 0-based `M/account/chain/i` |
| Change | `HDW_CHAIN_EXTERNAL=0`, `HDW_CHAIN_INTERNAL=1` |
| Vector | **Yes** — etotheipi gist 2012-04-27 `ckd_output.txt` (`armory_chain_selftest.py` PASS) |
| Sources | `ARMORY_VECTOR_LOCK.md`; https://gist.github.com/etotheipi/2513316 |
| Notes | Locks **ChildKeyDeriv** CKD (multiply), not BIP32-add. Older product “classic sequential” docs are related history; this vector is the exact published lock. |

### G05 — BIP32

| | |
|--|--|
| Formula | Master `HMAC-SHA512(key="Bitcoin seed", msg=seed)`; CKD add `I_L` |
| Index | Path indices (often 0-based) |
| Change | Conventionally path level (BIP44 later) |
| Vector | **Yes** — BIP32 mediawiki test vectors (2013+) |
| Sources | BIP 32 assigned **2012-02-11** |
| Notes | Usable wallets by late 2014 (Electrum 2 plans, Mycelium HD, Trezor, etc.). Creator did **not** use BIP32 jargon. |

### G06 / G07 — Maxwell Type-1 / Type-2

| | |
|--|--|
| Formula | Type-1: `H(n\|S\|type)`; Type-2: `master + H(n\|S\|type)` |
| Index | Sequence `n` |
| Change | `type` field |
| Vector | Conceptual / forum; serialization not unique |
| Sources | gmaxwell 2011 posts; BIP32 motivation cites Type-2 / Armory |
| Notes | Best **linguistic** match to “deterministic wallet” in 2011 dialect. |

### G08 / G09 — bitaddress.org

| | |
|--|--|
| Brain formula | `SHA256(passphrase)` → one privkey (CHANGELOG v1.4 / v1.6) |
| Bulk formula | Independent RNG keypairs → CSV |
| Index / change | Brain: none; Bulk: none (not seed-chained) |
| Vector | Brain: public weak phrases (do not reuse) |
| Fit | Brain **Low** (not consecutive). Bulk **None** as deterministic consecutive source. |
| Notes | Forum users discussed `pass+n` as DIY; **not** stock bitaddress brain. |

### G10 / G11 — brainwallet.org & Type-1 clones

| | |
|--|--|
| Stock brainwallet.org | Typically `SHA256(pass)` single |
| Indexed clones | e.g. `SHA256(pass ‖ str(i))` with **i from 0** (brainvault README) |
| Change | Usually no |
| Vector | Occasional README examples; CHBS folklore address |
| Fit | Indexed clones **Medium–High**; single-key **Low** |
| Notes | C1-like but often **0-based** and no `/BITCOIN` — distinct from Casascius C2. |

### G12 — pybitcointools

| | |
|--|--|
| Formula | Wraps Electrum stretch/seq + BIP32 |
| Index / change | Same as Electrum / BIP32 |
| Vector | Library-level |
| Fit | High as **implementation host**, not a unique family |

### G14 — Mycelium HD (≤ puzzle date)

| | |
|--|--|
| Available | HD BIP32/39/44 announced **2014-10-07** — before puzzle |
| Formula | Standard BIP44 account paths |
| Fit | Medium (possible; creator language not BIP44) |
| Vector | BIP39/44 |

### G15 — Schildbach Bitcoin Wallet

| | |
|--|--|
| Early | Non-deterministic key pool dominant pre-HD |
| Fit | Low for “deterministic wallet” wording |

### G16 — libbitcoin

| | |
|--|--|
| Status | **Open** — pin tag ≤2015-01-15 for Electrum-v1 / BIP32 modules |
| Fit | Medium–High once pinned |

### G18 — Custom indexed SHA

| | |
|--|--|
| Formula | Any author script; includes Casascius-like and Maxwell-like |
| Fit | High structurally |
| Puzzle link | None unless archive shows the script |

---

## Exact shortlist after gates (2026-07-20)

Gates: (1) pre-2015-01-15 (2) consecutive det. keys (3) ≥256 export (4) source+vector (5) Puzzle/creator document link.

| ID | Family | Gates 1–4 | Gate 5 | Action |
|----|--------|-----------|--------|--------|
| G01/G02 | Casascius C1/C2 | **Pass** | Fail | Technical candidate; **no seed scan** |
| G03 | Electrum 1.x | **Pass** (`ELECTRUM_V1_VECTOR_LOCK.md` PASS) | Fail | Technical candidate; **no seed scan** |
| G04 | Armory HD CKD | **Pass** (`ARMORY_VECTOR_LOCK.md` PASS) | Fail | Technical candidate; **no seed scan** |
| G05–G18 | others | fail ≥1 of 1–4 or too wide | Fail | Closed / background |

**Three exact families locked:** Casascius, Electrum 1.x, Armory. See `GENERATOR_DIFFERENTIAL_AUDIT.md`.  
**Seed/Puzzle comparison opens only if Gate 5 gets primary evidence.**

---

## Fit vs creator description (summary)

**Best structural + linguistic matches (still no Puzzle link):**

1. Casascius C1/C2 (bulk consecutive, 2011, export)  
2. Electrum 1.x / Type-2  
3. Armory HD CKD (tree consecutive; multiply CKD)  
4. gmaxwell Type-1 indexed hash families  
5. BIP32 (possible; less matching vocabulary)  
6. Indexed brainwallet clones (`pass‖i`)  

**Weak / eliminate as sole `K[i]` source:**

- Stock bitaddress **Bulk** (random CSV)  
- Single-key brainwallet without index  
- BIP38 (encrypts; does not invent consecutive puzzle series)  

---

## Research queue (census work only)

| Priority | Task | Output |
|----------|------|--------|
| 1 | Differential use of three locks (no seed scan) | `GENERATOR_DIFFERENTIAL_AUDIT.md` |
| 2 | Catalog **deleted/rare** Bitcointalk attachments: “deterministic paper wallet”, “bulk generator”, PHP/C# scripts | New G-IDs |
| 3 | Pin **libbitcoin** electrum_v1 / hd modules at 2014 tag | Fill G16 |
| 4 | Compare **0-based vs 1-based** Type-1 clones to Casascius | Avoid false “C1 tested” claims |
| 5 | Mycelium / breadwallet BIP44 first-address vectors (control only) | G14 |

**Do not:** open phrase grind, timestamp expansion, or “run all generators against #71” without a justified seed.

---

## Honest bound

Still missing for a “solve command”:

1. exact **generator** identity,  
2. exact **seed**,  
3. exact mask **`T`**.

Census targets (1). Seed and `T` stay closed until primary evidence.

---

## Cross-links

- `CASASCIUS_BAU_DOSSIER.md` / `CASASCIUS_BAU_ARCHAEOLOGY.md`  
- `LEGACY_ELECTRUM_DOSSIER.md` / `ARMORY_DOSSIER.md`  
- `SOURCE_SEQUENCE_REASSESSMENT.md`  
- `CASCADE_COVERAGE.md`  
- `EVIDENCE_CANDIDATES.md`  
- `FUNDING_SIBLING_CLUSTER.md` (operator context; not generator)  
