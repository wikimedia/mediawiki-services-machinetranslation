def test_home_page(client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    landing = client.get("/")
    html = landing.data.decode()

    assert "Translate" in html

    assert landing.status_code == 200
