from app import create_app


def test_index_renders_all_questions() -> None:
    client = create_app().test_client()
    response = client.get("/")
    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "SK-T01" in body
    assert "SK-T25" in body


def test_result_rejects_incomplete_submission() -> None:
    client = create_app().test_client()
    response = client.post("/sonuc", data={"SK-T01": "evet"})
    assert response.status_code == 400


def test_result_renders_valid_submission() -> None:
    client = create_app().test_client()
    data = {f"SK-T{i:02d}": "evet" for i in range(1, 26)}
    response = client.post("/sonuc", data=data)
    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "%100.00" in body
    assert "Temel güvenlik kontrollerinde olumlu görünüm" in body
    assert "İyileştirme gerektiren yanıt bulunmadı." in body


def test_result_lists_partial_and_negative_findings() -> None:
    client = create_app().test_client()
    data = {f"SK-T{i:02d}": "evet" for i in range(1, 26)}
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
