def test_openapi_spec(client):
    spec_page = client.get("/openapi.json")
    json_data = spec_page.json()

    assert "components" in json_data

    assert spec_page.status_code == 200


def test_api_languages(client):
    spec_page = client.get("/api/languages")
    json_data = spec_page.json()

    assert "en" in json_data

    assert spec_page.status_code == 200
