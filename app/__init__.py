import os
import click

from flask import Flask
from app.extensions import db


def create_app(test_config=None):
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL",
        "sqlite:///taskflow_dev.db"
    )

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    if test_config:
        app.config.update(test_config)

    db.init_app(app)

    # Register database models
    from app import models

    # Register homepage and health routes
    from app.routes import main
    app.register_blueprint(main)

    # Register Task API routes
    from app.api import api
    app.register_blueprint(api)

    @app.cli.command("init-db")
    def init_db_command():
        """Create missing TaskFlow database tables."""
        with app.app_context():
            db.create_all()

        click.echo("TaskFlow database tables initialized successfully.")


    return app
