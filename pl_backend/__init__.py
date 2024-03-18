import os
from flask import Flask
from flask_restful import Api
from .resources.user import UserResource
from .models import db
from .models.lifts import (
    Squat,
    Bench,
    Deadlift,
)
from .models.user import User



DB_NAME = os.getenv("POSTGRES_DB")
DB_USERNAME = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("POSTGRES_HOST")


def create_app() -> Flask:
    # Initialize flask API
    app = Flask(__name__)
    api = Api(app)

    app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
    db.init_app(app)

    # Create DB tables if not exist
    with app.app_context():
        db.create_all()

    api.add_resource(UserResource, "/user")

    return app
