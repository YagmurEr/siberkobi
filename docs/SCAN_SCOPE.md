# Web Analiz ve SEO Analiz Kapsamı

SiberKOBİ'nin Web Analiz ve SEO Analiz modülleri, kullanıcının girdiği herkese
açık hedeflere sınırlı ağ istekleri gönderir. Bu doküman, araçların sınırlarını
ve kullanıcı/işletmeci sorumluluklarını açıklar.

## Yetki şartı

Kullanıcı, her iki araçta da hedefi değerlendirmeye yetkili olduğunu onaylamak
zorundadır. Bu onay yalnız arayüzde değil, sunucu tarafında da doğrulanır.
Yetkisiz hedeflerde araç kullanılmamalıdır.

## Web Analiz

Web Analiz:

- Alan adını DNS ile çözer ve hedef IP adreslerinin genel (public) IP olduğunu
  doğrular.
- `localhost`, private, loopback, link-local ve rezerve IP hedeflerini reddeder.
- Sınırlı bir sabit TCP port listesinde erişilebilirlik kontrolü yapar.
- HTTP/HTTPS yanıt başlıklarını, TLS sertifikası özelliklerini ve erişilebilen
  web belgesindeki sınırlı teknoloji izlerini inceler.
- Exploit, parola denemesi, içerik değiştirme veya kimlik doğrulama denemesi
  yapmaz.

Bir açık port ya da HTML/HTTP izi tek başına zafiyet veya CVE kanıtı değildir.
Rapor, dışarıdan görülen sınırlı teknik sinyallerden üretilir.

## SEO Analiz

SEO Analiz:

- Girilen URL'ye HTTP/HTTPS isteği gönderir ve yönlendirme sonrası nihai URL'yi
  inceler.
- Başlık, açıklama, başlık hiyerarşisi, canonical, viewport, robots.txt,
  sitemap, Open Graph, Twitter/X card, JSON-LD ve görsel alt metni gibi herkese
  açık işaretlemeleri okur.
- GPTBot, OAI-SearchBot, Googlebot ve Bingbot için robots.txt tabanlı erişim
  sinyallerini değerlendirir.
- Aynı host üzerindeki sınırlı sayıda iç bağlantı örneğini ve sayfa yapısını
  kontrol eder.
- Form göndermez, giriş yapmaz, içerik değiştirmez ve taranan sitenin özel
  alanlarına erişmeye çalışmaz.

## Veri saklama ve loglar

- Analiz ve değerlendirme sonuçları varsayılan olarak kalıcı biçimde saklanmaz.
- Sunucu tarafında HTML/PDF rapor arşivi tutulmaz.
- Sonuç yanıtları `Cache-Control: no-store` ile döner.
- Operasyonel loglar form yanıtlarını veya rapor içeriğini içermemelidir.

## İşletmeci notu

İnternete açık kurulumlarda egress politikası, hedeflere giden DNS, TCP ve
HTTP/HTTPS trafiğini bu kapsamla uyumlu olacak şekilde belirlemelidir. Araç,
kurumun yetkilendirme sürecinin veya profesyonel güvenlik testinin yerine
geçmez.
