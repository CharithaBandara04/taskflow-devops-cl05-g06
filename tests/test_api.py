import pytest

from app import create_app
from app.extensions import db


@pytest.fixture
def client():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })

    with app.app_context():
        db.create_all()

        yield app.test_client()

        db.session.remove()
        db.drop_all()


def create_sample_task(client):
    response = client.post("/api/tasks", json={
        "title": "Test TaskFlow API",
        "description": "Automated testing"
    })

    assert response.status_code == 201
    return response.json["task"]["id"]


def test_create_task(client):
    response = client.post("/api/tasks", json={
        "title": "Complete SWE40006 project",
        "description": "Build the DevOps pipeline"
    })

    assert response.status_code == 201
    assert response.json["task"]["title"] == "Complete SWE40006 project"
    assert response.json["task"]["status"] == "pending"
    assert response.json["task"]["id"] is not None


def test_get_all_tasks(client):
    create_sample_task(client)

    response = client.get("/api/tasks")

    assert response.status_code == 200
    assert len(response.json["tasks"]) == 1
    assert response.json["tasks"][0]["title"] == "Test TaskFlow API"


def test_get_task_by_id(client):
    task_id = create_sample_task(client)

    response = client.get(f"/api/tasks/{task_id}")

    assert response.status_code == 200
    assert response.json["task"]["id"] == task_id


def test_update_task(client):
    task_id = create_sample_task(client)

    response = client.patch(
        f"/api/tasks/{task_id}",
        json={
            "title": "Updated task",
            "description": "Edited successfully"
        }
    )

    assert response.status_code == 200
    assert response.json["task"]["title"] == "Updated task"
    assert response.json["task"]["description"] == "Edited successfully"


def test_complete_task(client):
    task_id = create_sample_task(client)

    response = client.patch(
        f"/api/tasks/{task_id}",
        json={"status": "completed"}
    )

    assert response.status_code == 200
    assert response.json["task"]["status"] == "completed"


def test_delete_task(client):
    task_id = create_sample_task(client)

    response = client.delete(f"/api/tasks/{task_id}")

    assert response.status_code == 200

    get_response = client.get(f"/api/tasks/{task_id}")

    assert get_response.status_code == 404


def test_invalid_task_title(client):
    response = client.post("/api/tasks", json={
        "title": "",
        "description": "Invalid task"
    })

    assert response.status_code == 400
    assert "error" in response.json


def test_invalid_status(client):
    task_id = create_sample_task(client)

    response = client.patch(
        f"/api/tasks/{task_id}",
        json={"status": "unknown"}
    )

    assert response.status_code == 400


def test_missing_task(client):
    response = client.get("/api/tasks/99999")

    assert response.status_code == 404
    assert response.json["error"] == "Task not found"
