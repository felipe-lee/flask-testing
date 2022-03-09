# -*- coding: utf-8 -*-
"""
Package containing all the app code. This file will also house the app factory.
"""
import os
from typing import Any, Mapping

import dotenv
from flask import Flask


dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)  # take environment variables from .env.


def create_app(test_config: Mapping[str, Any] = None) -> Flask:
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

    db_path = os.path.join(app.instance_path, "flaskr.sqlite")

    sqlalchemy_track_modifications = (
        os.environ.get("sqlalchemy_track_modifications", "False").lower() == "true"
    )

    app.config.from_mapping(
        SECRET_KEY=os.environ["SECRET_KEY"],
        SQLALCHEMY_DATABASE_URI=f"sqlite:////{db_path}",
        SQLALCHEMY_TRACK_MODIFICATIONS=sqlalchemy_track_modifications,
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from .models import init_app

    init_app(app)

    from . import auth

    app.register_blueprint(auth.bp)

    from . import blog

    app.register_blueprint(blog.bp)
    app.add_url_rule("/", endpoint="index")

    return app
