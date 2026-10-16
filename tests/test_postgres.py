import os

import pytest
from sqlalchemy import text
from sqlalchemy.engine import make_url

from app import create_app
from app.extensions import db


@pytest.fixture
def postgres_client():
    database_url = os.getenv("TEST_DATABASE_URL")

    if not database_url:
        pytest.fail("TEST_DATABASE_URL is not configured")

    # Safety check: only use the dedicated test database
    parsed_url = make_url(database_url)

    if (
        parsed_url.get_backend_name() != "postgresql"
        or parsed_url.database != "taskflow_test"
    ):
        pytest.fail(
            "Integration tests must use PostgreSQL "
            "database 'taskflow_test'"
        )

    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": database_url
    })

    with app.app_context():
        actual_database = db.session.execute(
            text("SELECT current_database()")
        ).scalar()

        if actual_database != "taskflow_test":
            pytest.fail("Connected to an unexpected database")

        db.create_all()

        try:
            yield app.test_client()
        finally:
            db.session.remove()
            db.drop_all()

def test_postgres_create_and_read(postgres_client):
    response = postgres_client.post(
        "/api/tasks",
        json={
            "title": "PostgreSQL Integration Test",
            "description": "Testing real database storage"
        }
    )

    assert response.status_code == 201

    task_id = response.json["task"]["id"]

    response = postgres_client.get(
        f"/api/tasks/{task_id}"
    )

    assert response.status_code == 200
    assert response.json["task"]["title"] == (
        "PostgreSQL Integration Test"
    )

    # Confirm the record exists in PostgreSQL
    row = db.session.execute(
        text(
            "SELECT title, status FROM tasks "
            "WHERE id = :task_id"
        ),
        {"task_id": task_id}
    ).mappings().one()

    assert row["title"] == "PostgreSQL Integration Test"
    assert row["status"] == "pending"


def test_postgres_update_task(postgres_client):
    response = postgres_client.post(
        "/api/tasks",
        json={"title": "Original Task"}
    )

    assert response.status_code == 201
    task_id = response.json["task"]["id"]

    response = postgres_client.patch(
        f"/api/tasks/{task_id}",
        json={
            "title": "Updated Task",
            "status": "completed"
        }
    )

    assert response.status_code == 200
    assert response.json["task"]["title"] == "Updated Task"
    assert response.json["task"]["status"] == "completed"

    row = db.session.execute(
        text(
            "SELECT title, status FROM tasks "
            "WHERE id = :task_id"
        ),
        {"task_id": task_id}
    ).mappings().one()

    assert row["title"] == "Updated Task"
    assert row["status"] == "completed"


def test_postgres_delete_task(postgres_client):
    response = postgres_client.post(
        "/api/tasks",
        json={"title": "Task to Delete"}
    )

    assert response.status_code == 201
    task_id = response.json["task"]["id"]

    response = postgres_client.delete(
        f"/api/tasks/{task_id}"
    )

    assert response.status_code == 200

    response = postgres_client.get(
        f"/api/tasks/{task_id}"
    )

    assert response.status_code == 404

    remaining = db.session.execute(
        text(
            "SELECT COUNT(*) FROM tasks "
            "WHERE id = :task_id"
        ),
        {"task_id": task_id}
    ).scalar()

    assert remaining == 0

