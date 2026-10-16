from flask import Blueprint, jsonify, request
from app.extensions import db
from app.models import Task

api = Blueprint("api", __name__, url_prefix="/api")


def task_to_dict(task):
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "created_at": task.created_at.isoformat(),
        "updated_at": task.updated_at.isoformat()
    }


@api.route("/tasks", methods=["GET"])
def get_tasks():
    tasks = db.session.execute(
        db.select(Task).order_by(Task.id)
    ).scalars().all()

    return jsonify({
        "tasks": [task_to_dict(task) for task in tasks]
    }), 200


@api.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "A JSON object is required"
        }), 400

    title = data.get("title")
    description = data.get("description", "")

    if not isinstance(title, str) or not title.strip():
        return jsonify({
            "error": "Task title is required"
        }), 400

    title = title.strip()

    if len(title) > 200:
        return jsonify({
            "error": "Task title must not exceed 200 characters"
        }), 400

    if description is not None and not isinstance(description, str):
        return jsonify({
            "error": "Description must be a string or null"
        }), 400

    task = Task(
        title=title,
        description=description,
        status="pending"
    )

    db.session.add(task)
    db.session.commit()

    return jsonify({
        "message": "Task created successfully",
        "task": task_to_dict(task)
    }), 201

@api.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    task = db.session.get(Task, task_id)

    if task is None:
        return jsonify({
            "error": "Task not found"
        }), 404

    return jsonify({
        "task": task_to_dict(task)
    }), 200


@api.route("/tasks/<int:task_id>", methods=["PATCH"])
def update_task(task_id):
    task = db.session.get(Task, task_id)

    if task is None:
        return jsonify({
            "error": "Task not found"
        }), 404

    data = request.get_json(silent=True)

    if not isinstance(data, dict) or not data:
        return jsonify({
            "error": "A non-empty JSON object is required"
        }), 400

    allowed_fields = {"title", "description", "status"}

    if not set(data).issubset(allowed_fields):
        return jsonify({
            "error": "Unsupported task field"
        }), 400

    if "title" in data:
        title = data["title"]

        if not isinstance(title, str) or not title.strip():
            return jsonify({
                "error": "Task title is required"
            }), 400

        if len(title.strip()) > 200:
            return jsonify({
                "error": "Title must not exceed 200 characters"
            }), 400

        task.title = title.strip()

    if "description" in data:
        description = data["description"]

        if description is not None and not isinstance(description, str):
            return jsonify({
                "error": "Description must be a string or null"
            }), 400

        task.description = description

    if "status" in data:
        if data["status"] not in ("pending", "completed"):
            return jsonify({
                "error": "Status must be pending or completed"
            }), 400

        task.status = data["status"]

    db.session.commit()

    return jsonify({
        "message": "Task updated successfully",
        "task": task_to_dict(task)
    }), 200


@api.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = db.session.get(Task, task_id)

    if task is None:
        return jsonify({
            "error": "Task not found"
        }), 404

    db.session.delete(task)
    db.session.commit()

    return jsonify({
        "message": "Task deleted successfully"
    }), 200
