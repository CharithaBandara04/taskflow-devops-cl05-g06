# TaskFlow — PostgreSQL Database Setup Guide

## 1. Overview

TaskFlow uses PostgreSQL for persistent task storage.

The Flask backend connects to PostgreSQL through
Flask-SQLAlchemy and the Psycopg 3 driver.

This guide covers local development, testing,
and integration with the Docker environment.

## 2. Technology Stack

- Python 3.13
- Flask 3.1
- Flask-SQLAlchemy 3.1
- SQLAlchemy 2.x
- Psycopg 3
- PostgreSQL 16
- Docker

## 3. Database Architecture

Flask Application
    |
Flask-SQLAlchemy
    |
Psycopg 3
    |
PostgreSQL Database
    |
tasks table

Database connection details are configured through
environment variables rather than hardcoded credentials.

## 4. Database Configuration

Required environment variable:

DATABASE_URL

Connection string format:

postgresql+psycopg://USER:PASSWORD@HOST:PORT/DATABASE

For local development:

- Host: 127.0.0.1
- Port: 5433
- Database: taskflow
- Username: taskflow

The password must be supplied through local configuration.

Never commit actual database passwords, connection strings
containing credentials, or production secrets to GitHub.

## 5. Local PostgreSQL Development

A local PostgreSQL 16 container can be used for development.

Generate a password in PowerShell:

    $env:TASKFLOW_DEV_DB_PASSWORD = (New-Guid).Guid.Replace('-', '')

Create the container:

    docker run -d --name taskflow-pg-dev -e POSTGRES_USER=taskflow -e "POSTGRES_PASSWORD=$env:TASKFLOW_DEV_DB_PASSWORD" -e POSTGRES_DB=taskflow -p 127.0.0.1:5433:5432 -v taskflow-pg-dev-data:/var/lib/postgresql/data postgres:16

This command is for creating a new container and volume.

If the container already exists, start it instead:

    docker start taskflow-pg-dev

Existing database credentials are not changed by
restarting the container or changing POSTGRES_PASSWORD.

Verify readiness:

    docker exec taskflow-pg-dev pg_isready -U taskflow -d taskflow

Verify the database:

    docker exec taskflow-pg-dev psql -U taskflow -d taskflow -c "SELECT current_database();"

## 6. Flask Database Connection

The Flask application factory is defined in:

app/__init__.py

It loads DATABASE_URL from the environment.

For local PowerShell development, set the URL using
the existing container password:

    $env:DATABASE_URL = "postgresql+psycopg://taskflow:$($env:TASKFLOW_DEV_DB_PASSWORD)@127.0.0.1:5433/taskflow"

The password variable must contain the password used
when the PostgreSQL volume was originally initialized.

Do not print or log the complete connection URL.

## 7. Database Model

The Task model is defined in:

app/models.py

Table name: tasks

Fields:

- id: Integer primary key
- title: String(200), required
- description: Text, optional
- status: String(20), pending or completed
- created_at: DateTime
- updated_at: DateTime

The status field has a database check constraint
restricting values to pending and completed.

## 8. Initial Database Schema Creation

For the initial development environment, the tasks
table can be created with SQLAlchemy.

Run from the repository root after DATABASE_URL
has been configured:

    python -c "from app import create_app; from app.extensions import db; app=create_app(); ctx=app.app_context(); ctx.push(); db.create_all(); ctx.pop()"

Verify the table:

    docker exec taskflow-pg-dev psql -U taskflow -d taskflow -c "\dt"

Expected table:

    public.tasks

Note: create_all() creates missing tables but does
not manage schema changes to existing tables.

Production deployments will require a controlled
schema migration and initialization process.

## 9. Automated Testing

The project uses Pytest.

SQLite in-memory databases are used for isolated
unit and API tests.

PostgreSQL is used for separate integration tests.

Integration testing database:

    taskflow_test

This database must be separate from normal
application data.

Create the database if it does not already exist:

    docker exec taskflow-pg-dev psql -U taskflow -d postgres -c "CREATE DATABASE taskflow_test OWNER taskflow;"

Configure the integration test URL:

    $env:TEST_DATABASE_URL = "postgresql+psycopg://taskflow:$($env:TASKFLOW_DEV_DB_PASSWORD)@127.0.0.1:5433/taskflow_test"

Run all tests:

    python -m pytest -v

Current test suite:

- 9 API tests
- 2 health/homepage tests
- 1 database model test
- 3 PostgreSQL integration tests

Total: 15 tests.

PostgreSQL integration tests create and remove tables
inside the dedicated disposable test database.

Never point TEST_DATABASE_URL at a database containing
important or production data.

## 10. GitHub Actions Integration

GitHub Actions uses a PostgreSQL 16 service container
during automated testing.

Workflow file:

.github/workflows/ci.yml

The workflow:

1. Checks out the repository.
2. Starts the PostgreSQL service.
3. Configures Python 3.13.
4. Installs project dependencies.
5. Executes the Pytest suite.
6. Reports success or failure to GitHub.

The backend PR successfully passed all 15 tests
on a GitHub-hosted Linux runner.

The CI database is temporary and independent from
local development and production databases.

## 11. Docker Compose Integration

For Eddie's Docker Compose implementation:

- The Flask container must receive DATABASE_URL.
- PostgreSQL must be accessible on the Compose network.
- Use the PostgreSQL service name as the database host.
- Use port 5432 for container-to-container connections.
- Use a persistent Docker volume for database storage.
- Wait until PostgreSQL is ready before initializing
  the schema or running database-dependent operations.
- Keep credentials outside source control.

For example, if the PostgreSQL service is named db,
the internal connection hostname should be db,
not localhost.

The final connection settings must match the actual
Docker Compose service names and configuration.

## 12. Security Considerations

- Never commit database passwords.
- Do not expose PostgreSQL publicly without a need.
- Use environment variables or secret management.
- Use separate development, testing and production databases.
- Avoid logging complete database URLs.
- Protect production data through backups and access controls.

## 13. Responsibility and Handover

Backend implementation:
Charitha Bandara

Docker and deployment integration:
Eddie

Frontend API integration:
Hiranya

The backend implementation and database model are ready
for integration after the backend pull request receives
the required approval and is merged into develop.

## Database Initialization Command

TaskFlow provides a Flask CLI command to initialize missing
database tables in a fresh environment.

### Running initialization

Ensure PostgreSQL is running and the DATABASE_URL environment
variable points to the intended database.

From the project root, run:

    python -m flask --app run init-db

Expected output:

    TaskFlow database tables initialized successfully.

### Verify database tables

For the local development PostgreSQL container:

    docker exec taskflow-pg-dev psql -U taskflow -d taskflow -c "\dt"

The `public.tasks` table should be listed.

### Safe repeated execution

The initialization command uses SQLAlchemy's db.create_all().

- Creates missing database tables.
- Preserves existing task records.
- Can be executed repeatedly.
- Does not modify existing table structures.

### Docker and deployment integration

The deployment process should:

1. Start the PostgreSQL database.
2. Wait for PostgreSQL to become healthy.
3. Configure DATABASE_URL for the target environment.
4. Execute `python -m flask --app run init-db`.
5. Start the Flask application only after initialization succeeds.

The initialization command is not automatically executed when
the Flask development server starts.

### Database migrations

db.create_all() does not migrate existing database schemas.

Future changes to database columns or constraints should use
a migration framework such as Alembic or Flask-Migrate.

### Automated verification

Database initialization is tested in:

    tests/test_init_db.py

Run the initialization tests:

    python -m pytest tests/test_init_db.py -v

The tests verify that:
- Missing database tables are created successfully.
- Repeated initialization preserves existing task records.
