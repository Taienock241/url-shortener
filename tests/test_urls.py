def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["message"] == "URL Shortener API is running."


def test_dashboard_is_served(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "URL Shortener" in response.text


def test_dashboard_assets_are_served(client):
    assert client.get("/assets/style.css").status_code == 200
    assert client.get("/assets/script.js").status_code == 200


def test_create_url(client):
    response = client.post(
        "/api/urls",
        json={"url": "https://example.com/articles/python"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["original_url"] == "https://example.com/articles/python"
    assert data["short_code"]
    assert data["short_url"].endswith("/" + data["short_code"])


def test_rejects_invalid_scheme(client):
    response = client.post("/api/urls", json={"url": "javascript:alert(1)"})
    assert response.status_code == 422


def test_rejects_url_without_hostname(client):
    response = client.post("/api/urls", json={"url": "https:///missing-host"})
    assert response.status_code == 422


def test_get_url_info(client):
    created = client.post("/api/urls", json={"url": "https://example.com"})
    code = created.json()["short_code"]
    response = client.get(f"/api/urls/{code}")
    assert response.status_code == 200
    assert response.json()["original_url"] == "https://example.com"
    assert response.json()["click_count"] == 0


def test_list_urls_is_newest_first_and_includes_analytics_fields(client):
    first = client.post("/api/urls", json={"url": "https://example.com/first"})
    second = client.post("/api/urls", json={"url": "https://example.com/second"})

    client.get(f"/{first.json()['short_code']}", follow_redirects=False)
    response = client.get("/api/urls")

    assert response.status_code == 200
    data = response.json()
    assert [item["original_url"] for item in data] == [
        "https://example.com/second",
        "https://example.com/first",
    ]
    assert data[1]["click_count"] == 1
    assert data[0]["short_url"].endswith("/" + second.json()["short_code"])


def test_list_urls_supports_pagination(client):
    for path in ("one", "two", "three"):
        client.post("/api/urls", json={"url": f"https://example.com/{path}"})

    response = client.get("/api/urls?limit=1&offset=1")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_unknown_code_returns_404(client):
    response = client.get("/api/urls/noSuchCode")
    assert response.status_code == 404


def test_redirects_with_302_and_increments_click_count(client):
    created = client.post("/api/urls", json={"url": "https://example.com/hello"})
    code = created.json()["short_code"]

    response = client.get(f"/{code}", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["location"] == "https://example.com/hello"

    info = client.get(f"/api/urls/{code}")
    assert info.json()["click_count"] == 1


def test_unknown_redirect_returns_404(client):
    response = client.get("/notARealCode", follow_redirects=False)
    assert response.status_code == 404
