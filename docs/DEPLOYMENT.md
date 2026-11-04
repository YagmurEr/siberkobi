# SiberKOBİ Dağıtım ve Operasyon Rehberi

Bu rehber, Docker Compose ile çalışan SiberKOBİ için operatör sorumluluklarını
açıklar. Uygulama kalıcı kullanıcı verisi veya veritabanı tutmaz; yine de
container imajı, kaynak kodu ve erişim katmanı işletmeci tarafından korunur.

## Desteklenen çalışma modeli

Docker Compose, uygulamayı varsayılan olarak `8000` portunda başlatır:

```bash
docker compose up --build
```

Yerel kullanımda uygulamayı `http://localhost:8000` adresinden açın ve sağlık
kontrolünü doğrulayın:

```bash
curl --fail http://localhost:8000/health
```

`compose.yaml` içindeki varsayılan port eşlemesi tüm ağ arayüzlerinde erişim
sağlayabilir. İnternete açık bir sunucuda uygulamayı doğrudan `8000` portundan
yayınlamayın; ağ güvenlik duvarı, TLS sonlandırması ve erişim politikasını
kurumunuzun reverse proxy katmanında yönetin.

## İnternete açık kurulum sınırı

İnternete açık kullanımda aşağıdaki kontroller işletmecinin sorumluluğundadır:

- Uygulamaya yalnızca HTTPS üzerinden erişim sağlamak ve geçerli sertifika
  kullanmak.
- Uygulama container'ını bir reverse proxy arkasına almak; doğrudan `8000`
  erişimini güvenlik duvarı ile sınırlandırmak.
- İşletim sistemi, Docker Engine ve reverse proxy güncellemelerini düzenli
  uygulamak.
- Yalnız yetkili yöneticilere sunucu ve Docker erişimi vermek.
- Web Analiz ve SEO Analiz modüllerinin dış hedeflere ağ isteği gönderdiğini
  dikkate alarak egress/firewall politikasını belirlemek. Kapsam için
  [SCAN_SCOPE.md](SCAN_SCOPE.md) dosyasına bakın.

Bu depoda reverse proxy veya sertifika yönetimi yapılandırması bulunmaz. Kurum,
kendi alan adı, TLS sertifikası ve ağ topolojisine uygun yapılandırmayı
uygulamalıdır.

## Güncelleme

Güncellemeden önce mevcut commit'i kaydedin; sorun çıkarsa bu commit'e geri
dönebilirsiniz:

```bash
git log -1 --oneline
git pull --ff-only
docker compose down
docker compose up --build -d
curl --fail http://localhost:8000/health
docker compose ps
```

`git pull --ff-only`, beklenmeyen bir merge commit oluşturmadan yalnızca hızlı
ileri güncellemeleri kabul eder. Yerelde commit yapılmış veya değiştirilmiş
dosyalar varsa önce bunları gözden geçirin.

## Geri dönüş

Yeni sürüm sağlık kontrolünü geçmezse, kaydettiğiniz önceki commit'e dönün ve
imajı yeniden oluşturun:

```bash
git checkout <önceki-commit>
docker compose down
docker compose up --build -d
curl --fail http://localhost:8000/health
```

Geri dönüşten sonra sorunun commit kimliğini, container loglarını ve sağlık
kontrolü sonucunu kaydedin. Değerlendirme geçmişi, veritabanı ve sunucu tarafı
rapor arşivi olmadığı için uygulama verisi için restore işlemi gerekmez.

## İzleme ve hata ayıklama

```bash
docker compose ps
docker compose logs --tail=200
docker compose logs -f
```

Uygulama istek yöntemi, yolu, HTTP durum kodu ve süre bilgisini kaydeder.
Değerlendirme yanıtları ve rapor içeriği operasyonel loglara yazılmamalıdır.

## Kullanımdan kaldırma

Önce container'ı durdurun:

```bash
docker compose down
```

Kaynak klasörünü ve imajları silmeden önce başka uygulamaların bu kaynakları
kullanmadığını doğrulayın. Bu işlem uygulamanın kalıcı kullanıcı verisini
silmez; çünkü SiberKOBİ bu tür veri saklamaz.
