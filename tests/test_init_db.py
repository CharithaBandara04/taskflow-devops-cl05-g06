import pytest
from sqlalchemy import inspect

from app import create_app
from app.extensions import db
from app.models import Task


@pytest.fixture
def app(tmp_path):
    """Create an isolated empty database for each test."""
    database_path = (tmp_path / "init_test.db").as_posix()

    return create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{database_path}",
    })


def test_init_db_creates_tables(app):
    """Initialization should create the missing tasks table."""

    with app.app_context():
        assert "tasks" not in inspect(db.engine).get_table_names()

    runner = app.test_cli_runner()
    result = runner.invoke(args=["init-db"])

    assert result.exit_code == 0, result.output
    assert "initialized successfully" in result.output

    with app.app_context():
        assert "tasks" in inspect(db.engine).get_table_names()


def test_init_db_preserves_existing_tasks(app):
    """Running initialization twice must preserve existing data."""

    runner = app.test_cli_runner()

    first_result = runner.invoke(args=["init-db"])
    assert first_result.exit_code == 0, first_result.output

    with app.app_context():
        task = Task(
            title="Important existing task",
            description="This task must not be deleted",
        )

        db.session.add(task)
        db.session.commit()
        task_id = task.id

    second_result = runner.invoke(args=["init-db"])

    assert second_result.exit_code == 0, second_result.output

    with app.app_context():
        saved_task = db.session.get(Task, task_id)

        assert saved_task is not None
        assert saved_task.title == "Important existing task"
        assert saved_task.description == "This task must not be deleted"
        assert saved_task.status == "pending"