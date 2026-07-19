# Puzzle #71 — Negatif / Kısmi Test Kayıtları

Son güncelleme: 2026-07-20

Bu dosya “hipotez elendi” iddiası **taşımaz**.  
Her satır yalnızca: *şu merkez × şu kodlama × şu derivation × şu pencere → hit yok* anlamına gelir.

**2026-07-20:** Casascius C2 ve kaynak-dizi metodolojisi için → `CASASCIUS_BAU_DOSSIER.md`, `SOURCE_SEQUENCE_REASSESSMENT.md`.

## Statü etiketleri

| Etiket | Anlam |
|--------|--------|
| Test edilmedi | Hiç koşulmadı |
| Kısmen test edildi | Ailenin küçük bir alt kümesi koşuldu |
| Dar modelde negatif | Uygulanan parametrelerde hit=0; genel eleme değil |
| Bağımsız doğrulandı | Aynı sonuç bağımsız yeniden üretildi |
| Güvenilir biçimde elendi | Tüm tarihsel varyantlar + kodlamalar + mapping kapsandı (şu an **yok**) |

---

## Seed merkezi (bilinen)

| Merkez | Değer | Not |
|--------|-------|-----|
| Puzzle TX Unix (UTC) | `1421345234` | 2015-01-15 18:07:14 UTC civarı (`TX_TS` in `generator_cascade.py`) |
| Block | `339085` | |
| TXID | `08389f34c98c606322740c0be6a7125d9860bb8d5cb182c02f98461e5fa6cd15` | |
| Funding UTXO oluşum zamanı | — | **Test edilmedi** (TX zamanından farklı olabilir) |

---

## Koşu kayıtları

### R1 — Phrase seeds × indexed / chain / electrum / gmaxwell / bip32

| Alan | Değer |
|------|--------|
| Seed’ler | `phrase_seeds()` listesi (ascii + sha256(ascii)); ~18–30 etiket |
| Kodlama | ham UTF-8 bytes; ayrıca `sha256(phrase)` |
| Pencere | yok |
| Mask | `mask_be` (bazı koşularda `mask_le` de denendi — aşağı) |
| Sonuç | hits=0 |
| Statü | **Dar modelde negatif** |

Alt koşular (özet):

- `--mode quick --phrases` → hits=0  
- `--mode chain --phrases --start-max 128` → hits=0  
- `--mode indexed --phrases --mask mask_be,mask_le` → hits=0  
- `--mode electrum --phrases --electrum-rounds 1` ve `100000 --start-max 64` → hits=0  
- `--mode gmaxwell --phrases` → hits=0 (2880 job)  
- `--mode bip32 --phrases` → hits=0 (180 job)  

**Kapsam dışı:** rastgele 128-bit Electrum hex seed uzayı; Armory root+chaincode; BIP44 full tree; uncompressed Electrum fingerprint doğrulaması.

---

### R2 — TX_TS ±24h × indexed (yalnız `ts4be`)

| Alan | Değer |
|------|--------|
| Merkez | `1421345234` |
| Pencere | ±86400 s (`--timestamp-hours 24`) |
| Seed kodlaması | **yalnız** `ts4be` = `ts.to_bytes(4, "big")` |
| Derivation | `INDEXED_FAMILIES` (SHA/HMAC varyantları) |
| Index offset | −2..+2 |
| Mask | `mask_be` |
| Jobs | ~13.8M |
| Sonuç | hits=0 |
| Statü | **Dar modelde negatif** |

**Kapsam dışı:** `ts4le`, `ts8be/le`, decimal ASCII, ISO-8601, ms timestamp, gmaxwell/bip32/electrum bu pencerede.

---

### R3 — TX_TS ±72h × indexed (`ts4be`)

| Alan | Değer |
|------|--------|
| Merkez | `1421345234` |
| Pencere | ±259200 s |
| Seed kodlaması | yalnız `ts4be` |
| Derivation | indexed families |
| Mask | `mask_be` |
| Jobs | ~41.5M |
| Sonuç | hits=0 (~144s) |
| Statü | **Dar modelde negatif** |

---

### R4 — TX_TS ±6h × gmaxwell

| Alan | Değer |
|------|--------|
| Merkez | `1421345234` |
| Pencere | ±21600 s |
| Seed kodlaması | yalnız `ts4be` |
| Derivation | gmaxwell Type-1/Type-2: layouts `n_S_t,n_t_S,S_n_t,t_n_S`; `n_ser` u32be/u32le/ascii; `type_id` 0/1; `variant` t1/t2 |
| Index | `idx_mode` `n` ve `n0` |
| Mask | `mask_be` |
| Jobs | 4,147,296 |
| Sonuç | hits=0 (~4.4s) |
| Statü | **Dar modelde negatif** |

**Kapsam dışı:** diğer timestamp kodlamaları; type string (`receiving`/`change`); Maxwell’in orijinal serialization’ının tüm yorumları; Type-2’nin Electrum/Armory eşdeğerleri.

**Not (bug, düzeltilmiş):** Daha önce `gmaxwell` timestamp seed’lerini filtreleyip neredeyse boş koşabiliyordu. R4, düzeltme sonrası geçerli koşudur.

---

### R5 — TX_TS ±6h × bip32

| Alan | Değer |
|------|--------|
| Merkez | `1421345234` |
| Pencere | ±21600 s |
| Seed kodlaması | yalnız `ts4be` |
| BIP32 master | `HMAC-SHA512(key="Bitcoin seed", msg=seed_bytes)` |
| Path’ler | yalnız `m/i`, `m/0/i`, `m/0h_i` (`m/0'/i`) |
| Index | `n` ve `n0` |
| Hardened | yalnızca path `m/0h_i` ilk adımında; `m/i'` ve `m/44'/0'/0'/0/i` **yok** |
| Mask | `mask_be` |
| Jobs | 259,206 |
| Sonuç | hits=0 (~2.9s) |
| Statü | **Dar modelde negatif** |

**Kapsam dışı (bu yüzden “BIP32 elendi” DENEMEZ):**

- `m/i'`, `m/44'/0'/0'/0/i`, `m/0'/0'/i`, change branch  
- seed’in UTF-8 decimal / ISO string olarak master’a verilmesi  
- `ts4le` / `ts8*` / ASCII timestamp  
- compressed vs uncompressed adres fingerprint ile aile elemesi  

---

### R6 — Electrum v1 (phrase)

| Alan | Değer |
|------|--------|
| Seed malzemesi | `sha256(phrase)[:16].hex().encode()` (32 ascii hex) — **gerçek Electrum old-seed uzayı değil** |
| Stretch | 1 ve 100000 |
| Formula | `n_change_mpk`, `mpk_n_change`, `n_mpk` |
| change | 0, 1 |
| start_index | 0..32 veya 0..64 |
| Mask | `mask_be` |
| Sonuç | hits=0 |
| Statü | **Kısmen test edildi** → dar modelde negatif |

**Kapsam dışı:** gerçek 128-bit rastgele hex seed; old 12-word; MPK uncompressed fingerprint; tarihsel kaynakla birebir eşleşen seq formülü doğrulaması.  
→ **Electrum elenmedi.**

---

### R7 — `mask_le`

| Alan | Değer |
|------|--------|
| Koşu | indexed + phrases, `mask_be,mask_le` |
| Sonuç | hits=0 |
| Statü | **Kısmen test edildi** |

`mask_le` uygulamadaki LE yorumu, tüm anlamlı little-endian / byte-swap alternatiflerini kapsamaz.  
→ **LE mask hipotezi elenmedi.**

---

## Seed kodlama matrisi (program vs ihtiyaç)

| Kodlama | `generator_cascade.py` durumu | R2–R5’te kullanıldı mı? |
|---------|--------------------------------|-------------------------|
| `ts4be` | Var | Evet |
| `ts4le` | Yok | Hayır — **Test edilmedi** |
| `ts8be` / `ts8le` | Yok | Hayır — **Test edilmedi** |
| decimal ASCII (`str(ts)`) | Yok (phrase listesinde sabit `"1421345234"` var) | Sabit string kısmen; pencere taraması yok |
| ISO-8601 UTC | Yok | **Test edilmedi** |
| milisaniye | Yok | **Test edilmedi** |

---

## Derivation matrisi (özet statü)

| Aile | Statü | Not |
|------|--------|-----|
| Generic indexed SHA/HMAC | Dar modelde negatif (ts4be pencereleri + phrases) | |
| gmaxwell H(n\|S\|type) t1/t2 | Dar modelde negatif (phrases + ts4be±6h) | Layout alt kümesi |
| BIP32 `m/i`, `m/0/i`, `m/0'/i` | Dar modelde negatif (phrases + ts4be±6h) | Path alt kümesi |
| BIP32 BIP44 vb. | **Test edilmedi** | |
| Electrum v1 (kısmi) | Kısmen test edildi / dar negatif | Tam historical değil |
| Armory root+chaincode | **Test edilmedi** | Elenmedi; pozitif kanıt yok |
| Casascius BAU C1 (`pass‖i`) | Dedicated değil | `CASCADE_COVERAGE.md` |
| Casascius BAU C2 (`i/pass/i/BITCOIN`) | **Test edilmedi** (R1–R7) | Self-test PASS; Puzzle karşılaştırması kapalı |
| Iterated hash chain | Dar modelde negatif (phrases, start≤128) | |
| Type-2 “full” | Başlıkta partial — **Kısmen test edildi** | |

---

## Tekrar çalıştırma yasağı (aynı kapsam)

Aşağıdakileri **aynı parametrelerle** yeniden koşup “yine elendi” sanma:

1. `gmaxwell --phrases`  
2. `bip32 --phrases`  
3. `gmaxwell --timestamp-hours 6` (yalnız ts4be)  
4. `bip32 --timestamp-hours 6` (yalnız ts4be)  
5. `indexed --timestamp-hours 24` veya `72` (yalnız ts4be)  
6. `electrum --phrases` (mevcut material encoding)

Yeni koşu ancak **kapsam genişlerse** anlamlıdır (yeni kodlama, path, merkez, mask, implementasyon).

---

## Dürüst özet cümleler

**Doğru:**  
Phrase seed’ler ve TX Unix ±6/24/72 saat içindeki **ts4be** kodlaması ile programda uygulanmış belirli indexed / gmaxwell / bip32 / kısmi electrum parametrelerinde hit çıkmadı.

**Yanlış / fazla güçlü:**  
“gmaxwell / BIP32 / Electrum timestamp-seed hipotezi elendi.”

**Sonuç:**  
Creator güçlü rastgele seed kullandıysa, solved key’lerin maskeli alt bitlerinden seed’i geri kazanmak için bilinen pratik yöntem yoktur. Cascade ancak **yeni tarihsel kanıt** veya **genişletilmiş, belgelenmiş kapsam** ile anlamlıdır.

Native `./run_max.sh --random` = piyango; ipucu değildir.

---

## Araştırma durumu (2026-07-20)

**Bulk cascade / native random / phrase grind: kapalı.**  
**Casascius:** somut tarihsel aday; Puzzle bağı yok; C2 daha önce test edilmedi (doğrulandı).  
**Electrum / Armory:** elenmedi; pozitif kanıt yok — “orta olasılık” iddiası yok.  
**Mask `T`:** bilinmiyor; `mask_be` hipotez.

### Belge seti

| Dosya | Rol |
|-------|-----|
| `CASCADE_COVERAGE.md` | Exact material × R1–R7 matrisi |
| `CASASCIUS_BAU_DOSSIER.md` | 2011 formüller + vektör |
| `SOURCE_SEQUENCE_REASSESSMENT.md` | Eleme geri alma; `T` unknown |
| `casascius_vector_selftest.py` | C2 WIF lock (PASS) |
| `CREATOR_ARCHIVE.md` | Arşiv |
| `PUBKEY_FINGERPRINT.md` | Compressed = **P→A** only |

### Statü cümlesi

Casascius C2’nin daha önce test edilmediği doğrulandı; tarihsel olarak gerekçelendirilmiş passphrase olmadığı için Puzzle karşılaştırması açılmadı. Kazanım: hangi formülün gerçekten test edilmediğinin bilinmesi.  
