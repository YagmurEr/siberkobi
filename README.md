# SiberKOBİ

SiberKOBİ, KOBİ'lerin temel siber güvenlik kontrollerini kendi kendilerine değerlendirebilmesi için geliştirilen ücretsiz ve açık kaynak bir öz değerlendirme aracıdır.

## Özellikler

- 25 teknik soru (SK-T01–SK-T25)
- 5 güvenlik alanı
- Evet / Kısmen / Hayır yanıtları
- Yalnız uygun sorularda Uygulanamaz seçeneği
- Deterministik değerlendirme
- Alan bazlı sonuçlar
- HTML sonuç ve iyileştirme raporu
- Tarayıcı üzerinden yazdırma / PDF olarak kaydetme
- Kullanıcı hesabı ve veritabanı gerektirmeyen yapı
- Docker ile kolay kurulum
- Modüler Flask mimarisi

## Mimari ilkeler

- Eclipta Suite kaynak kodu kullanılmaz veya kopyalanmaz.
- Sorular ve değerlendirme kuralları uygulama kodundan ayrıdır.
- İlk sürümde AI veya harici API gereksinimi yoktur.
- Kalıcı kullanıcı verisi tutulmaz.
- Güvenli varsayılanlar, test edilebilirlik ve anlamlı loglama temel gereksinimdir.
- Public yayına geçmeden önce güvenlik, hassas veri ve lisans kontrolü yapılır.

## Yerel çalıştırma

Python 3.13 önerilir.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
flask --app app:create_app run
```

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
flask --app app:create_app run
```

Uygulama varsayılan olarak Flask'ın yerel geliştirme adresinde açılır.

## Docker

```bash
docker compose up --build
```

Ardından:

```text
http://localhost:8000
```

Health endpoint:

```text
http://localhost:8000/health
```

## Test ve kalite kontrolleri

```bash
ruff check .
pytest -q
bandit -r app
pip-audit
```

Bu kontroller GitHub Actions üzerinde de çalıştırılır.

## Proje yapısı

```text
app/
  assessment/
  evaluation/
  reporting/
  config/
  web/
  templates/
  static/
tests/
docs/
.github/workflows/
Dockerfile
compose.yaml
```

## Değerlendirme

Puanlama ve sonuç bantları `docs/ARCHITECTURE.md` içinde belgelenmiştir.

## Durum

İlk açık kaynak sürüm geliştirme ve güvenlik doğrulama aşamasındadır. Repository, public release kontrolü tamamlanana kadar private tutulacaktır.

## Lisans

Lisans kararı public release öncesinde kesinleştirilecektir.
