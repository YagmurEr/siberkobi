# SiberKOBİ v0.1.0 — Windows Kurulum Rehberi

Bu rehber SiberKOBİ'yi Windows üzerinde çalıştırmak için hazırlanmıştır.

## Önerilen yöntem

Windows için önerilen kurulum yöntemi **Docker Desktop + Docker Compose** kullanmaktır.

Bu yöntem:

- Python ortamı hazırlamayı gerektirmez,
- uygulamayı proje ile test edilen container yapısında çalıştırır,
- Windows üzerindeki Python/Gunicorn uyumsuzluklarını önler,
- kaldırma ve yeniden kurulum işlemlerini kolaylaştırır.

---

## 1. Ön gereksinimler

Aşağıdakiler kurulu olmalıdır:

1. **Git for Windows**
2. **Docker Desktop for Windows**

Docker Desktop kurulduktan sonra uygulamayı açın ve Docker Engine'in çalıştığından emin olun.

PowerShell açın ve aşağıdaki komutları kontrol edin:

```powershell
git --version
docker --version
docker compose version
```

Üç komut da sürüm bilgisi döndürmelidir.

---

## 2. SiberKOBİ kaynak kodunu indirin

PowerShell açın.

Çalışmak istediğiniz klasöre geçin. Örneğin:

```powershell
cd C:\
mkdir Eclipta
cd Eclipta
```

Projeyi GitHub'dan indirin:

```powershell
git clone https://github.com/YagmurEr/siberkobi.git
cd siberkobi
```

Kurulu sürümü doğrulamak isterseniz:

```powershell
git status
git log -1
```

---

## 3. Uygulamayı Docker ile başlatın

Proje klasöründeyken:

```powershell
docker compose up --build
```

İlk çalıştırmada Docker gerekli image'ları indirecek ve SiberKOBİ image'ını oluşturacaktır.

Terminalde Gunicorn'ın port 8000 üzerinde çalıştığını gösteren loglar görülmelidir.

---

## 4. SiberKOBİ'yi açın

Tarayıcıdan:

```text
http://localhost:8000
```

adresini açın.

Health kontrolü için:

```text
http://localhost:8000/health
```

Beklenen cevap:

```json
{"status":"ok"}
```

Bu cevap uygulamanın çalıştığını gösterir.

---

## 5. Uygulamayı durdurun

Docker Compose terminalinde:

```text
Ctrl+C
```

ardından:

```powershell
docker compose down
```

komutunu çalıştırın.

---

## 6. Daha sonra yeniden başlatmak

Yeni bir PowerShell açın:

```powershell
cd C:\Eclipta\siberkobi
docker compose up
```

Kod veya image değiştiyse:

```powershell
docker compose up --build
```

kullanın.

---

## 7. SiberKOBİ'yi güncellemek

Proje klasöründe:

```powershell
git pull
docker compose down
docker compose up --build
```

Bu işlem GitHub'daki güncel kodu indirir ve container'ı yeniden oluşturur.

---

## 8. Tamamen kaldırmak

Önce container'ı durdurun:

```powershell
docker compose down
```

Ardından proje klasörünü Windows üzerinden silebilirsiniz.

SiberKOBİ değerlendirme geçmişi veya kullanıcı veritabanı tutmadığı için ayrıca veri taşıma işlemi gerekmez.

---

# Alternatif: Native Python ile Windows kurulumu

Docker kullanmak istemiyorsanız uygulama Python ile de çalıştırılabilir.

> Windows üzerinde Gunicorn native olarak desteklenmediği için bu yöntem yerel kullanım ve test içindir. Windows üzerinde kalıcı servis kurulumu için Docker yöntemi önerilir.

## 1. Python kontrolü

Python 3.13 veya üzeri kurulu olmalıdır.

```powershell
python --version
```

## 2. Projeyi indirin

```powershell
git clone https://github.com/YagmurEr/siberkobi.git
cd siberkobi
```

## 3. Virtual environment oluşturun

```powershell
python -m venv .venv
```

Aktifleştirin:

```powershell
.\.venv\Scripts\Activate.ps1
```

PowerShell execution policy nedeniyle hata alınırsa sistem politikanızı değiştirmeden önce kurumunuzun güvenlik politikasını kontrol edin.

## 4. SiberKOBİ'yi kurun

```powershell
python -m pip install --upgrade pip
pip install .
```

## 5. Uygulamayı çalıştırın

```powershell
flask --app app:create_app run --host=127.0.0.1 --port=8000
```

Tarayıcı:

```text
http://localhost:8000
```

---

# Sorun giderme

## Port 8000 kullanımda

Kontrol:

```powershell
netstat -ano | findstr :8000
```

Başka bir uygulama portu kullanıyorsa onu durdurun veya SiberKOBİ'yi farklı portta çalıştırın.

Native Python örneği:

```powershell
flask --app app:create_app run --host=127.0.0.1 --port=8080
```

## Docker çalışmıyor

Kontrol edin:

```powershell
docker info
```

Docker Desktop açık değilse başlatın.

## Container durumunu görmek

```powershell
docker compose ps
```

## Container loglarını görmek

```powershell
docker compose logs
```

Canlı log:

```powershell
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
