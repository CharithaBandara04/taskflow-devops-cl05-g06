from app import create_app


def test_health_endpoint():
    app = create_app()
    client = app.test_client()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json["status"] == "healthy"
    assert response.json["application"] == "TaskFlow"


def test_homepage():
    app = create_app()
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert b"Welcome to TaskFlow" in response.data
