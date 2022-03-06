# -*- coding: utf-8 -*-
"""
Fixtures for tests
"""
import os
import tempfile
from pathlib import Path
from typing import Iterable

import pytest
from flask import Flask
from flask.testing import FlaskCliRunner, FlaskClient

from flaskr import create_app
from flaskr.db import execute_sql_script, init_db


@pytest.fixture
def app() -> Iterable[Flask]:
    """
    Initialize temp file for database and set up the app. Handle
    Returns:

    """
    db_fd, db_path = tempfile.mkstemp()

    app = create_app(
        {
            "TESTING": True,
            "DATABASE": db_path,
        }
    )

    with app.app_context():
        init_db()

        path_to_file = Path(__file__).parent / "data.sql"

        execute_sql_script(path_to_file)

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    return app.test_client()


@pytest.fixture
def runner(app: Flask) -> FlaskCliRunner:
    return app.test_cli_runner()
