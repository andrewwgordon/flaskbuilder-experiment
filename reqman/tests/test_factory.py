from werkzeug.middleware.proxy_fix import ProxyFix


def test_app_factory_creation(app):
    assert app is not None
    assert app.name == "app"
    # Check that ProxyFix middleware is applied
    assert isinstance(app.wsgi_app, ProxyFix)


def test_custom_404_error_handler(client, db_session):
    response = client.get("/non-existent-route-for-404-test/")
    assert response.status_code == 404
    html = response.get_data(as_text=True)
    assert "page not found" in html.lower()
