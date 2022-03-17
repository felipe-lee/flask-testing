# -*- coding: utf-8 -*-
"""
Package containing all the app code. This file will also house the app factory.
"""
import os
from typing import Any, Mapping, Optional

import dotenv
from flask import Flask

from .auth import bp as auth_bp
from .blog import bp as blog_bp
from .models import init_app


dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)  # take environment variables from .env.


def create_app(test_config: Optional[Mapping[str, Any]] = None) -> Flask:
    """
    Initializes the flask app, sets up configuration as needed, initializes the app with the DB,
    and registers the blueprints.

    Args:
        test_config (): Config that can be used when testing to override values as needed.

    Returns:
        The initialized and configured flask app.
    """
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    sqlalchemy_track_modifications = (
        os.environ.get("sqlalchemy_track_modifications", "False").lower() == "true"
    )

    sqlalchemy_database_uri = (
        f"postgresql://{os.environ['POSTGRES_USER']}:"
        f"{os.environ['POSTGRES_PASSWORD']}@{os.environ['POSTGRES_HOST']}:"
        f"{os.environ['POSTGRES_HOST_PORT']}/{os.environ['POSTGRES_DB']}"
    )

    app.config.from_mapping(
        SECRET_KEY=os.environ["SECRET_KEY"],
        SQLALCHEMY_DATABASE_URI=sqlalchemy_database_uri,
        SQLALCHEMY_TRACK_MODIFICATIONS=sqlalchemy_track_modifications,
    )

    if test_config:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    init_app(app)

    app.register_blueprint(auth_bp)

    app.register_blueprint(blog_bp)
    app.add_url_rule("/", endpoint="index")

    return app
