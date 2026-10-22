from app import create_app


def _valid_submission() -> dict[str, str]:
    data = {f"SK-T{i:02d}": "evet" for i in range(1, 26)}
    data["authorization_confirmed"] = "yes"
    return data


def test_index_renders_all_questions_and_authorization_gate() -> None:
    client = create_app().test_client()
    response = client.get("/")

    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "SK-T01" in body
    assert "SK-T25" in body
    assert 'name="authorization_confirmed"' in body
    assert "Değerlendirmeyi tamamla" in body


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
    assert "İyileştirme gerektiren yanıt bulunmadı." in body


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
    assert "Kısmen" in body
    assert "Hayır" in body
    assert "İyileştirme gerektiren yanıt bulunmadı." not in body


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
