# -*- coding: utf-8 -*-
"""
Fixtures for tests
"""
from pathlib import Path
from typing import Iterable

import pytest
from flask import Flask
from flask.testing import FlaskCliRunner, FlaskClient

from flaskr import create_app
from flaskr.db import execute_sql_script, init_db


@pytest.fixture
def app(tmp_path: Path) -> Iterable[Flask]:
    """
    Initialize app with test config, initialize DB, set up data fixtures, and yield initialized app.

    Returns:
        initialized app, ready for use
    """
    app = create_app(
        {
            "TESTING": True,
            "DATABASE": tmp_path / "test_db.sqlite",
        }
    )

    with app.app_context():
        init_db()

        path_to_file = Path(__file__).parent / "data.sql"

        execute_sql_script(path_to_file)

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
