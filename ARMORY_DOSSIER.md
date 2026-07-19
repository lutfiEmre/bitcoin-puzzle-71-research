# Armory Legacy — Source Dossier

Last updated: 2026-07-20  
**Seed / root-key taraması yok.** Yalnızca tarihsel davranış belgesi.

## Neden şimdi

Armory 2012–2015’te ciddi deterministic wallet adayıydı.  
**2026-07-20:** Compressed Puzzle fingerprint, Armory’yi **kaynak `K[i]` dizisi** olarak elemez (`SOURCE_SEQUENCE_REASSESSMENT.md`). Seed hattı hâlâ kapalı.

## Deterministik zincir (kaynaklı)

etotheipi / GitHub issue #204 özeti:

1. Root private key → chain code türetilir (sürümde: root’tan deterministik derive).  
2. Address pair **N+1**, pair **N**’den scalar ile:  
   `scalar = SHA256(SHA256(pubKey_N)) XOR chaincode`  
3. Private ve public, bu scalar ile çarpılarak bir sonraki çift üretilir.  
4. Root tek başına tüm cüzdanı yeniden kurabilir; chaincode + first pubkey → watch-only zincir.

Kod referansları (upstream):

- `EncryptionUtils.cpp`: `ComputeChainedPrivateKey` / `ComputeChainedPublicKey`  
- `armoryengine/PyBtcWallet.py` — deterministic wallet notları  
- Issue: https://github.com/etotheipi/BitcoinArmory/issues/204  

Chaincode derive (yaygın rekonstrüksiyon / tartışma):

- Mesaj: `"Derive Chaincode from Root Key"`  
- HMAC-SHA256 tabanlı; Armory’nin eski HMAC parametrelerinde bilinen **non-RFC quirk** tartışması var (Bitcointalk “deriving chaincode from root privkey”) — reimplementation’da **Armory’nin kendi HMAC’i** kullanılmalı, “doğru RFC HMAC” değil.

## Compressed / uncompressed (kritik fingerprint)

Bitcointalk thread “Does Armory use compressed keys?” (`topic=197715`):

- etotheipi (dönem): **Armory wallets have not supported compressed keys yet**; yeni wallet formatına ertelenmiş.  
- Endişe: yanlışlıkla yanlış HASH160’a gönderim riski; muhafazakâr test süreci.

**Sonuç (tarihsel):** Puzzle TX tarihi (2015-01-15) civarında **stock Armory address pool’unun compressed P2PKH üretmesi beklenmez** (en azından klasik pre-HD wallet hattı için).  

BIP32 / Wallet2.0 çalışmaları 2013–2014’te PR olarak vardı (`Wallet2.0` PR #161, merge ~2014-02); **hangi release’in compressed adresi varsayılan yaptığı** bu dosyada **pin’lenmedi** — takip maddesi.

| Karşılaştırma | Stock Armory (klasik zincir) | Puzzle (82/82 solved) |
|---------------|------------------------------|------------------------|
| Address pubkey | Dönem kaynaklarına göre **uncompressed** yönelim | **Compressed** |
| Fit | **Zayıf** (stock) | — |

| Rol | Statü |
|-----|--------|
| Stock Armory UI = final Puzzle address exporter | Zayıf (uncompressed default) |
| Stock Armory = source `K[i]` → unknown `T` | **Elenmedi; pozitif kanıt yok** |

Custom Armory fork / zincir + compressed export: **elenmedi**, kanıtsız.

## Index / address pool

- Sıralı zincir: pair 0, 1, 2… (root’tan ileri)  
- Puzzle #1 ↔ Armory index 0/1 mapping: **creator bilinmiyor**  
- Transaction builder’ın 256 aritmetik output üretmesi Armory UI’nin tipik davranışı değil → yine **özel script** daha doğal

## Backup formatı

- Root / paper backup: EasyType16 vb. (PyBtcWallet `getRootPKCCBackupData`)  
- Puzzle ile bağlantı: **yok**

## Puzzle ile yapılmaması gerekenler

- Root key brute-force  
- Chaincode tahmin  
- “Armory seed tarama” cascade modu  

## Tamamlanacak arşiv maddeleri (belge, kod değil)

- [ ] 2015-01-01 öncesi son **stable** Armory sürüm tag’i  
- [ ] O tag’de `createNewAddress` / HASH160 compressed flag satır referansı  
- [ ] Wallet2.0 / BIP32 Armory hattının ilk compressed-default release’i  
- [ ] Bilinen throwaway test wallet → ilk 5 adres (bağımsız reimplementation doğrulaması)

## Statü

**Dossier: kısmi.**  
Final-exporter zayıf; kaynak `K[i]` olarak **elenmedi, pozitif kanıt yok**.  
Cross-link: `SOURCE_SEQUENCE_REASSESSMENT.md`, `CASCADE_COVERAGE.md`.
