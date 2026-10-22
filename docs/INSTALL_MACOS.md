# SiberKOBİ v0.1.0 — macOS Kurulum Rehberi

Bu rehber SiberKOBİ'yi macOS üzerinde çalıştırmak için hazırlanmıştır.

## Önerilen yöntem

macOS için önerilen kurulum yöntemi **Docker Desktop + Docker Compose** kullanmaktır.

Docker yöntemi Apple Silicon ve Intel Mac'lerde proje ortamının tutarlı çalışmasını sağlar.

---

## 1. Ön gereksinimler

Aşağıdakiler kurulu olmalıdır:

1. **Git**
2. **Docker Desktop for Mac**

Terminal açın ve kontrol edin:

```bash
git --version
docker --version
docker compose version
```

Üç komut da sürüm bilgisi döndürmelidir.

---

## 2. SiberKOBİ kaynak kodunu indirin

Terminal açın.

Örneğin çalışma klasörü oluşturun:

```bash
mkdir -p ~/Eclipta
cd ~/Eclipta
```

Projeyi GitHub'dan indirin:

```bash
git clone https://github.com/YagmurEr/siberkobi.git
cd siberkobi
```

Kontrol:

```bash
git status
git log -1
```

---

## 3. Docker ile çalıştırın

Proje klasöründe:

```bash
docker compose up --build
```

İlk çalıştırmada gerekli image'lar indirilecek ve SiberKOBİ container image'ı oluşturulacaktır.

Terminalde Gunicorn'ın port 8000 üzerinde çalıştığını gösteren loglar görülmelidir.

---

## 4. SiberKOBİ'yi açın

Tarayıcı:

```text
http://localhost:8000
```

Health kontrolü:

```text
http://localhost:8000/health
```

Beklenen cevap:

```json
{"status":"ok"}
```

---

## 5. Uygulamayı durdurun

Çalışan Docker Compose terminalinde:

```text
Control+C
```

ardından:

```bash
docker compose down
```

---

## 6. Daha sonra yeniden başlatmak

```bash
cd ~/Eclipta/siberkobi
docker compose up
```

Kod veya image değiştiyse:

```bash
docker compose up --build
```

---

## 7. SiberKOBİ'yi güncellemek

```bash
cd ~/Eclipta/siberkobi
git pull
docker compose down
docker compose up --build
```

---

## 8. Tamamen kaldırmak

```bash
cd ~/Eclipta/siberkobi
docker compose down
```

Daha sonra proje klasörünü silebilirsiniz:

```bash
cd ~/Eclipta
rm -rf siberkobi
```

> `rm -rf` komutu geri dönüşü olmayan silme işlemi yapar. Komutu çalıştırmadan önce doğru klasörde olduğunuzu kontrol edin.

SiberKOBİ kalıcı değerlendirme geçmişi tutmadığı için ayrıca kullanıcı verisi taşımaya gerek yoktur.

---

# Alternatif: Native Python ile macOS kurulumu

Docker kullanmak istemiyorsanız uygulamayı Python ile çalıştırabilirsiniz.

## 1. Python sürümünü kontrol edin

Python 3.13 veya üzeri gereklidir.

```bash
python3 --version
```

## 2. Kaynak kodu indirin

```bash
mkdir -p ~/Eclipta
cd ~/Eclipta
git clone https://github.com/YagmurEr/siberkobi.git
cd siberkobi
```

## 3. Virtual environment oluşturun

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Terminal satırının başında genellikle `(.venv)` görünür.

## 4. Uygulamayı kurun

```bash
python -m pip install --upgrade pip
pip install .
```

## 5. Yerel geliştirme sunucusuyla çalıştırın

```bash
flask --app app:create_app run --host=127.0.0.1 --port=8000
```

Tarayıcı:

```text
http://localhost:8000
```

## 6. Gunicorn ile çalıştırmak

macOS üzerinde uygulamayı Gunicorn ile de başlatabilirsiniz:

```bash
gunicorn --bind 127.0.0.1:8000 --workers 2 --threads 2 --timeout 30 "app:create_app()"
```

Health kontrolü:

```text
http://localhost:8000/health
```

---

# Apple Silicon notu

M1, M2, M3, M4 veya sonraki Apple Silicon Mac'lerde Docker Desktop'ın Apple Silicon sürümünü kullanın.

SiberKOBİ'nin Docker image'ı Python tabanlıdır ve standart Docker build akışını kullanır.

---

# Sorun giderme

## Port 8000 kullanımda

Kontrol:

```bash
lsof -i :8000
```

Native Python ile farklı port:

```bash
flask --app app:create_app run --host=127.0.0.1 --port=8080
```

## Docker durumunu kontrol etmek

```bash
docker info
```

## Container durumunu görmek

```bash
docker compose ps
```

## Container loglarını görmek

```bash
docker compose logs
```

Canlı log:

```bash
docker compose logs -f
```

---

# Güvenlik ve veri saklama

SiberKOBİ v0.1.0:

- kullanıcı hesabı oluşturmaz,
- değerlendirme geçmişi tutmaz,
- değerlendirme cevaplarını kalıcı olarak saklamaz,
- sunucu tarafında PDF/HTML rapor arşivi oluşturmaz,
- değerlendirme sonucu için session cookie oluşturmaz.

Sonuç raporunu saklamak istiyorsanız tarayıcı üzerinden **Yazdır / PDF olarak kaydet** seçeneğini kullanın.
