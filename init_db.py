
# Initialize the TaskFlow database tables.
# Intended for initial development setup.

from run import app
from app.extensions import db

with app.app_context():
    db.create_all()
    print("TaskFlow database tables are ready.")
