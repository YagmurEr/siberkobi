from __future__ import annotations

ASSESSMENT_ACTION_RULES = [
    {
        "category": "A",
        "id": "A-01",
        "questions": ["SK-T01", "SK-T02"],
        "title": "Varlık envanterini düzenli doğrulayın",
        "action": (
            "İnternete açık varlıklar ile ağınıza bağlı cihazları tek bir envanterde tutun. "
            "En az üç ayda bir kullanılmayan, unutulmuş veya yetkisiz sistemleri gözden geçirip "
            "sonucu kayıt altına alın."
        ),
    },
    {
        "category": "A",
        "id": "A-02",
        "questions": ["SK-T03", "SK-T04"],
        "title": "Zafiyet ve yama sürecini birlikte yönetin",
        "action": (
            "Kritik güvenlik açıklarını aktif istismar ve iş etkisine göre önceliklendirin. "
            "Kritik yamaların gerçekten uygulandığını düzenli olarak doğrulayın ve kapanış kaydı tutun."
        ),
    },
    {
        "category": "B",
        "id": "B-01",
        "questions": ["SK-T05"],
        "title": "Kritik hesaplarda MFA kapsamını tamamlayın",
        "action": (
            "Yönetici hesapları, uzaktan erişim ve kritik uygulamalarda MFA kullanın. "
            "MFA istisnalarını sınırlı tutun ve periyodik olarak gözden geçirin."
        ),
    },
    {
        "category": "B",
        "id": "B-02",
        "questions": ["SK-T06", "SK-T07", "SK-T08", "SK-T09"],
        "title": "Kullanıcı ve ayrıcalıklı hesapları üç ayda bir gözden geçirin",
        "action": (
            "Kullanıcı hesaplarını, ayrıcalıklı/yönetici erişimlerini, işten ayrılan veya görev değiştiren "
            "kullanıcıları ve Local Administrator yetkilerini en az üç ayda bir kontrol edin. "
            "Gereksiz erişimleri kaldırın ve yapılan gözden geçirmeyi kayıt altına alın."
        ),
    },
    {
        "category": "C",
        "id": "C-01",
        "questions": ["SK-T10", "SK-T14", "SK-T15"],
        "title": "Güvenlik kayıtları ve alarm takibini merkezileştirin",
        "action": (
            "Kritik istemci, sunucu ve güvenlik ürünlerinden gelen kayıtları merkezi olarak izleyin. "
            "Üretilen alarmların gerçek olayları yakalayabildiğini düzenli testlerle doğrulayın."
        ),
    },
    {
        "category": "C",
        "id": "C-02",
        "questions": ["SK-T11", "SK-T12"],
        "title": "Ağ erişimlerini ve segmentasyonu gözden geçirin",
        "action": (
            "Firewall kurallarındaki gereksiz erişimleri kaldırın ve kritik sistemler arasında ihtiyaç kadar "
            "erişim sağlayın. Bir sistem ele geçirilse bile yatay hareketi sınırlandıracak kontroller uygulayın."
        ),
    },
    {
        "category": "C",
        "id": "C-03",
        "questions": ["SK-T13"],
        "title": "Uzaktan erişim kayıtlarını görünür hale getirin",
        "action": (
            "VPN ve uzaktan yönetim erişimlerinde kullanıcı, zaman ve kaynak bilgilerini kaydedin. "
            "Şüpheli erişimlerin incelenebileceği yeterli log saklama süresi belirleyin."
        ),
    },
    {
        "category": "C",
        "id": "C-04",
        "questions": ["SK-T16"],
        "title": "Sosyal mühendislik bildirim sürecini netleştirin",
        "action": (
            "Çalışanların şüpheli e-posta, SMS ve bağlantıları kolayca bildirebileceği bir kanal oluşturun. "
            "Bildirimleri değerlendirecek sorumluyu ve temel müdahale adımlarını belirleyin."
        ),
    },
    {
        "category": "D",
        "id": "D-01",
        "questions": ["SK-T17", "SK-T18"],
        "title": "Hassas veri erişimini ve veri çıkışını kontrol edin",
        "action": (
            "Kişisel ve kritik kurumsal verilerin nerede tutulduğunu, kimlerin eriştiğini kayıt altına alın. "
            "Yetkisiz paylaşım veya kurum dışına veri aktarımını önleyecek ya da tespit edecek kontrolleri doğrulayın."
        ),
    },
    {
        "category": "D",
        "id": "D-02",
        "questions": ["SK-T19", "SK-T20"],
        "title": "SaaS ve tedarikçi erişimlerini periyodik değerlendirin",
        "action": (
            "Kurumsal veri paylaşılan SaaS ve üçüncü tarafları listeleyin. Tedarikçi sistem erişimlerini, "
            "veri paylaşımını ve güvenlik risklerini en az yılda bir ve önemli değişikliklerde yeniden değerlendirin."
        ),
    },
    {
        "category": "D",
        "id": "D-03",
        "questions": ["SK-T21"],
        "title": "Mobil cihaz güvenlik tabanını belirleyin",
        "action": (
            "Kurumsal veriye erişen telefon ve tabletlerde ekran kilidi, güncelleme, erişim kontrolü ve "
            "kayıp cihaz müdahalesi için asgari güvenlik kuralları uygulayın."
        ),
    },
    {
        "category": "D",
        "id": "D-04",
        "questions": ["SK-T22"],
        "title": "Yapay zekâ araçlarına veri aktarım kuralları koyun",
        "action": (
            "Çalışanların yapay zekâ araçlarına hangi kurumsal veya kişisel verileri girebileceğini açıkça belirleyin. "
            "Hassas verilerin yetkisiz AI servislerine aktarılmasını sınırlandırın."
        ),
    },
    {
        "category": "E",
        "id": "E-01",
        "questions": ["SK-T23", "SK-T25"],
        "title": "Yedek geri dönüş ve hizmet kurtarma testlerini planlayın",
        "action": (
            "Kritik sistemlerin yedekten geri yüklenmesini ve iş hizmetlerinin hedeflenen süre içinde yeniden "
            "başlatılmasını en az yılda bir, kritik sistemlerde tercihen daha sık test edin; sonuçları kayıt altına alın."
        ),
    },
    {
        "category": "E",
        "id": "E-02",
        "questions": ["SK-T24"],
        "title": "Olay müdahale rollerini ve ilk adımları yazılı hale getirin",
        "action": (
            "Bir siber olayda kimin karar vereceğini, sistemlerin nasıl izole edileceğini, iletişimin nasıl yürütüleceğini "
            "ve dış destek gerektiğinde kimin aranacağını kısa bir olay müdahale planında tanımlayın."
        ),
    },
]


def build_grouped_actions(data: dict, responses: dict[str, str]) -> list[dict]:
    category_names = {item["id"]: item["name"] for item in data["categories"]}
    grouped: dict[str, list[dict]] = {item["id"]: [] for item in data["categories"]}

    for rule in ASSESSMENT_ACTION_RULES:
        triggered = [
            qid for qid in rule["questions"]
            if responses.get(qid) in {"hayir", "kismen"}
        ]
        if not triggered:
            continue

        has_no = any(responses[qid] == "hayir" for qid in triggered)
        item = {
            "id": rule["id"],
            "title": rule["title"],
            "action": rule["action"],
            "question_ids": triggered,
            "status": "Öncelikli" if has_no else "İyileştirme",
            "severity": "high" if has_no else "medium",
        }
        grouped[rule["category"]].append(item)

    return [
        {
            "category_id": category["id"],
            "category_name": category_names[category["id"]],
            "actions": grouped[category["id"]],
        }
        for category in data["categories"]
    ]
