# Creator Archive — CLOSED PASS (2026-07-20)

Bu dosya açık web / forum arşiv geçidini **kapatır**. Cascade yeniden açılmaz; yalnızca aşağıdaki kanıt sınıflarından biri gelirse.

## Kesin kayıtlar (doğrulanmış)

### saatoshi_rising

| Madde | Sonuç |
|-------|--------|
| Doğrulanmış post sayısı | **1** (2017-04-27, topic=1306983) |
| İkinci creator postu | **Bulunamadı** |
| Adres #256 ile imzalı mesaj | **Bulunamadı** |
| Redistribution | Önceden açıklandı → 2017-07-11 zincirde `5d45587c…` gerçekleşti |
| Bağlantı ifadesi | Hesabın *gerçek kişi* kimliği doğrulanmış **değil**; fakat önceden duyurulan redistrib’in zincirde olması, hesabı puzzle anahtarlarını kontrol eden kişiyle **güçlü operasyonel** bağlar |
| “Saatoshi = Satoshi Nakamoto” | **Spekülasyon** — güvenilir kanıt yok (yazım, çift boşluk, kullanıcı adı vb. spekülasyon) |

Kaynaklar: profil/thread `topic=1306983.msg18687273`; redistrib mempool `5d45587cfd1d5b0fb826805541da7d94c61fe432259e68ee26f4a04544384164`.

### Funding adresleri — açık web

| Adres | Sonuç |
|-------|--------|
| `1Czoy8xtddvcGrEhUUCZDQ9QqdRfKh697F` | İndekslenmiş forum/Reddit’te anlamlı 2015 izi **yok**; explorer sayfaları hakim |
| `173ujrhEVGqaZvPHXLqwXiSmPVMo225cqT` | Aynı |
| İlk büyük kullanım | Funding TX → puzzle TX (bkz. `FUNDING_PROVENANCE.md`) |
| Sonraki küçük transferler | Dust olasılığı; creator kimliğiyle **ilişkilendirilemez** |

**Kapsam notu:** Yokluk kanıtı değildir — yalnızca indekslenmiş açık web taraması.

### Aynı output düzeninde başka 2015 TX

Genel aramada şu fingerprint’in tamamını paylaşan ikinci örnek **görülmedi**:

- 256× P2PKH  
- değerler 0.001…0.256 BTC  
- toplam 32.896 BTC  
- compressed adresler  
- aynı gün 32.9 BTC staging  

**İfade:** “Başka örnek bulunamadı” — “başka örnek yoktur” **denemez** (tam zincir taraması yapılmadı).  
Güvenli sonraki araştırma: `TX_STRUCTURE_FINGERPRINT.md`.

---

## Hipotez durumu (2026-07-20) — olasılık değil, kanıt durumu

| ID | Hipotez | Statü |
|----|---------|--------|
| H0 | Casascius BAU C1/C2 | **Somut tarihsel aday**; Puzzle bağı yok; C2 R1–R7’de yok |
| H1 | gmaxwell / custom Type-1 | Tarihsel dil uyumu; Puzzle bağı yok |
| H2 | Generic Type-2 | Exact yok |
| H3 | BIP32 erken | Dar path test; elenmedi |
| H4 | Armory kaynak `K[i]` | **Elenmedi; pozitif kanıt yok** |
| H5 | Electrum v1 kaynak `K[i]` | **Elenmedi; pozitif kanıt yok** |
| H6 | BIP39/44 | Düşük öncelik / dar dışı |

---

## Program statüsü

| Hat | Statü |
|-----|--------|
| Bulk cascade / phrase grind | **Kapalı** |
| Native random | **Kapalı** |
| Casascius C2 self-test | **PASS** |
| Puzzle ↔ Casascius karşılaştırması | **Açılmadı** (justified passphrase yok) |
| Electrum/Armory seed tarama | **Kapalı** |

**Kazanım:** hangi exact formülün test edilmediği biliniyor (`CASCADE_COVERAGE.md`).

## Cross-links

- `CASCADE_COVERAGE.md`  
- `CASASCIUS_BAU_DOSSIER.md`  
- `CASASCIUS_BAU_ARCHAEOLOGY.md`  
- `TX_BUILDER_FINGERPRINT.md`  
- `WALLET_BUILDER_COMPARISON.md`  
- `HISTORICAL_BUILDER_REPRODUCTION.md`  
- `FUNDING_SIBLING_CLUSTER.md`  
- `EVIDENCE_CANDIDATES.md`  
- `SOURCE_SEQUENCE_REASSESSMENT.md`  
- `FUNDING_PROVENANCE.md`  
- `PUBKEY_FINGERPRINT.md`  
- `LEGACY_ELECTRUM_DOSSIER.md`  
- `ARMORY_DOSSIER.md`  
- `TX_STRUCTURE_FINGERPRINT.md`  
- `NEGATIVE_RESULTS.md`
