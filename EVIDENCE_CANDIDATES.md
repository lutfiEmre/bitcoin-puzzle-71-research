# Evidence Candidates — Primary-Source Strings Only

Last updated: 2026-07-20  
**No bulk scan. No C/D execution.**  
Only A or strong B may be marked “justified for narrow C1/C2 test.”  
Current justified-for-test set: **empty** (no A; BAU sample is B but **not** Puzzle-linked).

## Evidence levels

| Level | Meaning |
|-------|---------|
| **A** | Creator message or on-chain entity directly tied to puzzle/funding |
| **B** | Historical default/demo string of a named tool (software-authentic) |
| **C** | Period-plausible only |
| **D** | Numerology / free guess |

---

## Candidates

### EC-001 — Creator technical description (excerpt)

| Field | Value |
|-------|--------|
| Exact string (reported quote) | `There is no pattern. It is just consecutive keys from a deterministic wallet (masked with leading 000...0001 to set difficulty). It is simply a crude measuring instrument, of the cracking strength of the community.` |
| Date | 2017-04-27 (saatoshi_rising post) |
| Source | Bitcointalk `topic=1306983` / msg attributed to creator account |
| Puzzle/creator link | **Operational** (account claimed creation; redistrib followed) |
| Level | **A** (as *description text*, not as passphrase) |
| Justified for C1/C2? | **No** — this is explanatory prose, not a seed. Substrings as passwords = **D** if scraped into wordlists |

### EC-002 — Distinctive creator fragments (not full sentences)

| Field | Value |
|-------|--------|
| Exact strings | `crude measuring instrument` · `cracking strength of the community` · `deterministic wallet` (phrase as used by creator) |
| Date | 2017-04-27 |
| Source | Same creator post |
| Puzzle link | A as *vocabulary*; as passphrase → still speculative |
| Level | **A** (origin) / **D** (if used as seed without further proof) |
| Justified for C1/C2? | **No** |

### EC-003 — Casascius BAU published sample passphrase

| Field | Value |
|-------|--------|
| Exact string | `Sample passphrase that should not be used for any real Bitcoin money transactions.` (trailing period required for published WIF) |
| Date | 2011 (forum sample; formula in git `591eb23`+) |
| Source | Casascius BAU documentation / forum sample; C2 self-test PASS in-repo |
| Puzzle/creator link | **None** |
| Level | **B** (authentic tool demo) |
| Justified for C1/C2 vs Puzzle? | **No** — strong B for *formula lock*, not for Puzzle. Already known to produce throwaway keys, not puzzle addresses |

### EC-004 — BAU UI formula label text

| Field | Value |
|-------|--------|
| Exact string | `Generation formula: PrivKey = SHA256(n + "/" + passphrase + "/" + n + "/BITCOIN) where n = "1" thru "10"` |
| Date | 2011-08-03+ (`Walletgen.Designer.cs`) |
| Source | BAU source |
| Puzzle link | None |
| Level | **B** |
| Justified for C1/C2? | **No** (meta-label, not a passphrase) |

### EC-005 — BAU random alphabet (not a passphrase)

| Field | Value |
|-------|--------|
| Exact string | `123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz*#_%+!` |
| Date | 2011+ `Walletgen_Shown` |
| Source | BAU source |
| Puzzle link | None |
| Level | **B** (alphabet for CSPRNG fill) |
| Justified for C1/C2? | **No** — charset, not seed |

### EC-006 — Funding / puzzle addresses as “strings”

| Field | Value |
|-------|--------|
| Exact strings | `1Czoy8xtddvcGrEhUUCZDQ9QqdRfKh697F` · `173ujrhEVGqaZvPHXLqwXiSmPVMo225cqT` · TXIDs |
| Date | 2015-01-15 |
| Source | Chain |
| Puzzle link | **A** as *entities* |
| Level | **A** (chain) / **D** as passphrase material |
| Justified for C1/C2? | **No** |

### EC-007 — Username `saatoshi_rising`

| Field | Value |
|-------|--------|
| Exact string | `saatoshi_rising` |
| Date | Account 2017-04-27 |
| Source | Bitcointalk |
| Puzzle link | Operational A for *identity handle* |
| Level | **A** (handle) / **D** as seed |
| Justified for C1/C2? | **No** |

### EC-008 — Period slogans (examples only — do not expand)

| Field | Value |
|-------|--------|
| Examples | `bitcoin puzzle`, `Large Bitcoin Collider`, ISO date `2015-01-15` |
| Level | **C** or **D** |
| Justified for C1/C2? | **No — do not run** |

---

## Narrow-test gate

| Requirement | Status |
|-------------|--------|
| A or strong B **and** plausible as passphrase **and** Puzzle link | **None present** |
| Open C1/C2 cascade | **Forbidden** |
| Re-test EC-003 under Puzzle mask | **Forbidden** (known throwaway; no Puzzle link) |

---

## Result

**Pozitif Puzzle↔string bağlantısı bulunamadı.**  
A-level material exists only as creator *prose* / chain *identifiers*, not as justified passphrases.  
Strong B exists for BAU demo/formula lock only.

## Cross-links

- `CASASCIUS_BAU_ARCHAEOLOGY.md`  
- `CASASCIUS_BAU_DOSSIER.md`  
- `CREATOR_ARCHIVE.md`  
- `TX_BUILDER_FINGERPRINT.md`  
