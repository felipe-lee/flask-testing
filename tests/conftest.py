# -*- coding: utf-8 -*-
"""
Fixtures for tests
"""
from typing import Iterable

import pytest
from _pytest.tmpdir import TempPathFactory
from flask import Flask
from flask.testing import FlaskCliRunner, FlaskClient
from werkzeug import Response

from flaskr import create_app
from flaskr.models import db
from tests.factories import UserFactory


@pytest.fixture(scope="session")
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
        db.create_all()

        db.init_app(app)

    yield app


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """
    Returns a test client to interact with the initialized flask app.

    Args:
        app: initialized app

    Returns:
        Client that can be used to interact with initialized app.
    """
    return app.test_client()


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

    def login(self, username: str = "test", password: str = "test") -> Response:
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


@pytest.fixture(autouse=True)
def provide_session_to_factories(app: Flask) -> None:
    """
    Factories need a DB session in order to function so this adds it to them for ease of use.

    Args:
        app: initialized app
    """
    for factory in [UserFactory]:
        factory._meta.sqlalchemy_session = db.session
