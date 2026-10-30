from app import create_app


def test_health_endpoint():
    app = create_app()
    client = app.test_client()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json["status"] == "broken" # quality gate demo, deliberate failure
    assert response.json["application"] == "TaskFlow"


def test_homepage():
    app = create_app()
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert b"<title>TaskFlow</title>" in response.data
    assert b'id="task-form"' in response.data
    assert b'id="task-list"' in response.data
    assert b"js/app.js" in response.data
