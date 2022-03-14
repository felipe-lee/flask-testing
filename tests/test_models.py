# -*- coding: utf-8 -*-
"""
Tests for models 
"""
from _pytest.monkeypatch import MonkeyPatch
from faker import Faker
from flask.testing import FlaskCliRunner
from pytest_mock import MockerFixture
from werkzeug.security import check_password_hash

from flaskr.models import User


def test_hashes_password(faker: Faker) -> None:
    username = faker.user_name()
    password = faker.password()

    user = User(username=username, password=password)

    assert check_password_hash(user.password, password)


def test_can_check_password(faker: Faker) -> None:
    username = faker.user_name()
    password = faker.password()

    user = User(username=username, password=password)

    assert user.check_password(password)


def test_init_db_command(
    runner: FlaskCliRunner, monkeypatch: MonkeyPatch, mocker: MockerFixture
) -> None:
    fake_db = mocker.MagicMock()

    monkeypatch.setattr("flaskr.models.db", fake_db)

    result = runner.invoke(args=["init-db"])

    assert "Initialized" in result.output

    fake_db.create_all.assert_called_once()
