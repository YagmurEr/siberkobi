# SiberKOBİ Mimari Notları

## Hedef

SiberKOBİ; üyelik, veritabanı veya harici API gerektirmeden çalışabilen, 25 soruluk deterministik bir siber güvenlik öz değerlendirme uygulamasıdır.

## Modüller

- `assessment`: soru seti ve veri yükleme
- `evaluation`: deterministik değerlendirme ve kategori sonuçları
- `reporting`: HTML raporlama için ayrılmış modül sınırı
- `web`: HTTP route ve template katmanı
- `config`: yapılandırma sınırı

## Veri akışı

1. Soru seti JSON'dan yüklenir.
2. Kullanıcı Evet / Kısmen / Hayır, yalnız izin verilen sorularda Uygulanamaz yanıtı verir.
3. Evaluation engine yanıt kümesini tamlık ve izin kuralları açısından doğrular.
4. Sonuç toplam ve kategori bazında hesaplanır.
5. HTML sonuç ekranı iyileştirme gerektiren maddeleri listeler.

## Puanlama

- Evet = 2
- Kısmen = 1
- Hayır = 0
- Uygulanamaz yalnız SK-T01, SK-T13, SK-T19, SK-T20 ve SK-T21 için kullanılabilir.
- Uygulanamaz yanıtlar payda ve azami puandan çıkarılır.

Sonuç bantları:

- %0–33.33: Temel güvenlik kontrolleri geliştirilmeli
- >%33.33–66.66: Güvenlik hazırlığı kısmen sağlanmış
- >%66.66–100: Temel güvenlik kontrollerinde olumlu görünüm

## Güvenlik sınırları

- İlk sürümde kullanıcı hesabı ve kalıcı kişisel veri depolama yoktur.
- Form girdileri allow-list ile doğrulanır.
- Harici AI/API bağımlılığı yoktur.
- Secret gerektiren konfigürasyon kullanılmaz.
- Public release öncesinde bağımlılık, secret ve lisans kontrolleri zorunludur.
