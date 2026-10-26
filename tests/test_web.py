from app import create_app


def _valid_submission() -> dict[str, str]:
    data = {f"SK-T{i:02d}": "evet" for i in range(1, 26)}
    data["authorization_confirmed"] = "yes"
    return data


def test_index_renders_product_landing_page() -> None:
    client = create_app().test_client()
    response = client.get("/")

    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "Siber Güvenlik Anketi" in body
    assert "Web Analiz" in body
    assert "SEO Analiz" in body
    assert "SK-T01" not in body


def test_assessment_renders_all_questions_and_authorization_gate() -> None:
    client = create_app().test_client()
    response = client.get("/assessment")

    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "SK-T01" in body
    assert "SK-T25" in body
    assert 'name="authorization_confirmed"' in body
    assert "Değerlendirmeyi tamamla" in body


def test_module_entry_pages_render() -> None:
    client = create_app().test_client()

    openscan = client.get("/openscan")
    seo = client.get("/web-seo-audit")

    assert openscan.status_code == 200
    openscan_body = openscan.get_data(as_text=True)
    assert "Web Analiz" in openscan_body
    assert 'name="target"' in openscan_body
    assert seo.status_code == 200
    seo_body = seo.get_data(as_text=True)
    assert "SEO Analiz" in seo_body
    assert 'name="target"' in seo_body


def test_result_rejects_missing_authorization() -> None:
    client = create_app().test_client()
    data = {f"SK-T{i:02d}": "evet" for i in range(1, 26)}

    response = client.post("/sonuc", data=data)

    assert response.status_code == 400
    assert "onaylamanız gerekir" in response.get_data(as_text=True)


def test_result_rejects_incomplete_submission() -> None:
    client = create_app().test_client()
    response = client.post(
        "/sonuc",
        data={"SK-T01": "evet", "authorization_confirmed": "yes"},
    )
    assert response.status_code == 400


def test_result_renders_valid_submission() -> None:
    client = create_app().test_client()
    response = client.post("/sonuc", data=_valid_submission())

    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "%100.00" in body
    assert "Temel güvenlik kontrollerinde olumlu görünüm" in body
    assert "Bu alanda öncelikli iyileştirme oluşmadı." in body


def test_result_lists_partial_and_negative_findings() -> None:
    client = create_app().test_client()
    data = _valid_submission()
    data["SK-T02"] = "kismen"
    data["SK-T03"] = "hayir"

    response = client.post("/sonuc", data=data)

    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "SK-T02" in body
    assert "SK-T03" in body
    assert "Varlık envanterini düzenli doğrulayın" in body
    assert "Zafiyet ve yama sürecini birlikte yönetin" in body


def test_assessment_is_stateless_and_sets_no_session_cookie() -> None:
    app = create_app()
    client = app.test_client()

    response = client.post("/sonuc", data=_valid_submission())

    assert response.status_code == 200
    assert "Set-Cookie" not in response.headers
    assert not client.get_cookie("session")


def test_result_response_is_not_cached() -> None:
    client = create_app().test_client()

    response = client.post("/sonuc", data=_valid_submission())

    assert response.status_code == 200
    assert response.headers["Cache-Control"] == "no-store"


def test_identity_answers_are_grouped_into_one_access_review_action() -> None:
    client = create_app().test_client()
    data = _valid_submission()
    for qid in ("SK-T06", "SK-T07", "SK-T08", "SK-T09"):
        data[qid] = "kismen"

    response = client.post("/sonuc", data=data)

    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert body.count("Kullanıcı ve ayrıcalıklı hesapları üç ayda bir gözden geçirin") == 1
    assert "SK-T06 · SK-T07 · SK-T08 · SK-T09" in body


def test_legal_notice_page_and_home_link() -> None:
    client = create_app().test_client()

    legal = client.get("/yasal-uyari")
    assert legal.status_code == 200
    body = legal.get_data(as_text=True)
    assert "Bilgilendirme ve Sorumluluk Sınırı" in body
    assert "Eclipta'nın yürürlükteki mevzuat uyarınca" in body

    home = client.get("/")
    assert home.status_code == 200
    home_body = home.get_data(as_text=True)
    assert "Bilgilendirme Notu" in home_body
    assert "Devamı için Yasal Uyarı" in home_body
    assert 'href="/yasal-uyari"' in home_body
