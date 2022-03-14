# -*- coding: utf-8 -*-
"""
Fixtures for tests
"""
from typing import Iterable

import pytest
from _pytest.tmpdir import TempPathFactory
from flask import Flask
from flask.testing import FlaskCliRunner, FlaskClient
from flask_sqlalchemy import SQLAlchemy
from werkzeug import Response

from flaskr import create_app
from flaskr.models import db as _db


@pytest.fixture
def app(tmp_path_factory: TempPathFactory) -> Iterable[Flask]:
    """
    Initialize app with test config, initialize DB, set up data fixtures, and yield initialized app.

    Returns:
        initialized app, ready for use
    """
    db_path = tmp_path_factory.mktemp("test_db") / "test_db.sqlite"

    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": f"sqlite:////{db_path}",
        }
    )

    with app.app_context():
        yield app


@pytest.fixture
def db(app: Flask) -> Iterable[SQLAlchemy]:
    """
    Sets up a database and yield it ready for use. Ideally we'd set up a DB once per test session
    and just roll back the transactions between tests, but can't figure out the transaction rollbacks
    yet...

    Args:
        app: initialized app

    Returns:
        db ready for use
    """
    _db.init_app(app)

    _db.create_all()

    yield _db

    _db.session.close()

    _db.drop_all()


@pytest.fixture
def client(app: Flask) -> Iterable[FlaskClient]:
    """
    Returns a test client to interact with the initialized flask app.

    Args:
        app: initialized app

    Returns:
        Client that can be used to interact with initialized app.
    """
    with app.test_client() as client:
        yield client


@pytest.fixture
def runner(app: Flask) -> FlaskCliRunner:
    """
    Returns a CLI client that can run click commands.

    Args:
        app: initialized app

    Returns:
        Runner that can utilize click commands.
    """
    return app.test_cli_runner()


class AuthActions:
    """
    Contains auth actions to perform as a user.
    """

    def __init__(self, client: FlaskClient) -> None:
        self._client = client

    def login(self, username: str, password: str) -> Response:
        """
        Attempts to log user in using the provided credentials.

        Args:
            username: username to log in as
            password: password for username

        Returns:
            Response from app's login endpoint.
        """
        return self._client.post(
            "/auth/login", data={"username": username, "password": password}
        )

    def logout(self) -> Response:
        """
        Attempts to log the user out of the application.

        Returns:
            Response from the app's logout endpoint.
        """
        return self._client.get("/auth/logout")


@pytest.fixture
def auth(client: FlaskClient) -> AuthActions:
    """
    Initializes class to ease auth interactions and returns it.

    Args:
        client: Flask client to interact with the app

    Returns:
        Initialized auth class to perform user auth actions.
    """
    return AuthActions(client)
