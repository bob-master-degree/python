def test_root_redirect(client):
    response = client.get("/")
    assert response.status_code == 303
    assert "/analyze" in response.location

def test_settings_page(client):
    response = client.get("/settings")
    assert response.status_code == 200
    assert "Настройки" in response.data.decode("utf-8")

def test_settings_submit_and_delete(client):
    response = client.post("/settings", data={"api_key": "fakekey"})
    assert response.status_code == 303

    with client.session_transaction() as sess:
        assert sess.get("openai_api_key") == "fakekey"

    response = client.post("/settings/delete")
    assert response.status_code == 303
    with client.session_transaction() as sess:
        assert "openai_api_key" not in sess

def test_analyze_requires_api_key(client):
    response = client.post("/analyze", data={"text": "тест"})
    assert response.status_code == 400
    assert "Укажите OpenAI API Key" in response.get_data(as_text=True)
