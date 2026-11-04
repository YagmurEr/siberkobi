# SiberKOBİ Mimari Notları

## Hedef

SiberKOBİ; üyelik, veritabanı, harici AI sağlayıcısı veya API anahtarı
gerektirmeden çalışabilen bir öz değerlendirme ve sınırlı dış görünürlük
analizi uygulamasıdır. Web Analiz ve SEO Analiz modülleri, kullanıcının
yetkilendirme onayıyla dış hedeflere ağ isteği gönderir.

## Modüller

- `assessment`: soru seti ve veri yükleme
- `evaluation`: deterministik değerlendirme ve kategori sonuçları
- `reporting`: HTML raporlama için ayrılmış modül sınırı
- `web`: HTTP route ve template katmanı
- `webscan`: DNS, TCP, HTTP/HTTPS ve TLS tabanlı Web Analiz
- `seoaudit`: herkese açık sayfa işaretlemeleri ve sınırlı iç bağlantılar için
  SEO Analiz
- `config`: yapılandırma sınırı

## Veri akışı

1. Öz değerlendirmede soru seti JSON'dan yüklenir.
2. Kullanıcı Evet / Kısmen / Hayır, yalnız izin verilen sorularda Uygulanamaz yanıtı verir.
3. Kullanıcı değerlendirmeyi kendi kurumu, sistemleri veya değerlendirme yapmaya yetkili olduğu ortam için kullandığını onaylar.
4. Backend kullanım onayını ve yanıt kümesini doğrular.
5. Evaluation engine yanıt kümesini tamlık ve izin kuralları açısından doğrular.
6. Sonuç toplam ve kategori bazında hesaplanır.
7. HTML sonuç ekranı iyileştirme gerektiren maddeleri listeler.

Web Analiz ve SEO Analiz için ayrı veri akışı kullanılır: kullanıcı hedefi ve
yetki onayını gönderir; backend hedefi doğrular, yalnız tanımlı sınırlı
kontrolleri yürütür ve sonucu kalıcı olarak saklamadan HTML rapor olarak döner.
Tam ağ kapsamı `SCAN_SCOPE.md` içinde belgelenmiştir.

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

## Veri saklama modeli

SiberKOBİ varsayılan olarak stateless çalışır.

- Değerlendirme yanıtları kalıcı olarak saklanmaz.
- Tarama/değerlendirme geçmişi oluşturulmaz.
- Sunucuda HTML/PDF rapor arşivi tutulmaz.
- Flask session kullanılmaz ve değerlendirme sonucu için session cookie oluşturulmaz.
- Kullanıcı raporu tarayıcı üzerinden yazdırabilir veya kendi cihazına PDF olarak kaydedebilir.
- Sonuç yanıtları `Cache-Control: no-store` ile döner.
- Operasyonel loglar form yanıtlarını veya değerlendirme içeriğini kaydetmez.

Bu kural değiştirilmek istenirse kalıcı veri modeli, saklama süresi, silme politikası ve gizlilik etkisi ayrıca ürün kararı olarak değerlendirilmelidir.

## Kullanım onayı

Değerlendirme tamamlanmadan önce kullanıcı, aracı kendi kurumu, sistemleri veya değerlendirme yapmaya yetkili olduğu bir ortam için kullandığını onaylamalıdır.

Bu kontrol:

- arayüzde zorunlu checkbox olarak gösterilir,
- onay verilmeden gönderim butonunu aktif etmez,
- yalnız frontend kontrolüne güvenmez; backend de aynı alanı doğrular.

## Güvenlik sınırları

- İlk sürümde kullanıcı hesabı ve kalıcı kişisel veri depolama yoktur.
- Form girdileri allow-list ile doğrulanır.
- Harici AI sağlayıcısı veya API anahtarı bağımlılığı yoktur.
- Web Analiz ve SEO Analiz dış hedeflere sınırlı ağ isteği gönderebilir;
  kullanıcının yetki onayı ve hedef doğrulaması zorunludur.
- Secret gerektiren konfigürasyon kullanılmaz.
- Public release öncesinde bağımlılık, secret ve lisans kontrolleri zorunludur.
