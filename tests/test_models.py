from app import create_app
from app.extensions import db
from app.models import Task


def test_task_creation():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })

    with app.app_context():
        db.create_all()

        task = Task(
            title="Complete SWE40006 project",
            description="Implement the DevOps pipeline"
        )

        db.session.add(task)
        db.session.commit()

        task_id = task.id
        db.session.expunge_all()

        saved_task = db.session.get(Task, task_id)

        assert saved_task is not None
        assert saved_task.title == "Complete SWE40006 project"
        assert saved_task.status == "pending"
        assert saved_task.id is not None

        db.session.remove()
        db.drop_all()
