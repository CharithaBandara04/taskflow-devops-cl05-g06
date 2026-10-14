# TaskFlow REST API Documentation

## Overview

TaskFlow provides a REST API built using Python Flask,
Flask-SQLAlchemy and PostgreSQL.

Local development base URL:
http://127.0.0.1:5000/api

Task API requests and responses use JSON

## Task Data Structure

{
  "id": 1,
  "title": "Complete SWE40006 project",
  "description": "Implement the DevOps pipeline",
  "status": "pending",
  "created_at": "2026-10-14T02:30:50+00:00",
  "updated_at": "2026-10-14T02:30:50+00:00"
}

Supported status values:
- pending
- completed

## API Endpoints

### GET /api/tasks
Retrieve all tasks.

Success: HTTP 200

Response:
{
  "tasks": []
}

The tasks array contains the saved task objects.

### GET /api/tasks/{id}
Retrieve a specific task.

Success: HTTP 200
Not found: HTTP 404

Response:
{
  "task": {
    "id": 1,
    "title": "Example task",
    "description": "Task description",
    "status": "pending",
    "created_at": "...",
    "updated_at": "..."
  }
}

### POST /api/tasks
Create a task.

Required: title
Optional: description

Request:
{
  "title": "New Task",
  "description": "Task details"
}

Success: HTTP 201

The response includes a success message and
the newly created task object.

New tasks are assigned the pending status.

### PATCH /api/tasks/{id}
Update an existing task.

Supported fields:
- title
- description
- status

Request:
{
  "status": "completed"
}

Success: HTTP 200
Invalid request: HTTP 400
Not found: HTTP 404

The response includes the updated task object.

### DELETE /api/tasks/{id}
Delete an existing task.

Success: HTTP 200
Not found: HTTP 404

Response:
{
  "message": "Task deleted successfully"
}

## Validation

- Title is required when creating a task.
- Title must not be empty or exceed 200 characters.
- Description must be a string or null.
- Status must be pending or completed.
- Unsupported update fields are rejected.
- Missing tasks return HTTP 404.

## Testing

Run automated tests:

python -m pytest -v

The test suite currently includes:
- 9 API tests
- 2 application tests
- 1 database model test
- 3 PostgreSQL integration tests

PostgreSQL integration tests require TEST_DATABASE_URL
pointing to the dedicated taskflow_test database.

## Team Integration

Frontend:
Use these API endpoints to create, display,
edit, complete and delete tasks.

DevOps:
Configure DATABASE_URL for PostgreSQL connectivity.
The PostgreSQL connection must be available before
database-dependent application operations.

Database schema initialization currently uses
SQLAlchemy create_all() during development.
Production migrations and initialization are
planned separately.
