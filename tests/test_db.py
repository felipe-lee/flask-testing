# -*- coding: utf-8 -*-
"""
Tests for DB
"""
import sqlite3

import pytest
from _pytest.monkeypatch import MonkeyPatch
from flask import Flask
from flask.testing import FlaskCliRunner
from pytest_mock import MockerFixture

from flaskr.db import get_db


def test_get_db_returns_same_connection(app: Flask) -> None:
    with app.app_context():
        db = get_db()

        assert db is get_db()


def test_db_closed_after_context_closes(app: Flask) -> None:
    with app.app_context():
        db = get_db()

        db.execute("SELECT 1")

    with pytest.raises(sqlite3.ProgrammingError, match="closed"):
        db.execute("SELECT 1")


def test_init_db_command(
    runner: FlaskCliRunner, monkeypatch: MonkeyPatch, mocker: MockerFixture
) -> None:
    fake_init_db = mocker.MagicMock()

    monkeypatch.setattr("flaskr.db.init_db", fake_init_db)

    result = runner.invoke(args=["init-db-old"])

    assert "Initialized" in result.output

    fake_init_db.assert_called_once()
