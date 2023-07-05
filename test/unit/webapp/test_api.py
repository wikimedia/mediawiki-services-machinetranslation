import json


def test_openapi_spec(client):
    spec_page = client.get("/api/spec")
    json_data = spec_page.data.decode()

    assert "components" in json.loads(json_data)

    assert spec_page.status_code == 200


def test_api_languages(client):
    spec_page = client.get("/api/languages")
    json_data = spec_page.data.decode()

    assert "en" in json.loads(json_data)

    assert spec_page.status_code == 200
