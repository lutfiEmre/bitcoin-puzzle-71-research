# Casascius Bitcoin Address Utility (BAU) — Dossier

Last updated: 2026-07-20  
**No passphrase brute-force. No claim that Casascius/Mike Caldwell created the Puzzle.**

## What this is

2011-era open-source **deterministic bulk key generator** by Mike Caldwell (Casascius):

- GitHub: https://github.com/casascius/Bitcoin-Address-Utility  
- Blog: https://casascius.wordpress.com/2013/01/26/bitcoin-address-utility/  
- Forum lineage: Bitcointalk announcements from **July/August 2011** (“Bitcoin Address Utility I made”)

Fits creator language (“deterministic wallet”, consecutive keys) as a
**concrete historical generator candidate** — not “high probability,” not authorship.

## Exact formulas (source: `Forms/Walletgen.cs`)

Loop: `for (int i = 1; i <= n; i++)` — **1-based**.

```csharp
switch (GenerationFormula) {
  case 1:
    privatestring = txtPassphrase.Text + i.ToString();
    break;
  default: // GenerationFormula == 0 after double-click on formula label
    privatestring = i.ToString() + "/" + txtPassphrase.Text + "/" + i.ToString() + "/BITCOIN";
    break;
}
byte[] privatekey = Util.ComputeSha256(privatestring);
KeyPair kp = new KeyPair(privatekey);
```

Default field (HEAD / post-2012-11-07): `private int GenerationFormula = 1;` → **C1 default**.  
Alternate (`lblFormula_DoubleClick`): `GenerationFormula = 0` → **C2**.

**Era note (git archaeology):** 2011-08-03 initial = **C2 only**; 2011-09-09–2012-11-06 = C2 default + C1 via double-click; after `8b09119` (2012-11-07) = **C1 default**. Details: `CASASCIUS_BAU_ARCHAEOLOGY.md`.

| ID | Formula | Default UI (HEAD)? | Default UI (2011)? |
|----|---------|-------------------|---------------------|
| **C1** | `SHA256(passphrase ‖ decimal(i))` | Yes | No (absent until 2011-09-09) |
| **C2** | `SHA256(decimal(i) ‖ "/" ‖ passphrase ‖ "/" ‖ decimal(i) ‖ "/BITCOIN")` | Double-click | **Yes** (only/default) |

UTF-8 passphrase text as typed; index as **decimal ASCII** (not u32be).

## Published 2011 test vector (independently re-verified here)

Passphrase (with trailing period):

```text
Sample passphrase that should not be used for any real Bitcoin money transactions.
```

Published WIF #1:

```text
5JwH8jmznh4RbyMBYXMwzPL45pnr8FW9TtwunSKfTz1ibyao8Ym
```

| Formula | Match published WIF #1? |
|---------|-------------------------|
| C1: `SHA256(passphrase + "1")` | **No** |
| C2: `SHA256("1/" + passphrase + "/1/BITCOIN")` | **Yes** (byte-identical WIF) |

Priv hex (C2, i=1):

```text
9392ac4225ccee1814c5e0958778dd5d2eeaf44cd2936bf15d632e7dbbf0a3f7
```

Without trailing `.` on passphrase → C2 **fails**. Period is required for this vector.

## Passphrase UX (why phrase hunting stays closed)

`Walletgen_Shown`: fills ~**80** chars from `RandomNumberGenerator` over alphabet  
`123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz*#_%+!`

Also warns if passphrase `< 20` chars or “too simple” (`Util.PassphraseTooSimple`).

**Implication:** Normal use ⇒ high-entropy random string, **not** natural-language / TX timestamps. Finding this dossier ≠ open million-phrase cascade.

## Export / TX role

CSV / import-script / paper listing — **key export only**.  
BAU **does not** create or broadcast transactions (`CASASCIUS_BAU_ARCHAEOLOGY.md`).  
`KeyPair(bytes)` default → **uncompressed** addresses; puzzle final `A[i]` are compressed → separate rebuild required even if BAU supplied `K[i]`.

## Authorship boundary

| Claim | Status |
|-------|--------|
| Tool existed 2011+ and matches “deterministic consecutive keys” | **Verified** |
| Formula C2 matches published sample WIF | **Verified** |
| BAU built puzzle/funding TX | **No** (source) |
| Casascius / Caldwell = puzzle creator | **No evidence** |
| Puzzle used C1 or C2 | **Unknown** |

## Cascade coverage → `CASCADE_COVERAGE.md`

**Bottom line:** C2 never in R1–R7. C1 not dedicated. Puzzle comparison **not opened**
(no justified passphrase). Self-test locks formula only: `casascius_vector_selftest.py`.

## Allowed next step (narrow)

1. Keep C1/C2 documented + published-WIF self-test.  
2. Do **not** launch passphrase search.  
3. Justified archive passphrase only → single-string C1/C2 test under hypothesized `T` — still not bulk guessing.
