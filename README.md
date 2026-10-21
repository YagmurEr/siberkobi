# SiberKOBİ

SiberKOBİ, KOBİ'lerin temel siber güvenlik kontrollerini kendi kendilerine değerlendirebilmesi için geliştirilen ücretsiz ve açık kaynak bir öz değerlendirme aracıdır.

## Proje hedefi

- 25 teknik soru (SK-T01–SK-T25)
- Yanıt seçenekleri: Evet / Kısmen / Hayır
- Deterministik değerlendirme
- HTML sonuç ve öneri ekranı
- Kullanıcı hesabı ve veritabanı gerektirmeyen ilk sürüm
- Docker ile kolay kurulum
- Modüler Flask mimarisi

## Mimari ilkeler

- Eclipta Suite kaynak kodu kullanılmaz veya kopyalanmaz.
- Sorular ve değerlendirme kuralları uygulama kodundan ayrılır.
- İlk sürümde AI/API anahtarı zorunlu değildir.
- Güvenli varsayılanlar, test edilebilirlik ve anlamlı loglama temel gereksinimdir.
- Public yayına geçmeden önce güvenlik ve hassas veri kontrolü yapılır.

## Planlanan yapı

```text
app/
  assessment/
  evaluation/
  reporting/
  config/
  templates/
  static/
tests/
docs/
.github/workflows/
```

## Durum

İlk geliştirme iskeleti hazırlanıyor. 25 sorunun ve değerlendirme kurallarının doğrulanması tamamlanmadan soru içeriği sabitlenmeyecektir.

## Lisans

Lisans kararı public release öncesinde kesinleştirilecektir.
