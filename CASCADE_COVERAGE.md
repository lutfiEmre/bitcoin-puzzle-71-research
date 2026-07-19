# Cascade Coverage Matrix (R1–R7)

Last updated: 2026-07-20  
Source of truth for “was this exact family tested?” — not probability rankings.

Masking in cascade uses hypothesized `mask_be` / `mask_le` helpers. Creator’s real
transform `K → P` is **unknown** (see `SOURCE_SEQUENCE_REASSESSMENT.md`). Coverage
below is about **source-key material formulas only**.

| Aile | Exact material | R1–R7 kapsıyor mu? |
|------|----------------|--------------------|
| Casascius C1 | `SHA256(passphrase ‖ decimal(i))`, `i≥1` | **Kısmi / formula-exact on some jobs.** `indexed_wallet_at("sha_seed_ascii")` = `sha256(seed + str(n).encode())` — byte-identical to C1 when `seed` is raw passphrase (`phrase_seeds()` raw branch). R1 `--mode indexed --phrases` bu formülü o phrase listesi × puzzle-index/offset ile çalıştırdı. **Dedicated Casascius C1 değil:** C2 layout yok; index Casascius `i` ile eşleşmesi kanıtlı değil; yayımlanmış BAU vektör passphrase’i listede yok. |
| Casascius C2 | `SHA256(decimal(i) ‖ "/" ‖ passphrase ‖ "/" ‖ decimal(i) ‖ "/BITCOIN")` | **Hayır** — hiç implement edilmedi / R1–R7’de yok. Vektör kilidi: `casascius_vector_selftest.py` (PASS). |
| GMaxwell Type-1/2 | Program: layouts `n_S_t,n_t_S,S_n_t,t_n_S`; `n_ser` u32be/u32le/ascii; `type_id` 0/1; t1/t2 | **Kısmi** — Maxwell’in forum/wiki exact serileştirmesinin tüm yorumları yok; type string (`receiving`/`change`) yok. |
| Electrum v1 | Historical: 128-bit/32-hex + ~100k stretch + seq | **Kısmi** — material çoğunlukla `sha256(phrase)[:16].hex()`; gerçek rastgele hex seed uzayı yok; throwaway Electrum vektörüyle kilitlenmedi. |
| Armory | Exact historical root+chaincode HMAC chain | **Test edilmedi** |
| BIP32 | Paths `m/i`, `m/0/i`, `m/0'/i` only | **Dar kapsam** — BIP44 vb. yok |

### C1 byte-level pin (`generator_cascade.py`)

```text
sha_seed_ascii:  sha256(seed + str(n).encode())     ← C1 iff seed == raw passphrase
sha_seed_u32be:  sha256(seed + u32be(n))             ← not C1
sha256(phrase) as seed + ascii index                 ← not C1 (hashed seed)
C2 i/pass/i/BITCOIN                                  ← absent
```

## Statü (tek cümle)

Casascius C2’nin daha önce test edilmediği doğrulandı; C1 formülü `sha_seed_ascii`+raw phrase ile bazı R1 job’larında byte-exact koştu ama dedicated Casascius/Puzzle karşılaştırması değil. Tarihsel gerekçeli passphrase yok → Puzzle karşılaştırması **açılmadı**.

## Cross-links

- `CASASCIUS_BAU_DOSSIER.md` — somut tarihsel aday (Puzzle bağı yok)  
- `SOURCE_SEQUENCE_REASSESSMENT.md` — eleme geri alma ≠ pozitif kanıt; mask bilinmiyor  
- `NEGATIVE_RESULTS.md` — R1–R7 dar negatifler  
- `casascius_vector_selftest.py` — C2 implementasyon kilidi  
